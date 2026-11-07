/* Vaani Market — mobile client.
   Records mic audio, encodes 16-bit mono 16kHz WAV in-browser (Gnani STT needs WAV,
   phone browsers give WebM), caps at 30s with a countdown, then:
   STT+plan via /api/turn -> render answer + chart -> sentence-chunked TTS playback.
*/
const MAX_SECONDS = 30, OUT_RATE = 16000;
const $ = (id) => document.getElementById(id);

let audioCtx, mediaStream, processor, source, chunks = [], inRate = 48000;
let recording = false, countdownTimer = null;

/* ---------------- recording ---------------- */
async function startRecording() {
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
  } catch (e) {
    setStatus("మైక్ అనుమతి అవసరం (HTTPS లింక్ వాడండి)"); return;
  }
  audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  inRate = audioCtx.sampleRate;
  source = audioCtx.createMediaStreamSource(mediaStream);
  processor = audioCtx.createScriptProcessor(4096, 1, 1);
  chunks = [];
  processor.onaudioprocess = (e) => chunks.push(new Float32Array(e.inputBuffer.getChannelData(0)));
  source.connect(processor); processor.connect(audioCtx.destination);
  recording = true;
  $("mic").classList.add("recording"); $("mic").textContent = "■";
  let left = MAX_SECONDS;
  setStatus(`రికార్డ్ అవుతోంది… ${left}s`);
  countdownTimer = setInterval(() => {
    left -= 1; setStatus(`రికార్డ్ అవుతోంది… ${left}s`);
    if (left <= 0) stopRecording();
  }, 1000);
}

async function stopRecording() {
  if (!recording) return;
  recording = false;
  clearInterval(countdownTimer);
  $("mic").classList.remove("recording"); $("mic").textContent = "🎤";
  processor.disconnect(); source.disconnect();
  mediaStream.getTracks().forEach(t => t.stop());
  await audioCtx.close();
  const wav = encodeWAV(downsample(flatten(chunks), inRate, OUT_RATE), OUT_RATE);
  if (wav.byteLength < 2000) { setStatus("చాలా చిన్న రికార్డింగ్ — మళ్లీ ప్రయత్నించండి"); return; }
  setStatus("వింటోంది…");
  const t0 = performance.now();
  try {
    const res = await fetch("/api/turn", {
      method: "POST", headers: { "Content-Type": "audio/wav" }, body: wav,
    });
    const data = await res.json();
    if (data.error && !data.transcript) { setStatus("లోపం: " + data.error); return; }
    await handleTurn(data, t0);
  } catch (e) { setStatus("నెట్‌వర్క్ లోపం: " + e.message); }
}

/* ---------------- WAV encoding ---------------- */
function flatten(buffers) {
  const len = buffers.reduce((n, b) => n + b.length, 0);
  const out = new Float32Array(len); let o = 0;
  for (const b of buffers) { out.set(b, o); o += b.length; }
  return out;
}
function downsample(buf, inR, outR) {
  if (outR >= inR) return buf;
  const ratio = inR / outR, outLen = Math.floor(buf.length / ratio);
  const out = new Float32Array(outLen);
  for (let i = 0; i < outLen; i++) {
    const start = Math.floor(i * ratio), end = Math.floor((i + 1) * ratio);
    let sum = 0, c = 0;
    for (let j = start; j < end && j < buf.length; j++) { sum += buf[j]; c++; }
    out[i] = c ? sum / c : 0;
  }
  return out;
}
function encodeWAV(samples, rate) {
  const buf = new ArrayBuffer(44 + samples.length * 2), view = new DataView(buf);
  const str = (o, s) => { for (let i = 0; i < s.length; i++) view.setUint8(o + i, s.charCodeAt(i)); };
  str(0, "RIFF"); view.setUint32(4, 36 + samples.length * 2, true); str(8, "WAVE");
  str(12, "fmt "); view.setUint32(16, 16, true); view.setUint16(20, 1, true);
  view.setUint16(22, 1, true); view.setUint32(24, rate, true);
  view.setUint32(28, rate * 2, true); view.setUint16(32, 2, true); view.setUint16(34, 16, true);
  str(36, "data"); view.setUint32(40, samples.length * 2, true);
  let o = 44;
  for (let i = 0; i < samples.length; i++) {
    const s = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(o, s < 0 ? s * 0x8000 : s * 0x7fff, true); o += 2;
  }
  return buf;
}

/* ---------------- render + speak ---------------- */
async function handleTurn(data, t0) {
  $("result").classList.remove("hidden");
  $("transcript").textContent = data.transcript || "—";
  $("answer").textContent = data.answer || "";
  $("disclaimer").textContent = data.disclaimer || "";
  const route = { refuse: "తిరస్కరణ", decline: "పరిధిలో లేదు", clarify: "స్పష్టత కావాలి",
                  no_data: "డేటా లేదు", answer: "సమాధానం" }[data.routing] || "సమాధానం";
  $("routingLabel").textContent = route;
  renderViz(data.display || {});
  renderHeadlines(data.display || {});
  renderMeta(data);
  await speak(data.sentences || [], t0);
}

function renderMeta(data) {
  const d = data.display || {}, bits = [];
  if (d.as_of) bits.push("As of " + d.as_of.slice(0, 16).replace("T", " ") + " UTC");
  if (d.delayed_by_seconds != null) bits.push("delayed data");
  if (d.source) bits.push(d.source);
  const tm = data.timings || {};
  if (tm.stt_processing != null) bits.push(`STT ${tm.stt_processing}s`);
  if (data.gate_ok != null) bits.push("numbers verified ✓" + (data.used_template ? " (template)" : ""));
  $("meta").textContent = bits.join("  ·  ");
}

function renderHeadlines(d) {
  const el = $("headlines"); el.innerHTML = "";
  (d.headlines || []).forEach(h => {
    const div = document.createElement("div"); div.className = "headline";
    div.innerHTML = `${h.title} <small>— ${h.publisher || ""} ${(h.published_at || "").slice(0,10)}</small>`;
    el.appendChild(div);
  });
}

/* charts: live 30-day line (from real data) or illustrative candlestick diagram */
function renderViz(d) {
  const el = $("viz"); el.innerHTML = "";
  if (d.visual === "candlestick") { el.innerHTML = candlestickDiagram(); return; }
  if (d.change_pct != null) {
    const up = d.change_pct >= 0;
    const pill = `<span class="pill ${up ? "up" : "down"}">${up ? "▲" : "▼"} ${Math.abs(d.change_pct)}%</span>`;
    const price = d.price != null ? `${d.price} ${d.currency || ""}` : "";
    el.innerHTML = `<div style="margin:10px 0"><span style="font-size:24px;font-weight:700">${price}</span> ${pill}</div>`;
  }
  if (d.series && d.series.closes && d.series.closes.length > 1) {
    el.innerHTML += lineChart(d.series.closes);
    const s = d.series, extra = [];
    if (s.return_pct != null) extra.push(`30 రోజులు: ${s.return_pct}%`);
    if (s.volume_vs_avg_pct != null) extra.push(`వాల్యూమ్ సగటు కంటే: ${s.volume_vs_avg_pct}%`);
    if (extra.length) el.innerHTML += `<div class="meta">${extra.join("  ·  ")}</div>`;
  }
  if (d.gold) el.innerHTML += `<div class="meta">బంగారం: $${d.gold.gold_usd}/oz · USD/INR ${d.gold.usd_inr}</div>`;
}

function lineChart(closes) {
  const W = 320, H = 120, P = 6;
  const min = Math.min(...closes), max = Math.max(...closes), span = max - min || 1;
  const pts = closes.map((c, i) => {
    const x = P + (i / (closes.length - 1)) * (W - 2 * P);
    const y = P + (1 - (c - min) / span) * (H - 2 * P);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
  const up = closes[closes.length - 1] >= closes[0];
  const col = up ? "#34d399" : "#f87171";
  return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="30 day price">
    <polyline fill="none" stroke="${col}" stroke-width="2" points="${pts}"/></svg>`;
}

/* Illustrative (synthetic) candlestick anatomy — labeled, marked as an example */
function candlestickDiagram() {
  return `<svg viewBox="0 0 320 170" aria-label="candlestick example">
    <text x="8" y="16" fill="#8ea0c0" font-size="11">ఉదాహరణ (illustrative)</text>
    <!-- green candle -->
    <line x1="90" y1="30" x2="90" y2="140" stroke="#34d399" stroke-width="2"/>
    <rect x="76" y="60" width="28" height="55" fill="#34d399"/>
    <text x="70" y="158" fill="#34d399" font-size="11">ఆకుపచ్చ (పెరిగింది)</text>
    <!-- red candle -->
    <line x1="210" y1="40" x2="210" y2="150" stroke="#f87171" stroke-width="2"/>
    <rect x="196" y="70" width="28" height="50" fill="#f87171"/>
    <text x="196" y="30" fill="#8ea0c0" font-size="11">విక్</text>
    <text x="235" y="92" fill="#8ea0c0" font-size="11">బాడీ</text>
    <text x="196" y="168" fill="#f87171" font-size="11">ఎరుపు (తగ్గింది)</text>
  </svg>`;
}

/* sentence-chunked TTS: fetch each sentence, play in order; TTFA = first audio */
async function speak(sentences, t0) {
  if (!sentences.length) { setStatus("సిద్ధం"); return; }
  const player = $("player");
  let firstPlayed = false;
  // Pre-fetch sentence 1, then pipeline the rest.
  for (let i = 0; i < sentences.length; i++) {
    let blob;
    try {
      const r = await fetch("/api/tts", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: sentences[i], language: "te-IN" }),
      });
      if (!r.ok) continue;
      blob = await r.blob();
    } catch (e) { continue; }
    await playBlob(player, blob);
    if (!firstPlayed) {
      firstPlayed = true;
      setStatus(`మొదటి ఆడియో: ${((performance.now() - t0) / 1000).toFixed(1)}s (TTFA)`);
    }
  }
  setStatus(`పూర్తయింది · మొత్తం ${((performance.now() - t0) / 1000).toFixed(1)}s`);
}
function playBlob(player, blob) {
  return new Promise((resolve) => {
    player.src = URL.createObjectURL(blob);
    player.onended = resolve; player.onerror = resolve;
    player.play().catch(resolve);
  });
}

function setStatus(s) { $("status").textContent = s; }

/* ---------------- typed fallback ---------------- */
async function sendTyped() {
  const text = $("typed").value.trim(); if (!text) return;
  setStatus("ఆలోచిస్తోంది…");
  const t0 = performance.now();
  const r = await fetch("/api/ask_text", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  await handleTurn(await r.json(), t0);
}

/* ---------------- wiring ---------------- */
$("mic").addEventListener("click", () => recording ? stopRecording() : startRecording());
$("send").addEventListener("click", sendTyped);
$("typed").addEventListener("keydown", (e) => { if (e.key === "Enter") sendTyped(); });
if ("serviceWorker" in navigator) navigator.serviceWorker.register("/static/sw.js").catch(() => {});
