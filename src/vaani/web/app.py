"""Vaani Market web server — stdlib only (no framework), easy to explain in an interview.

Endpoints:
  GET  /                 -> the mobile web app (static/index.html)
  GET  /static/<file>    -> static assets (JS, manifest, service worker)
  POST /api/turn         -> body = 16-bit mono WAV bytes; runs STT -> orchestrator;
                            returns {transcript, detected_language, answer, sentences,
                            display, disclaimer, routing, timings}
  POST /api/tts          -> body = JSON {text, language, voice}; returns audio/wav bytes
                            (X-Wall-Seconds header carries synthesis time)
  POST /api/ask_text     -> body = JSON {text}; same as /api/turn but skips STT (typed input)

Every speech call logs wall-clock time AND Gnani's own processing_time.
"""
from __future__ import annotations

import json
import re
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # src/ on path

from vaani import config
from vaani.agent import orchestrate
from vaani.gnani import stt, tts

STATIC = Path(__file__).resolve().parent / "static"

# Sentence split for chunked synthesis (Telugu danda + ASCII . ? !).
_SENT = re.compile(r"[^.?!।]+[.?!।]?")


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENT.findall(text or "") if s.strip()]


def _turn_from_transcript(transcript: str, timings: dict) -> dict:
    t0 = time.monotonic()
    ans = orchestrate.handle(transcript)
    timings["agent_wall"] = round(time.monotonic() - t0, 3)
    return {
        "transcript": transcript,
        "routing": ans.routing,
        "answer": ans.text,
        "sentences": split_sentences(ans.text),
        "display": ans.display,
        "disclaimer": ans.disclaimer,
        "language": ans.language,
        "gate_ok": ans.gate_ok,
        "used_template": ans.used_template,
        "timings": timings,
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quieter console
        pass

    # ---- helpers ----
    def _send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> bytes:
        n = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(n) if n else b""

    # ---- GET ----
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/":
            return self._send_file(STATIC / "index.html", "text/html; charset=utf-8")
        if path.startswith("/static/"):
            f = STATIC / path[len("/static/"):]
            if f.is_file() and STATIC in f.resolve().parents:
                return self._send_file(f, _ctype(f))
        self.send_error(404)

    def _send_file(self, f: Path, ctype: str):
        try:
            data = f.read_bytes()
        except OSError:
            return self.send_error(404)
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # ---- POST ----
    def do_POST(self):
        path = self.path.split("?", 1)[0]
        try:
            if path == "/api/turn":
                return self._api_turn()
            if path == "/api/ask_text":
                return self._api_ask_text()
            if path == "/api/tts":
                return self._api_tts()
        except (stt.STTError, tts.TTSError) as exc:
            return self._send_json({"error": str(exc)}, status=502)
        except Exception as exc:  # noqa: BLE001 - surface, don't hide
            return self._send_json({"error": f"{type(exc).__name__}: {exc}"}, status=500)
        self.send_error(404)

    def _api_turn(self):
        audio = self._read_body()
        if not audio:
            return self._send_json({"error": "empty audio"}, status=400)
        t0 = time.monotonic()
        r = stt.transcribe(audio, language_code="te-IN")
        timings = {
            "stt_wall": round(time.monotonic() - t0, 3),
            "stt_processing": r.processing_time,
            "detected_language": r.detected_language_code,
        }
        if not r.transcript.strip():
            return self._send_json({"error": "empty transcript", "timings": timings}, status=200)
        self._send_json(_turn_from_transcript(r.transcript, timings))

    def _api_ask_text(self):
        data = json.loads(self._read_body() or b"{}")
        text = (data.get("text") or "").strip()
        if not text:
            return self._send_json({"error": "no text"}, status=400)
        self._send_json(_turn_from_transcript(text, {}))

    def _api_tts(self):
        data = json.loads(self._read_body() or b"{}")
        text = (data.get("text") or "").strip()
        if not text:
            return self._send_json({"error": "no text"}, status=400)
        res = tts.synthesize(
            text, language=data.get("language", "te-IN"), voice=data.get("voice", "Kalpana")
        )
        self.send_response(200)
        self.send_header("Content-Type", "audio/wav")
        self.send_header("X-Wall-Seconds", f"{res.wall_seconds:.3f}")
        self.send_header("Content-Length", str(len(res.audio)))
        self.end_headers()
        self.wfile.write(res.audio)


def _ctype(f: Path) -> str:
    return {
        ".js": "application/javascript", ".json": "application/json",
        ".html": "text/html; charset=utf-8", ".css": "text/css",
        ".svg": "image/svg+xml",
    }.get(f.suffix, "application/octet-stream")


def main(port: int = 8000) -> None:
    if not config.have_gnani():
        print("WARNING: GNANI_API_KEY not set — STT/TTS will fail.")
    srv = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Vaani Market serving on http://localhost:{port}  (Ctrl-C to stop)")
    print("Phone access needs HTTPS — run a tunnel, e.g.:  cloudflared tunnel --url http://localhost:%d" % port)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 8000)
