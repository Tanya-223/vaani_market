"""Phase 1 probe: confirm the Gnani auth header empirically.

Logic (from docs/vaani_context.md and report 5.1):
  On the SAME request, a 401 means the key/header was rejected; a 400/422 means
  authentication succeeded and only the parameters are wrong. We send an STT
  request with NO audio_file (so params are deliberately incomplete) and compare:
    - correct header X-API-Key-ID  -> expect 422 (auth OK, missing param)
    - wrong header   x-api-key     -> expect 401 (key not seen -> missing key)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vaani import config
from vaani.http import request_with_retry


def _try(header_name: str) -> None:
    headers = {header_name: config.GNANI_API_KEY}
    # Intentionally omit audio_file; send only language_code so the request is
    # well-formed except for the missing required file.
    resp, timing = request_with_retry(
        "POST",
        config.GNANI_STT_URL,
        headers=headers,
        data={"language_code": "te-IN", "model": "prisma-v3.0"},
        timeout=30,
    )
    body = resp.text[:400].replace("\n", " ")
    print(f"  header={header_name:>14}  ->  HTTP {resp.status_code}  ({timing.wall_seconds:.2f}s)")
    print(f"      body: {body}")


def main() -> int:
    if not config.have_gnani():
        print("GNANI_API_KEY not set in .env — cannot probe. Stopping.")
        return 2
    print(f"Gnani key loaded: {config.masked(config.GNANI_API_KEY)}")
    print(f"STT endpoint: {config.GNANI_STT_URL}\n")

    print("A) correct header name:")
    _try("X-API-Key-ID")
    print("\nB) wrong header name (Platform-API style):")
    _try("x-api-key")

    print(
        "\nInterpretation: if (A) is 400/422 and (B) is 401, the correct Speech-API "
        "header is confirmed as X-API-Key-ID."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
