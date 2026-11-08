"""Tier-1 glossary — the small, static, human-reviewable corpus for beginner concepts.

English source from docs/vaani_context.md §4. Telugu AND Hindi entries are DRAFTS
(reviewed=False) until a native speaker signs off — natural spoken language that keeps
common English words (share, stock, NSE, Nifty, P/E) as people say them.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Entry:
    id: str
    term_en: str
    text_en: str
    text_te: str
    text_hi: str
    reviewed: bool = False      # Telugu/Hindi must be reviewed before public use
    visual: str | None = None

    def text(self, language: str) -> str:
        return {"te-IN": self.text_te, "hi-IN": self.text_hi}.get(language, self.text_en)


GLOSSARY: list[Entry] = [
    Entry(
        "stock_share", "stock / share",
        "A share is a small piece of ownership in a company. If you own shares, you own a "
        "tiny part of that company. The price goes up and down as buyers and sellers agree "
        "on what the company is worth.",
        "షేర్ అంటే ఒక కంపెనీలో చిన్న యాజమాన్య భాగం. మీ దగ్గర షేర్లు ఉంటే, ఆ కంపెనీలో మీకు కొద్ది భాగం సొంతం. "
        "కొనేవాళ్లు, అమ్మేవాళ్లు కంపెనీ విలువ గురించి ఒప్పుకున్నప్పుడు ధర పెరుగుతూ, తగ్గుతూ ఉంటుంది.",
        "शेयर किसी कंपनी में मालिकाना हक़ का एक छोटा हिस्सा है। अगर आपके पास शेयर हैं, तो उस कंपनी का "
        "एक छोटा हिस्सा आपका है। खरीदने और बेचने वाले कंपनी की कीमत पर सहमत होते हैं, इसलिए दाम ऊपर-नीचे होता रहता है।",
    ),
    Entry(
        "stock_market", "stock market",
        "The stock market is where buyers and sellers trade company shares. In India this "
        "happens on exchanges, mainly NSE and BSE. Trading runs from 9:15 in the morning to "
        "3:30 in the afternoon on weekdays.",
        "స్టాక్ మార్కెట్ అంటే కంపెనీల షేర్లను కొనడం, అమ్మడం జరిగే చోటు. ఇండియాలో ఇది ప్రధానంగా NSE, BSE అనే "
        "ఎక్స్ఛేంజ్‌లలో జరుగుతుంది. ట్రేడింగ్ పని రోజుల్లో ఉదయం 9:15 నుంచి మధ్యాహ్నం 3:30 వరకు జరుగుతుంది.",
        "स्टॉक मार्केट वह जगह है जहाँ कंपनियों के शेयर खरीदे और बेचे जाते हैं। भारत में यह मुख्य रूप से NSE "
        "और BSE एक्सचेंज पर होता है। ट्रेडिंग कार्यदिवसों में सुबह 9:15 से दोपहर 3:30 बजे तक चलती है।",
    ),
    Entry(
        "nse_bse", "NSE and BSE",
        "NSE is the National Stock Exchange and BSE is the Bombay Stock Exchange. They are "
        "India's two main exchanges. BSE is older, and NSE handles far more trading. Most big "
        "companies are listed on both, at almost the same price.",
        "NSE అంటే నేషనల్ స్టాక్ ఎక్స్ఛేంజ్, BSE అంటే బాంబే స్టాక్ ఎక్స్ఛేంజ్. ఇవి ఇండియాలోని రెండు ప్రధాన "
        "ఎక్స్ఛేంజ్‌లు. BSE పాతది, NSEలో ట్రేడింగ్ చాలా ఎక్కువ. చాలా పెద్ద కంపెనీలు రెండింటిలోనూ దాదాపు ఒకే ధరకు లిస్ట్ అవుతాయి.",
        "NSE यानी नेशनल स्टॉक एक्सचेंज और BSE यानी बॉम्बे स्टॉक एक्सचेंज। ये भारत के दो मुख्य एक्सचेंज हैं। "
        "BSE पुराना है, और NSE पर कहीं ज़्यादा ट्रेडिंग होती है। ज़्यादातर बड़ी कंपनियाँ दोनों पर लगभग एक ही दाम पर लिस्टेड होती हैं।",
    ),
    Entry(
        "nifty_sensex", "Nifty and Sensex",
        "Nifty 50 is an index of fifty large companies on NSE. Sensex is an index of thirty "
        "large companies on BSE. When people say the market went up, they usually mean one of "
        "these went up.",
        "నిఫ్టీ 50 అంటే NSEలోని యాభై పెద్ద కంపెనీల ఇండెక్స్. సెన్సెక్స్ అంటే BSEలోని ముప్ఫై పెద్ద కంపెనీల ఇండెక్స్. "
        "మార్కెట్ పెరిగింది అని జనం అన్నప్పుడు, సాధారణంగా వీటిలో ఒకటి పెరిగిందని అర్థం.",
        "Nifty 50, NSE की पचास बड़ी कंपनियों का इंडेक्स है। Sensex, BSE की तीस बड़ी कंपनियों का इंडेक्स है। "
        "जब लोग कहते हैं कि मार्केट ऊपर गया, तो आमतौर पर इनमें से किसी एक की बात होती है।",
    ),
    Entry(
        "candlestick", "candlestick chart",
        "A candlestick shows what a price did in one period, such as one day. The thick part is "
        "the body, between the opening and the closing price. The thin lines above and below are "
        "the wicks, showing the highest and lowest prices. Commonly a green candle means the "
        "price closed higher than it opened, and a red candle means it closed lower.",
        "క్యాండిల్‌స్టిక్ అనేది ఒక రోజు లాంటి ఒక కాలంలో ధర ఎలా కదిలిందో చూపిస్తుంది. మందపాటి భాగం బాడీ, అది ఓపెనింగ్, "
        "క్లోజింగ్ ధరల మధ్య ఉంటుంది. పైన కింద ఉండే సన్నని గీతలు విక్స్, అవి అత్యధిక, అత్యల్ప ధరలను చూపిస్తాయి. "
        "సాధారణంగా ఆకుపచ్చ క్యాండిల్ అంటే ధర ఓపెన్ కంటే ఎక్కువ క్లోజ్ అయిందని, ఎరుపు క్యాండిల్ అంటే తక్కువ క్లోజ్ అయిందని అర్థం.",
        "कैंडलस्टिक दिखाती है कि एक अवधि, जैसे एक दिन में, दाम कैसे चला। मोटा हिस्सा बॉडी है, जो ओपनिंग और "
        "क्लोजिंग दाम के बीच होता है। ऊपर-नीचे की पतली लाइनें विक हैं, जो सबसे ऊँचा और सबसे नीचा दाम दिखाती हैं। "
        "आमतौर पर हरी कैंडल मतलब दाम ओपन से ऊपर बंद हुआ, और लाल कैंडल मतलब नीचे बंद हुआ।",
        visual="candlestick",
    ),
    Entry(
        "market_cap", "market capitalisation",
        "Market cap is the total value of a company's shares. It is the share price multiplied "
        "by the number of shares. In India it is usually told in crore rupees.",
        "మార్కెట్ క్యాప్ అంటే ఒక కంపెనీ షేర్ల మొత్తం విలువ. ఇది షేర్ ధరను షేర్ల సంఖ్యతో గుణిస్తే వస్తుంది. "
        "ఇండియాలో దీన్ని సాధారణంగా కోట్ల రూపాయల్లో చెబుతారు.",
        "मार्केट कैप किसी कंपनी के सभी शेयरों की कुल कीमत है। यह शेयर के दाम को शेयरों की संख्या से गुणा "
        "करने पर मिलती है। भारत में इसे आमतौर पर करोड़ रुपये में बताया जाता है।",
    ),
    Entry(
        "pe_ratio", "P/E ratio",
        "The P/E ratio is the share price divided by the company's yearly profit per share. It "
        "shows how many rupees people pay for each rupee of profit. Compare it with similar "
        "companies, not with everything.",
        "P/E రేషియో అంటే షేర్ ధరను కంపెనీ ఏడాది లాభం (ఒక్కో షేర్‌కి) తో భాగిస్తే వచ్చేది. ప్రతి ఒక్క రూపాయి లాభానికి "
        "జనం ఎన్ని రూపాయలు చెల్లిస్తున్నారో ఇది చూపిస్తుంది. దీన్ని అన్నిటితో కాకుండా, సారూప్య కంపెనీలతో పోల్చాలి.",
        "P/E रेशियो शेयर के दाम को कंपनी के सालाना प्रति-शेयर मुनाफ़े से भाग देने पर मिलता है। यह दिखाता है कि "
        "हर एक रुपये मुनाफ़े के लिए लोग कितने रुपये देते हैं। इसकी तुलना मिलती-जुलती कंपनियों से करें, हर किसी से नहीं।",
    ),
    Entry(
        "circuit_limit", "circuit limit",
        "A circuit limit is the most a share's price can move up or down in one day. When it "
        "reaches that limit, trading in it stops moving in that direction for the day.",
        "సర్క్యూట్ లిమిట్ అంటే ఒక రోజులో షేర్ ధర పైకి లేదా కిందికి కదలగల గరిష్ఠ పరిమితి. ఆ పరిమితిని చేరుకున్నప్పుడు, "
        "ఆ రోజుకు ఆ దిశలో ట్రేడింగ్ ఆగిపోతుంది.",
        "सर्किट लिमिट वह अधिकतम सीमा है जितना किसी शेयर का दाम एक दिन में ऊपर या नीचे जा सकता है। उस सीमा "
        "पर पहुँचने पर, उस दिन उस दिशा में ट्रेडिंग रुक जाती है।",
    ),
    Entry(
        "demat_account", "demat account",
        "A demat account holds your shares in electronic form, like a bank account holds money. "
        "You also need a trading account to place orders.",
        "డీమ్యాట్ అకౌంట్ మీ షేర్లను ఎలక్ట్రానిక్ రూపంలో ఉంచుతుంది, బ్యాంక్ అకౌంట్ డబ్బును ఉంచినట్టు. ఆర్డర్లు పెట్టడానికి "
        "మీకు ట్రేడింగ్ అకౌంట్ కూడా అవసరం.",
        "डीमैट अकाउंट आपके शेयरों को इलेक्ट्रॉनिक रूप में रखता है, जैसे बैंक अकाउंट पैसे रखता है। ऑर्डर देने के "
        "लिए आपको एक ट्रेडिंग अकाउंट भी चाहिए।",
    ),
    Entry(
        "etf", "ETF",
        "An ETF is a fund that trades on the exchange like a share and follows something, such "
        "as an index or the price of gold. GoldBEES is a gold ETF.",
        "ETF అనేది షేర్ లాగా ఎక్స్ఛేంజ్‌లో ట్రేడ్ అయ్యే ఒక ఫండ్; అది ఇండెక్స్ లేదా బంగారం ధర లాంటి దేనినో అనుసరిస్తుంది. "
        "GoldBEES ఒక గోల్డ్ ETF.",
        "ETF एक फंड है जो शेयर की तरह एक्सचेंज पर ट्रेड होता है और किसी चीज़ का अनुसरण करता है, जैसे कोई "
        "इंडेक्स या सोने का दाम। GoldBEES एक गोल्ड ETF है।",
    ),
    Entry(
        "dividend", "dividend",
        "A dividend is a part of a company's profit paid to its shareholders. Companies are not "
        "required to pay it, and the amount can change every year.",
        "డివిడెండ్ అంటే కంపెనీ లాభంలో షేర్‌హోల్డర్లకు ఇచ్చే భాగం. దీన్ని ఇవ్వడం కంపెనీలకు తప్పనిసరి కాదు, మొత్తం ప్రతి ఏడాది మారవచ్చు.",
        "डिविडेंड कंपनी के मुनाफ़े का वह हिस्सा है जो शेयरधारकों को दिया जाता है। इसे देना कंपनियों के लिए "
        "ज़रूरी नहीं है, और रकम हर साल बदल सकती है।",
    ),
    Entry(
        "volume", "volume",
        "Volume is how many shares were traded in a period. Large volume means many people were "
        "trading it.",
        "వాల్యూమ్ అంటే ఒక కాలంలో ఎన్ని షేర్లు ట్రేడ్ అయ్యాయో. ఎక్కువ వాల్యూమ్ అంటే చాలా మంది దాన్ని ట్రేడ్ చేశారని అర్థం.",
        "वॉल्यूम यानी एक अवधि में कितने शेयर ट्रेड हुए। ज़्यादा वॉल्यूम मतलब बहुत लोग उसे ट्रेड कर रहे थे।",
    ),
]

BY_ID = {e.id: e for e in GLOSSARY}


def unreviewed_count() -> int:
    return sum(1 for e in GLOSSARY if not e.reviewed)
