/* UI translations + inline SVG icons. UI chrome strings live here; the glossary/refusal
   CONTENT is served by the backend per language. `reviewed` marks whether a language's
   content has been human-verified (English = source; Telugu/Hindi still drafts). */

const ICONS = {
  stock_share: '<svg viewBox="0 0 24 24" fill="none"><rect x="3" y="13" width="4" height="7" rx="1" fill="#60a5fa"/><rect x="10" y="9" width="4" height="11" rx="1" fill="#3987e5"/><rect x="17" y="5" width="4" height="15" rx="1" fill="#34d399"/></svg>',
  nse_bse: '<svg viewBox="0 0 24 24" fill="none"><path d="M3 20h8V8L7 5 3 8z" fill="#60a5fa"/><path d="M13 20h8V11l-4-2-4 2z" fill="#3987e5"/><rect x="5" y="11" width="1.5" height="1.5" fill="#0b1020"/><rect x="7.5" y="14" width="1.5" height="1.5" fill="#0b1020"/></svg>',
  candlestick: '<svg viewBox="0 0 24 24" fill="none"><line x1="7" y1="3" x2="7" y2="21" stroke="#34d399" stroke-width="1.6"/><rect x="4.5" y="8" width="5" height="8" rx="1" fill="#34d399"/><line x1="17" y1="4" x2="17" y2="20" stroke="#f0787a" stroke-width="1.6"/><rect x="14.5" y="9" width="5" height="7" rx="1" fill="#f0787a"/></svg>',
  market_cap: '<svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="8.5" fill="none" stroke="#3987e5" stroke-width="2.2"/><path d="M12 3.5 A8.5 8.5 0 0 1 20 9 L12 12 Z" fill="#60a5fa"/><text x="12" y="15.5" text-anchor="middle" font-size="9" fill="#f0efec" font-family="sans-serif">₹</text></svg>',
};

const LANGS = {
  "te-IN": {
    name: "తెలుగు", reviewed: false,
    tagline: "వాయిస్‌తో అడగండి · స్టాక్ మార్కెట్ వివరణలు",
    basics: "ప్రాథమికాలు నేర్చుకోండి", tryAsking: "ఇలా అడగండి",
    placeholder: "లేదా టైప్ చేయండి…", send: "పంపు", youAsked: "మీరు అడిగింది",
    micHint: "మాట్లాడటానికి మైక్ నొక్కండి · గరిష్ఠం 30 సెకన్లు",
    draft: "⚠ తెలుగు టెక్స్ట్ ముసాయిదా · సమీక్ష పెండింగ్",
    disclaimer: "విద్యా ప్రయోజనం కోసం మాత్రమే. ఇది పెట్టుబడి సలహా కాదు.",
    routing: { answer: "సమాధానం", refuse: "తిరస్కరణ", decline: "పరిధిలో లేదు", clarify: "స్పష్టత కావాలి", no_data: "డేటా లేదు" },
    cards: [
      { icon: "stock_share", label: "స్టాక్ అంటే?", q: "స్టాక్ అంటే ఏమిటి?" },
      { icon: "nse_bse", label: "NSE, BSE", q: "NSE, BSE మధ్య తేడా ఏమిటి?" },
      { icon: "candlestick", label: "క్యాండిల్ చార్ట్", q: "క్యాండిల్ చార్ట్ అంటే ఏమిటి?" },
      { icon: "market_cap", label: "మార్కెట్ క్యాప్", q: "మార్కెట్ క్యాప్ అంటే ఏమిటి?" },
    ],
    examples: [
      "GAIL ఈ రోజు ఎందుకు పడింది?", "HDFC బ్యాంక్ ధర ఎంత?",
      "IOC ఈ నెలలో ఎలా ఉంది?", "Nifty ఈ రోజు ఎలా ఉంది?",
    ],
    st: { rec: (s) => `రికార్డ్ అవుతోంది · ${s}s`, thinking: "ఆలోచిస్తోంది", listening: "వింటోంది",
          speaking: "మాట్లాడుతోంది", ttfa: (t) => `✓ మొదటి ఆడియో ${t}s`, ready: "సిద్ధం",
          micDenied: "మైక్ అనుమతి అవసరం (HTTPS లింక్ వాడండి)", tooShort: "చాలా చిన్న రికార్డింగ్ — మళ్లీ ప్రయత్నించండి",
          netErr: "నెట్‌వర్క్ లోపం", err: "లోపం" },
  },
  "hi-IN": {
    name: "हिन्दी", reviewed: false,
    tagline: "आवाज़ से पूछें · स्टॉक मार्केट की जानकारी",
    basics: "बेसिक्स सीखें", tryAsking: "ऐसे पूछें",
    placeholder: "या टाइप करें…", send: "भेजें", youAsked: "आपने पूछा",
    micHint: "बोलने के लिए माइक दबाएँ · अधिकतम 30 सेकंड",
    draft: "⚠ हिन्दी टेक्स्ट ड्राफ़्ट · समीक्षा बाक़ी",
    disclaimer: "सिर्फ़ शैक्षणिक जानकारी। यह निवेश सलाह नहीं है।",
    routing: { answer: "जवाब", refuse: "अस्वीकार", decline: "दायरे से बाहर", clarify: "स्पष्ट करें", no_data: "डेटा नहीं" },
    cards: [
      { icon: "stock_share", label: "स्टॉक क्या है?", q: "स्टॉक क्या है?" },
      { icon: "nse_bse", label: "NSE, BSE", q: "NSE और BSE में क्या फ़र्क़ है?" },
      { icon: "candlestick", label: "कैंडलस्टिक", q: "कैंडलस्टिक चार्ट क्या है?" },
      { icon: "market_cap", label: "मार्केट कैप", q: "मार्केट कैप क्या है?" },
    ],
    examples: [
      "GAIL आज क्यों गिरा?", "HDFC बैंक का दाम क्या है?",
      "IOC इस महीने कैसा रहा?", "Nifty आज कैसा है?",
    ],
    st: { rec: (s) => `रिकॉर्ड हो रहा है · ${s}s`, thinking: "सोच रहा है", listening: "सुन रहा है",
          speaking: "बोल रहा है", ttfa: (t) => `✓ पहला ऑडियो ${t}s`, ready: "तैयार",
          micDenied: "माइक अनुमति चाहिए (HTTPS लिंक इस्तेमाल करें)", tooShort: "रिकॉर्डिंग बहुत छोटी — फिर कोशिश करें",
          netErr: "नेटवर्क एरर", err: "एरर" },
  },
  "en-IN": {
    name: "English", reviewed: true,
    tagline: "Ask by voice · stock-market explanations",
    basics: "Learn the basics", tryAsking: "Try asking",
    placeholder: "or type…", send: "Send", youAsked: "You asked",
    micHint: "Tap the mic to speak · max 30 seconds",
    draft: "",
    disclaimer: "Educational only. Not advice.",
    routing: { answer: "Answer", refuse: "Refused", decline: "Out of scope", clarify: "Need clarity", no_data: "No data" },
    cards: [
      { icon: "stock_share", label: "What is a stock?", q: "What is a stock?" },
      { icon: "nse_bse", label: "NSE & BSE", q: "What is the difference between NSE and BSE?" },
      { icon: "candlestick", label: "Candlestick", q: "What is a candlestick chart?" },
      { icon: "market_cap", label: "Market cap", q: "What is market cap?" },
    ],
    examples: [
      "Why did GAIL move today?", "What's HDFC Bank's price?",
      "How has IOC done this month?", "How is Nifty today?",
    ],
    st: { rec: (s) => `Recording · ${s}s`, thinking: "Thinking", listening: "Listening",
          speaking: "Speaking", ttfa: (t) => `✓ first audio ${t}s`, ready: "Ready",
          micDenied: "Mic permission needed (use the HTTPS link)", tooShort: "Recording too short — try again",
          netErr: "Network error", err: "Error" },
  },
};

const LANG_ORDER = ["te-IN", "hi-IN", "en-IN"];   // Telugu default (first)
