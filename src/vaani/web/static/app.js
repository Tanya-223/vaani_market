/* Vaani Market client. Language selector drives all UI chrome + the typed-reply language;
   voice input still auto-detects (Prisma) and replies in the detected language.
   Records mic -> 16-bit mono 16kHz WAV -> /api/turn -> render + sentence-chunked TTS. */
const MAX_SECONDS = 30, OUT_RATE = 16000;
const $ = (id) => document.getElementById(id);

let LANG = localStorage.getItem("vaani_lang") || "te-IN";
if (!LANGS[LANG]) LANG = "te-IN";
let T = LANGS[LANG];

let audioCtx, mediaStream, processor, source, chunks = [], inRate = 48000;
let recording = false, busy = false, countdownTimer = null;

/* ---------------- UI render (per language) ---------------- */
function setLang(code) {
  LANG = code; T = LANGS[code]; localStorage.setItem("vaani_lang", code); renderUI();
}
function renderUI() {
  document.documentElement.lang = LANG.slice(0, 2);
  $("tagline").textContent = T.tagline;
  $("basicsLabel").textContent = T.basics;
  $("tryLabel").textContent = T.tryAsking;
  $("youAskedLabel").textContent = T.youAsked;
  $("typed").placeholder = T.placeholder;
  $("send").textContent = T.send;
  $("footnote").textContent = T.disclaimer;
  $("draftbar").textContent = T.reviewed ? "" : T.draft;
  if (!recording && !busy) setStatus(T.micHint);

  // language selector (only languages whose content exists -> all three)
  const ls = $("langsel"); ls.innerHTML = "";
  LANG_ORDER.forEach(code => {
    const b = document.createElement("button");
    b.textContent = LANGS[code].name;
    b.className = code === LANG ? "active" : "";
    b.onclick = () => setLang(code);
    ls.appendChild(b);
  });
  // learn-the-basics cards
  const cc = $("cards"); cc.innerHTML = "";
  T.cards.forEach(c => {
    const d = document.createElement("div"); d.className = "lcard";
    d.innerHTML = `${ICONS[c.icon] || ""}<span>${c.label}</span>`;
    d.onclick = () => ask(c.q);
    cc.appendChild(d);
  });
  // example chips
  const ch = $("chips"); ch.innerHTML = "";
  T.examples.forEach(q => {
    const b = document.createElement("button"); b.className = "chip"; b.textContent = q;
    b.onclick = () => ask(q); ch.appendChild(b);
  });
}

/* ---------------- recording ---------------- */
async function startRecording() {
  if (busy) return;
  try { mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true }); }
  catch (e) { setStatus(T.st.micDenied); return; }
  audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  inRate = audioCtx.sampleRate;
  source = audioCtx.createMediaStreamSource(mediaStream);
  processor = audioCtx.createScriptProcessor(4096, 1, 1);
  chunks = [];
  processor.onaudioprocess = (e) => chunks.push(new Float32Array(e.inputBuffer.getChannelData(0)));
  source.connect(processor); processor.connect(audioCtx.destination);
  recording = true;
  $("mic").classList.add("rec"); $("mic").textContent = "■"; $("wave").classList.remove("hidden");
  let left = MAX_SECONDS; setStatus(T.st.rec(left));
  countdownTimer = setInterval(() => {
    left -= 1; setStatus(T.st.rec(left)); if (left <= 0) stopRecording();
  }, 1000);
}
async function stopRecording() {
  if (!recording) return;
  recording = false; clearInterval(countdownTimer);
  $("mic").classList.remove("rec"); $("mic").textContent = "🎤"; $("wave").classList.add("hidden");
  processor.disconnect(); source.disconnect();
  mediaStream.getTracks().forEach(t => t.stop());
  await audioCtx.close();
  const wav = encodeWAV(downsample(flatten(chunks), inRate, OUT_RATE), OUT_RATE);
  if (wav.byteLength < 2000) { setStatus(T.st.tooShort); return; }
  setBusy(true); setStatus(T.st.listening, true);
  const t0 = performance.now();
  try {
    const res = await fetch("/api/turn", { method: "POST", headers: { "Content-Type": "audio/wav" }, body: wav });
    const data = await res.json();
    if (data.error && !data.transcript) { setStatus(T.st.err + ": " + data.error); setBusy(false); return; }
    await handleTurn(data, t0);
  } catch (e) { setStatus(T.st.netErr + ": " + e.message); }
  setBusy(false);
}

/* ---------------- WAV encoding ---------------- */
function flatten(bufs){const n=bufs.reduce((a,b)=>a+b.length,0);const o=new Float32Array(n);let p=0;for(const b of bufs){o.set(b,p);p+=b.length;}return o;}
function downsample(buf,inR,outR){if(outR>=inR)return buf;const r=inR/outR,L=Math.floor(buf.length/r),o=new Float32Array(L);for(let i=0;i<L;i++){const s=Math.floor(i*r),e=Math.floor((i+1)*r);let sum=0,c=0;for(let j=s;j<e&&j<buf.length;j++){sum+=buf[j];c++;}o[i]=c?sum/c:0;}return o;}
function encodeWAV(sm,rate){const b=new ArrayBuffer(44+sm.length*2),v=new DataView(b);const s=(o,t)=>{for(let i=0;i<t.length;i++)v.setUint8(o+i,t.charCodeAt(i));};s(0,"RIFF");v.setUint32(4,36+sm.length*2,true);s(8,"WAVE");s(12,"fmt ");v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);v.setUint32(24,rate,true);v.setUint32(28,rate*2,true);v.setUint16(32,2,true);v.setUint16(34,16,true);s(36,"data");v.setUint32(40,sm.length*2,true);let o=44;for(let i=0;i<sm.length;i++){const x=Math.max(-1,Math.min(1,sm[i]));v.setInt16(o,x<0?x*0x8000:x*0x7fff,true);o+=2;}return b;}

/* ---------------- render answer ---------------- */
async function handleTurn(data, t0) {
  $("result").classList.remove("hidden");
  $("transcript").textContent = data.transcript || "—";
  $("answer").textContent = data.answer || "";
  $("disclaimer").textContent = "⚠ " + (data.disclaimer || T.disclaimer);
  const b = $("routing"); b.textContent = (T.routing[data.routing] || T.routing.answer);
  b.className = "badge " + (data.routing || "answer");
  renderViz(data.display || {}); renderHeadlines(data.display || {}); renderNote(data.display || {}); renderMeta(data);
  $("result").scrollIntoView({ behavior: "smooth", block: "start" });
  await speak(data.sentences || [], t0, data.language || LANG);
}
function renderMeta(data){const d=data.display||{},b=[];if(d.as_of)b.push("As of "+d.as_of.slice(0,10));if(d.delayed_by_seconds!=null)b.push("delayed");if(data.gate_ok)b.push('<span class="ok">✓ numbers verified</span>');$("meta").innerHTML=b.join("<span style='opacity:.4'>·</span> ");}
function renderHeadlines(d){const el=$("headlines");el.innerHTML="";(d.headlines||[]).forEach(h=>{const x=document.createElement("div");x.className="headline";x.innerHTML=`${h.title} <small>— ${h.publisher||""} ${(h.published_at||"").slice(0,10)}</small>`;el.appendChild(x);});}
function renderNote(d){$("note").innerHTML=d.background?`ℹ ${d.background}`:"";$("note").className=d.background?"note":"";}

function renderViz(d){
  const el=$("viz");el.innerHTML="";
  if(d.visual==="candlestick"){el.innerHTML=candlestick();return;}
  if(d.price!=null){
    const up=(d.change_pct||0)>=0;
    const pill=d.change_pct!=null?`<span class="pill ${up?"up":"down"}">${up?"▲":"▼"} ${Math.abs(d.change_pct)}%</span>`:"";
    el.innerHTML=`<div class="statrow"><span class="price">${fmt(d.price)} <span style="font-size:15px;color:var(--muted)">${d.currency||""}</span></span>${pill}</div>`;
  }
  if(d.series&&d.series.closes&&d.series.closes.length>1){
    el.innerHTML+=`<div class="chartwrap">${lineChart(d.series.closes)}</div>`;
    const s=d.series,k=[];
    if(s.return_pct!=null)k.push(kpi(`${s.return_pct>=0?"+":""}${s.return_pct}%`,"30d"));
    if(s.high!=null)k.push(kpi(fmt(s.high),"30d high"));
    if(s.low!=null)k.push(kpi(fmt(s.low),"30d low"));
    if(s.volume_vs_avg_pct!=null)k.push(kpi(`${s.volume_vs_avg_pct>=0?"+":""}${s.volume_vs_avg_pct}%`,"vol vs avg"));
    if(k.length)el.innerHTML+=`<div class="kpis">${k.join("")}</div>`;
  }
  if(d.gold)el.innerHTML+=`<div class="kpis"><div class="kpi"><div class="v">$${fmt(d.gold.gold_usd)}</div><div class="k">gold /oz</div></div><div class="kpi"><div class="v">${fmt(d.gold.usd_inr)}</div><div class="k">USD/INR</div></div></div>`;
}
function kpi(v,k){return `<div class="kpi"><div class="v">${v}</div><div class="k">${k}</div></div>`;}
function fmt(n){return (n==null)?"":Number(n).toLocaleString("en-IN");}

function lineChart(cl){
  const W=320,H=130,PL=6,PR=46,PT=10,PB=18;
  const min=Math.min(...cl),max=Math.max(...cl),span=(max-min)||1;
  const X=i=>PL+(i/(cl.length-1))*(W-PL-PR),Y=v=>PT+(1-(v-min)/span)*(H-PT-PB);
  const pts=cl.map((c,i)=>`${X(i).toFixed(1)},${Y(c).toFixed(1)}`).join(" ");
  const grid=[max,(max+min)/2,min].map(v=>`<line x1="${PL}" y1="${Y(v).toFixed(1)}" x2="${W-PR}" y2="${Y(v).toFixed(1)}" stroke="var(--grid)" stroke-width="1"/><text x="${W-PR+4}" y="${(Y(v)+3).toFixed(1)}" fill="var(--muted)" font-size="9">${fmt(Math.round(v))}</text>`).join("");
  const last=cl[cl.length-1],lx=X(cl.length-1),ly=Y(last);
  const area=`${PL},${(H-PB).toFixed(1)} ${pts} ${(W-PR).toFixed(1)},${(H-PB).toFixed(1)}`;
  return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="30 day price"><defs><linearGradient id="g" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="var(--series)" stop-opacity=".28"/><stop offset="1" stop-color="var(--series)" stop-opacity="0"/></linearGradient></defs>${grid}<polygon points="${area}" fill="url(#g)"/><polyline points="${pts}" fill="none" stroke="var(--series)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/><circle cx="${lx.toFixed(1)}" cy="${ly.toFixed(1)}" r="3.5" fill="var(--series)"/><line x1="${PL}" y1="${(H-PB).toFixed(1)}" x2="${W-PR}" y2="${(H-PB).toFixed(1)}" stroke="var(--baseline)" stroke-width="1"/><text x="8" y="${(H-5).toFixed(1)}" fill="var(--muted)" font-size="9">30d</text></svg>`;
}
function candlestick(){
  return `<div class="chartwrap"><svg viewBox="0 0 300 192" aria-label="candlestick example">
    <text x="4" y="13" fill="var(--muted)" font-size="10.5">illustrative</text>
    <line x1="10" y1="40" x2="290" y2="40" stroke="var(--grid)" stroke-width="1"/><line x1="10" y1="96" x2="290" y2="96" stroke="var(--grid)" stroke-width="1"/><line x1="10" y1="152" x2="290" y2="152" stroke="var(--grid)" stroke-width="1"/>
    <line x1="96" y1="34" x2="96" y2="158" stroke="var(--up)" stroke-width="2.5" stroke-linecap="round"/><rect x="78" y="66" width="36" height="58" rx="4" fill="var(--up)" stroke="#0a7a0a"/>
    <line x1="208" y1="44" x2="208" y2="166" stroke="var(--down)" stroke-width="2.5" stroke-linecap="round"/><rect x="190" y="74" width="36" height="52" rx="4" fill="var(--down)" stroke="#a82e2e"/>
    <line x1="96" y1="40" x2="134" y2="40" stroke="var(--muted)" stroke-width="1" stroke-dasharray="2 2"/><text x="138" y="44" fill="var(--ink-2)" font-size="11">wick</text>
    <line x1="114" y1="95" x2="138" y2="95" stroke="var(--muted)" stroke-width="1" stroke-dasharray="2 2"/><text x="142" y="99" fill="var(--ink-2)" font-size="11">body</text>
    <text x="66" y="184" fill="#48d06f" font-size="11">up (green)</text><text x="188" y="184" fill="#f0787a" font-size="11">down (red)</text>
  </svg></div>`;
}

/* sentence-chunked TTS: fetch all in parallel, play in order (fast first-audio, no gaps) */
async function speak(sentences, t0, language){
  if(!sentences.length){setStatus(T.st.ready);return;}
  setStatus(T.st.speaking, true);
  const player=$("player"),card=$("answerCard");card.classList.add("speaking");
  const jobs=sentences.map(s=>fetch("/api/tts",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text:s,language:language||"te-IN"})}).then(r=>r.ok?r.blob():null).catch(()=>null));
  let ttfa=null;
  for(const job of jobs){const blob=await job;if(!blob)continue;await playBlob(player,blob);if(ttfa===null){ttfa=(performance.now()-t0)/1000;setStatus(T.st.ttfa(ttfa.toFixed(1)));}}
  card.classList.remove("speaking");
  setStatus(ttfa!==null?T.st.ttfa(ttfa.toFixed(1)):T.st.ready);
}
function playBlob(p,blob){return new Promise(res=>{p.src=URL.createObjectURL(blob);p.onended=res;p.onerror=res;p.play().catch(res);});}

/* ---------------- typed + helpers ---------------- */
async function ask(text){
  if(busy||!text)return;
  setBusy(true);setStatus(T.st.thinking,true);
  const t0=performance.now();
  try{
    const r=await fetch("/api/ask_text",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text,language:LANG})});
    await handleTurn(await r.json(),t0);
  }catch(e){setStatus(T.st.netErr+": "+e.message);}
  setBusy(false);
}
function sendTyped(){const t=$("typed").value.trim();if(t){$("typed").value="";ask(t);}}
function setStatus(s,spin){$("status").innerHTML=spin?`${s}<span class="dots"></span>`:s;}
function setBusy(v){busy=v;$("mic").classList.toggle("busy",v);}

$("mic").addEventListener("click",()=>recording?stopRecording():startRecording());
$("send").addEventListener("click",sendTyped);
$("typed").addEventListener("keydown",e=>{if(e.key==="Enter")sendTyped();});
renderUI();
if("serviceWorker" in navigator)navigator.serviceWorker.register("/static/sw.js").catch(()=>{});
