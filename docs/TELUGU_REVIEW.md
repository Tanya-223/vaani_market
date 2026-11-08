# Telugu & Hindi review sheet

Every Telugu (te) and Hindi (hi) string the app can say/show, with its English meaning.
Write corrections under **Fix (te)** / **Fix (hi)**. Send edits to the agent; it updates the
code and flips `reviewed:false`→`true`.

---

## 1. Glossary — `retrieval/glossary.py`

### stock_share (stock / share)
- **EN:** A share is a small piece of ownership in a company. If you own shares, you own a tiny part of that company. The price goes up and down as buyers and sellers agree on what the company is worth.
- **te:** షేర్ అంటే ఒక కంపెనీలో చిన్న యాజమాన్య భాగం. మీ దగ్గర షేర్లు ఉంటే, ఆ కంపెనీలో మీకు కొద్ది భాగం సొంతం. కొనేవాళ్లు, అమ్మేవాళ్లు కంపెనీ విలువ గురించి ఒప్పుకున్నప్పుడు ధర పెరుగుతూ, తగ్గుతూ ఉంటుంది.
- **hi:** शेयर किसी कंपनी में मालिकाना हक़ का एक छोटा हिस्सा है। अगर आपके पास शेयर हैं, तो उस कंपनी का एक छोटा हिस्सा आपका है। खरीदने और बेचने वाले कंपनी की कीमत पर सहमत होते हैं, इसलिए दाम ऊपर-नीचे होता रहता है।
- **Fix (te):** _()_  · **Fix (hi):** _()_

### stock_market (stock market)
- **EN:** The stock market is where buyers and sellers trade company shares. In India this happens on exchanges, mainly NSE and BSE. Trading runs from 9:15 in the morning to 3:30 in the afternoon on weekdays.
- **te:** స్టాక్ మార్కెట్ అంటే కంపెనీల షేర్లను కొనడం, అమ్మడం జరిగే చోటు. ఇండియాలో ఇది ప్రధానంగా NSE, BSE అనే ఎక్స్ఛేంజ్‌లలో జరుగుతుంది. ట్రేడింగ్ పని రోజుల్లో ఉదయం 9:15 నుంచి మధ్యాహ్నం 3:30 వరకు జరుగుతుంది.
- **hi:** स्टॉक मार्केट वह जगह है जहाँ कंपनियों के शेयर खरीदे और बेचे जाते हैं। भारत में यह मुख्य रूप से NSE और BSE एक्सचेंज पर होता है। ट्रेडिंग कार्यदिवसों में सुबह 9:15 से दोपहर 3:30 बजे तक चलती है।
- **Fix (te):** _()_  · **Fix (hi):** _()_

### nse_bse (NSE and BSE)
- **EN:** NSE is the National Stock Exchange and BSE is the Bombay Stock Exchange. They are India's two main exchanges. BSE is older, and NSE handles far more trading. Most big companies are listed on both, at almost the same price.
- **te:** NSE అంటే నేషనల్ స్టాక్ ఎక్స్ఛేంజ్, BSE అంటే బాంబే స్టాక్ ఎక్స్ఛేంజ్. ఇవి ఇండియాలోని రెండు ప్రధాన ఎక్స్ఛేంజ్‌లు. BSE పాతది, NSEలో ట్రేడింగ్ చాలా ఎక్కువ. చాలా పెద్ద కంపెనీలు రెండింటిలోనూ దాదాపు ఒకే ధరకు లిస్ట్ అవుతాయి.
- **hi:** NSE यानी नेशनल स्टॉक एक्सचेंज और BSE यानी बॉम्बे स्टॉक एक्सचेंज। ये भारत के दो मुख्य एक्सचेंज हैं। BSE पुराना है, और NSE पर कहीं ज़्यादा ट्रेडिंग होती है। ज़्यादातर बड़ी कंपनियाँ दोनों पर लगभग एक ही दाम पर लिस्टेड होती हैं।
- **Fix (te):** _()_  · **Fix (hi):** _()_

### nifty_sensex (Nifty and Sensex)
- **EN:** Nifty 50 is an index of fifty large companies on NSE. Sensex is an index of thirty large companies on BSE. When people say the market went up, they usually mean one of these went up.
- **te:** నిఫ్టీ 50 అంటే NSEలోని యాభై పెద్ద కంపెనీల ఇండెక్స్. సెన్సెక్స్ అంటే BSEలోని ముప్ఫై పెద్ద కంపెనీల ఇండెక్స్. మార్కెట్ పెరిగింది అని జనం అన్నప్పుడు, సాధారణంగా వీటిలో ఒకటి పెరిగిందని అర్థం.
- **hi:** Nifty 50, NSE की पचास बड़ी कंपनियों का इंडेक्स है। Sensex, BSE की तीस बड़ी कंपनियों का इंडेक्स है। जब लोग कहते हैं कि मार्केट ऊपर गया, तो आमतौर पर इनमें से किसी एक की बात होती है।
- **Fix (te):** _()_  · **Fix (hi):** _()_

### candlestick (candlestick chart)
- **EN:** A candlestick shows what a price did in one period, such as one day. The thick part is the body, between the opening and the closing price. The thin lines above and below are the wicks, showing the highest and lowest prices. Commonly a green candle means the price closed higher than it opened, and a red candle means it closed lower.
- **te:** క్యాండిల్‌స్టిక్ అనేది ఒక రోజు లాంటి ఒక కాలంలో ధర ఎలా కదిలిందో చూపిస్తుంది. మందపాటి భాగం బాడీ, అది ఓపెనింగ్, క్లోజింగ్ ధరల మధ్య ఉంటుంది. పైన కింద ఉండే సన్నని గీతలు విక్స్, అవి అత్యధిక, అత్యల్ప ధరలను చూపిస్తాయి. సాధారణంగా ఆకుపచ్చ క్యాండిల్ అంటే ధర ఓపెన్ కంటే ఎక్కువ క్లోజ్ అయిందని, ఎరుపు క్యాండిల్ అంటే తక్కువ క్లోజ్ అయిందని అర్థం.
- **hi:** कैंडलस्टिक दिखाती है कि एक अवधि, जैसे एक दिन में, दाम कैसे चला। मोटा हिस्सा बॉडी है, जो ओपनिंग और क्लोजिंग दाम के बीच होता है। ऊपर-नीचे की पतली लाइनें विक हैं, जो सबसे ऊँचा और सबसे नीचा दाम दिखाती हैं। आमतौर पर हरी कैंडल मतलब दाम ओपन से ऊपर बंद हुआ, और लाल कैंडल मतलब नीचे बंद हुआ।
- **Fix (te):** _()_  · **Fix (hi):** _()_

### market_cap (market capitalisation)
- **EN:** Market cap is the total value of a company's shares. It is the share price multiplied by the number of shares. In India it is usually told in crore rupees.
- **te:** మార్కెట్ క్యాప్ అంటే ఒక కంపెనీ షేర్ల మొత్తం విలువ. ఇది షేర్ ధరను షేర్ల సంఖ్యతో గుణిస్తే వస్తుంది. ఇండియాలో దీన్ని సాధారణంగా కోట్ల రూపాయల్లో చెబుతారు.
- **hi:** मार्केट कैप किसी कंपनी के सभी शेयरों की कुल कीमत है। यह शेयर के दाम को शेयरों की संख्या से गुणा करने पर मिलती है। भारत में इसे आमतौर पर करोड़ रुपये में बताया जाता है।
- **Fix (te):** _()_  · **Fix (hi):** _()_

### pe_ratio (P/E ratio)
- **EN:** The P/E ratio is the share price divided by the company's yearly profit per share. It shows how many rupees people pay for each rupee of profit. Compare it with similar companies, not with everything.
- **te:** P/E రేషియో అంటే షేర్ ధరను కంపెనీ ఏడాది లాభం (ఒక్కో షేర్‌కి) తో భాగిస్తే వచ్చేది. ప్రతి ఒక్క రూపాయి లాభానికి జనం ఎన్ని రూపాయలు చెల్లిస్తున్నారో ఇది చూపిస్తుంది. దీన్ని అన్నిటితో కాకుండా, సారూప్య కంపెనీలతో పోల్చాలి.
- **hi:** P/E रेशियो शेयर के दाम को कंपनी के सालाना प्रति-शेयर मुनाफ़े से भाग देने पर मिलता है। यह दिखाता है कि हर एक रुपये मुनाफ़े के लिए लोग कितने रुपये देते हैं। इसकी तुलना मिलती-जुलती कंपनियों से करें, हर किसी से नहीं।
- **Fix (te):** _()_  · **Fix (hi):** _()_

### circuit_limit (circuit limit)
- **EN:** A circuit limit is the most a share's price can move up or down in one day. When it reaches that limit, trading in it stops moving in that direction for the day.
- **te:** సర్క్యూట్ లిమిట్ అంటే ఒక రోజులో షేర్ ధర పైకి లేదా కిందికి కదలగల గరిష్ఠ పరిమితి. ఆ పరిమితిని చేరుకున్నప్పుడు, ఆ రోజుకు ఆ దిశలో ట్రేడింగ్ ఆగిపోతుంది.
- **hi:** सर्किट लिमिट वह अधिकतम सीमा है जितना किसी शेयर का दाम एक दिन में ऊपर या नीचे जा सकता है। उस सीमा पर पहुँचने पर, उस दिन उस दिशा में ट्रेडिंग रुक जाती है।
- **Fix (te):** _()_  · **Fix (hi):** _()_

### demat_account (demat account)
- **EN:** A demat account holds your shares in electronic form, like a bank account holds money. You also need a trading account to place orders.
- **te:** డీమ్యాట్ అకౌంట్ మీ షేర్లను ఎలక్ట్రానిక్ రూపంలో ఉంచుతుంది, బ్యాంక్ అకౌంట్ డబ్బును ఉంచినట్టు. ఆర్డర్లు పెట్టడానికి మీకు ట్రేడింగ్ అకౌంట్ కూడా అవసరం.
- **hi:** डीमैट अकाउंट आपके शेयरों को इलेक्ट्रॉनिक रूप में रखता है, जैसे बैंक अकाउंट पैसे रखता है। ऑर्डर देने के लिए आपको एक ट्रेडिंग अकाउंट भी चाहिए।
- **Fix (te):** _()_  · **Fix (hi):** _()_

### etf (ETF)
- **EN:** An ETF is a fund that trades on the exchange like a share and follows something, such as an index or the price of gold. GoldBEES is a gold ETF.
- **te:** ETF అనేది షేర్ లాగా ఎక్స్ఛేంజ్‌లో ట్రేడ్ అయ్యే ఒక ఫండ్; అది ఇండెక్స్ లేదా బంగారం ధర లాంటి దేనినో అనుసరిస్తుంది. GoldBEES ఒక గోల్డ్ ETF.
- **hi:** ETF एक फंड है जो शेयर की तरह एक्सचेंज पर ट्रेड होता है और किसी चीज़ का अनुसरण करता है, जैसे कोई इंडेक्स या सोने का दाम। GoldBEES एक गोल्ड ETF है।
- **Fix (te):** _()_  · **Fix (hi):** _()_

### dividend (dividend)
- **EN:** A dividend is a part of a company's profit paid to its shareholders. Companies are not required to pay it, and the amount can change every year.
- **te:** డివిడెండ్ అంటే కంపెనీ లాభంలో షేర్‌హోల్డర్లకు ఇచ్చే భాగం. దీన్ని ఇవ్వడం కంపెనీలకు తప్పనిసరి కాదు, మొత్తం ప్రతి ఏడాది మారవచ్చు.
- **hi:** डिविडेंड कंपनी के मुनाफ़े का वह हिस्सा है जो शेयरधारकों को दिया जाता है। इसे देना कंपनियों के लिए ज़रूरी नहीं है, और रकम हर साल बदल सकती है।
- **Fix (te):** _()_  · **Fix (hi):** _()_

### volume (volume)
- **EN:** Volume is how many shares were traded in a period. Large volume means many people were trading it.
- **te:** వాల్యూమ్ అంటే ఒక కాలంలో ఎన్ని షేర్లు ట్రేడ్ అయ్యాయో. ఎక్కువ వాల్యూమ్ అంటే చాలా మంది దాన్ని ట్రేడ్ చేశారని అర్థం.
- **hi:** वॉल्यूम यानी एक अवधि में कितने शेयर ट्रेड हुए। ज़्यादा वॉल्यूम मतलब बहुत लोग उसे ट्रेड कर रहे थे।
- **Fix (te):** _()_  · **Fix (hi):** _()_

---

## 2. Guardrail constants — `agent/refusal.py`

### Refusal
- **EN:** I can't tell you to buy or sell any share — that's the work of a SEBI-registered adviser. But I can explain what this company does and what happened to it today. Shall I?
- **te:** నేను ఏ షేర్‌ని కొనమని లేదా అమ్మమని చెప్పలేను — అది SEBI నమోదు పొందిన సలహాదారు పని. కానీ ఈ కంపెనీ ఏం చేస్తుందో, ఈ రోజు దానికి ఏం జరిగిందో వివరించగలను. చెప్పమంటారా?
- **hi:** मैं आपको कोई शेयर खरीदने या बेचने के लिए नहीं कह सकता — यह SEBI-रजिस्टर्ड सलाहकार का काम है। लेकिन मैं बता सकता हूँ कि यह कंपनी क्या करती है और आज इसके साथ क्या हुआ। बताऊँ?
- **Fix (te):** _()_  · **Fix (hi):** _()_

### Decline
- **EN:** Sorry, that's outside what I do. But I can explain the stock market, or what happened to a company today.
- **te:** క్షమించండి, అది నా పని పరిధిలో లేదు. కానీ స్టాక్ మార్కెట్ గురించి లేదా ఈ రోజు ఒక కంపెనీకి ఏం జరిగిందో వివరించగలను.
- **hi:** माफ़ कीजिए, यह मेरे काम के दायरे में नहीं है। लेकिन मैं स्टॉक मार्केट के बारे में या आज किसी कंपनी के साथ क्या हुआ, समझा सकता हूँ।
- **Fix (te):** _()_  · **Fix (hi):** _()_

### Disclaimer
- **EN:** Educational only. Not advice.
- **te:** విద్యా ప్రయోజనం కోసం మాత్రమే. ఇది పెట్టుబడి సలహా కాదు.
- **hi:** सिर्फ़ शैक्षणिक जानकारी। यह निवेश सलाह नहीं है।
- **Fix (te):** _()_  · **Fix (hi):** _()_

### Unknown-cause
- **EN:** I can see this movement, but I cannot confirm the reason.
- **te:** ఈ కదలికను నేను చూడగలను, కానీ దానికి కారణాన్ని నిర్ధారించలేను.
- **hi:** मैं यह हलचल देख सकता हूँ, लेकिन इसका कारण पक्का नहीं बता सकता।
- **Fix (te):** _()_  · **Fix (hi):** _()_

### No-data
- **EN:** Sorry, I don't have data for that.
- **te:** క్షమించండి, దీనికి నా దగ్గర డేటా లేదు.
- **hi:** माफ़ कीजिए, इसके लिए मेरे पास डेटा नहीं है।
- **Fix (te):** _()_  · **Fix (hi):** _()_

---

## 3. Clarify prompts
- Ambiguous (te): మీరు హెచ్‌డిఎఫ్‌సి బ్యాంక్ లేదా హెచ్‌డిఎఫ్‌సి లైఫ్ గురించి అడుగుతున్నారా?
- Ambiguous (hi): क्या आप HDFC Bank या HDFC Life के बारे में पूछ रहे हैं?
- Generic (te): మీరు ఏ కంపెనీ లేదా అంశం గురించి అడుగుతున్నారో కొంచెం స్పష్టంగా చెప్పగలరా?
- Generic (hi): आप किस कंपनी या विषय के बारे में पूछ रहे हैं, थोड़ा साफ़ बताएँगे?
