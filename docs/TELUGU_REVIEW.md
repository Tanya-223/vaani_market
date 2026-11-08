# Telugu review sheet

Every Telugu string the app can say or show, with its English meaning. Mark any change
inline (write the corrected Telugu under **Fix:**). Tell the agent your edits and it will
update the code and flip `reviewed:false` → `true`.

---

## 1. Glossary (Tier-1 concept answers) — `retrieval/glossary.py`

### stock_share  (stock / share)
- **English:** A share is a small piece of ownership in a company. If you own shares, you own a tiny part of that company. The price goes up and down as buyers and sellers agree on what the company is worth.
- **Telugu (draft):** షేర్ అంటే ఒక కంపెనీలో చిన్న యాజమాన్య భాగం. మీ దగ్గర షేర్లు ఉంటే, ఆ కంపెనీలో మీకు కొద్ది భాగం సొంతం. కొనేవాళ్లు, అమ్మేవాళ్లు కంపెనీ విలువ గురించి ఒప్పుకున్నప్పుడు ధర పెరుగుతూ, తగ్గుతూ ఉంటుంది.
- **Fix:** _(leave blank if OK)_

### stock_market  (stock market)
- **English:** The stock market is where buyers and sellers trade company shares. In India this happens on exchanges, mainly NSE and BSE. Trading runs from 9:15 in the morning to 3:30 in the afternoon on weekdays.
- **Telugu (draft):** స్టాక్ మార్కెట్ అంటే కంపెనీల షేర్లను కొనడం, అమ్మడం జరిగే చోటు. ఇండియాలో ఇది ప్రధానంగా NSE, BSE అనే ఎక్స్ఛేంజ్‌లలో జరుగుతుంది. ట్రేడింగ్ పని రోజుల్లో ఉదయం 9:15 నుంచి మధ్యాహ్నం 3:30 వరకు జరుగుతుంది.
- **Fix:** _(leave blank if OK)_

### nse_bse  (NSE and BSE)
- **English:** NSE is the National Stock Exchange and BSE is the Bombay Stock Exchange. They are India's two main exchanges. BSE is older, and NSE handles far more trading. Most big companies are listed on both, at almost the same price.
- **Telugu (draft):** NSE అంటే నేషనల్ స్టాక్ ఎక్స్ఛేంజ్, BSE అంటే బాంబే స్టాక్ ఎక్స్ఛేంజ్. ఇవి ఇండియాలోని రెండు ప్రధాన ఎక్స్ఛేంజ్‌లు. BSE పాతది, NSEలో ట్రేడింగ్ చాలా ఎక్కువ. చాలా పెద్ద కంపెనీలు రెండింటిలోనూ దాదాపు ఒకే ధరకు లిస్ట్ అవుతాయి.
- **Fix:** _(leave blank if OK)_

### nifty_sensex  (Nifty and Sensex)
- **English:** Nifty 50 is an index of fifty large companies on NSE. Sensex is an index of thirty large companies on BSE. When people say the market went up, they usually mean one of these went up.
- **Telugu (draft):** నిఫ్టీ 50 అంటే NSEలోని యాభై పెద్ద కంపెనీల ఇండెక్స్. సెన్సెక్స్ అంటే BSEలోని ముప్ఫై పెద్ద కంపెనీల ఇండెక్స్. మార్కెట్ పెరిగింది అని జనం అన్నప్పుడు, సాధారణంగా వీటిలో ఒకటి పెరిగిందని అర్థం.
- **Fix:** _(leave blank if OK)_

### candlestick  (candlestick chart)
- **English:** A candlestick shows what a price did in one period, such as one day. The thick part is the body, between the opening and the closing price. The thin lines above and below are the wicks, showing the highest and lowest prices. Commonly a green candle means the price closed higher than it opened, and a red candle means it closed lower.
- **Telugu (draft):** క్యాండిల్‌స్టిక్ అనేది ఒక రోజు లాంటి ఒక కాలంలో ధర ఎలా కదిలిందో చూపిస్తుంది. మందపాటి భాగం బాడీ, అది ఓపెనింగ్, క్లోజింగ్ ధరల మధ్య ఉంటుంది. పైన కింద ఉండే సన్నని గీతలు విక్స్, అవి అత్యధిక, అత్యల్ప ధరలను చూపిస్తాయి. సాధారణంగా ఆకుపచ్చ క్యాండిల్ అంటే ధర ఓపెన్ కంటే ఎక్కువ క్లోజ్ అయిందని, ఎరుపు క్యాండిల్ అంటే తక్కువ క్లోజ్ అయిందని అర్థం.
- **Fix:** _(leave blank if OK)_

### market_cap  (market capitalisation)
- **English:** Market cap is the total value of a company's shares. It is the share price multiplied by the number of shares. In India it is usually told in crore rupees.
- **Telugu (draft):** మార్కెట్ క్యాప్ అంటే ఒక కంపెనీ షేర్ల మొత్తం విలువ. ఇది షేర్ ధరను షేర్ల సంఖ్యతో గుణిస్తే వస్తుంది. ఇండియాలో దీన్ని సాధారణంగా కోట్ల రూపాయల్లో చెబుతారు.
- **Fix:** _(leave blank if OK)_

### pe_ratio  (P/E ratio)
- **English:** The P/E ratio is the share price divided by the company's yearly profit per share. It shows how many rupees people pay for each rupee of profit. Compare it with similar companies, not with everything.
- **Telugu (draft):** P/E రేషియో అంటే షేర్ ధరను కంపెనీ ఏడాది లాభం (ఒక్కో షేర్‌కి) తో భాగిస్తే వచ్చేది. ప్రతి ఒక్క రూపాయి లాభానికి జనం ఎన్ని రూపాయలు చెల్లిస్తున్నారో ఇది చూపిస్తుంది. దీన్ని అన్నిటితో కాకుండా, సారూప్య కంపెనీలతో పోల్చాలి.
- **Fix:** _(leave blank if OK)_

### circuit_limit  (circuit limit)
- **English:** A circuit limit is the most a share's price can move up or down in one day. When it reaches that limit, trading in it stops moving in that direction for the day.
- **Telugu (draft):** సర్క్యూట్ లిమిట్ అంటే ఒక రోజులో షేర్ ధర పైకి లేదా కిందికి కదలగల గరిష్ఠ పరిమితి. ఆ పరిమితిని చేరుకున్నప్పుడు, ఆ రోజుకు ఆ దిశలో ట్రేడింగ్ ఆగిపోతుంది.
- **Fix:** _(leave blank if OK)_

### demat_account  (demat account)
- **English:** A demat account holds your shares in electronic form, like a bank account holds money. You also need a trading account to place orders.
- **Telugu (draft):** డీమ్యాట్ అకౌంట్ మీ షేర్లను ఎలక్ట్రానిక్ రూపంలో ఉంచుతుంది, బ్యాంక్ అకౌంట్ డబ్బును ఉంచినట్టు. ఆర్డర్లు పెట్టడానికి మీకు ట్రేడింగ్ అకౌంట్ కూడా అవసరం.
- **Fix:** _(leave blank if OK)_

### etf  (ETF)
- **English:** An ETF is a fund that trades on the exchange like a share and follows something, such as an index or the price of gold. GoldBEES is a gold ETF.
- **Telugu (draft):** ETF అనేది షేర్ లాగా ఎక్స్ఛేంజ్‌లో ట్రేడ్ అయ్యే ఒక ఫండ్; అది ఇండెక్స్ లేదా బంగారం ధర లాంటి దేనినో అనుసరిస్తుంది. GoldBEES ఒక గోల్డ్ ETF.
- **Fix:** _(leave blank if OK)_

### dividend  (dividend)
- **English:** A dividend is a part of a company's profit paid to its shareholders. Companies are not required to pay it, and the amount can change every year.
- **Telugu (draft):** డివిడెండ్ అంటే కంపెనీ లాభంలో షేర్‌హోల్డర్లకు ఇచ్చే భాగం. దీన్ని ఇవ్వడం కంపెనీలకు తప్పనిసరి కాదు, మొత్తం ప్రతి ఏడాది మారవచ్చు.
- **Fix:** _(leave blank if OK)_

### volume  (volume)
- **English:** Volume is how many shares were traded in a period. Large volume means many people were trading it.
- **Telugu (draft):** వాల్యూమ్ అంటే ఒక కాలంలో ఎన్ని షేర్లు ట్రేడ్ అయ్యాయో. ఎక్కువ వాల్యూమ్ అంటే చాలా మంది దాన్ని ట్రేడ్ చేశారని అర్థం.
- **Fix:** _(leave blank if OK)_

---

## 2. Guardrail constants — `agent/refusal.py`

### Refusal (advice)
- **English:** I can't tell you to buy or sell any share — that's the work of a SEBI-registered adviser. But I can explain what this company does and what happened to it today. Shall I?
- **Telugu (draft):** నేను ఏ షేర్‌ని కొనమని లేదా అమ్మమని చెప్పలేను — అది SEBI నమోదు పొందిన సలహాదారు పని. కానీ ఈ కంపెనీ ఏం చేస్తుందో, ఈ రోజు దానికి ఏం జరిగిందో వివరించగలను. చెప్పమంటారా?
- **Fix:** _(leave blank if OK)_

### Decline (out of scope)
- **English:** Sorry, that's outside what I do. But I can explain the stock market, or what happened to a company today.
- **Telugu (draft):** క్షమించండి, అది నా పని పరిధిలో లేదు. కానీ స్టాక్ మార్కెట్ గురించి లేదా ఈ రోజు ఒక కంపెనీకి ఏం జరిగిందో వివరించగలను.
- **Fix:** _(leave blank if OK)_

### Disclaimer
- **English:** Educational only. Not advice.
- **Telugu (draft):** విద్యా ప్రయోజనం కోసం మాత్రమే. ఇది పెట్టుబడి సలహా కాదు.
- **Fix:** _(leave blank if OK)_

### Unknown-cause line
- **English:** I can see this movement, but I cannot confirm the reason.
- **Telugu (draft):** ఈ కదలికను నేను చూడగలను, కానీ దానికి కారణాన్ని నిర్ధారించలేను.
- **Fix:** _(leave blank if OK)_

### No-data line
- **English:** Sorry, I don't have data for that.
- **Telugu (draft):** క్షమించండి, దీనికి నా దగ్గర డేటా లేదు.
- **Fix:** _(leave blank if OK)_

---

## 3. Clarify prompts
### Ambiguous-ticker question — `agent/ticker_resolver.py`
- **English:** "Are you asking about X or Y?" (X/Y filled with company names)
- **Telugu template:** మీరు హెచ్‌డిఎఫ్‌సి బ్యాంక్ లేదా హెచ్‌డిఎఫ్‌సి లైఫ్ గురించి అడుగుతున్నారా?
- **Fix:** _(leave blank if OK)_

### Generic clarify — `agent/orchestrate.py`
- **English:** Could you say a bit more clearly which company or topic you mean?
- **Telugu (draft):** మీరు ఏ కంపెనీ లేదా అంశం గురించి అడుగుతున్నారో కొంచెం స్పష్టంగా చెప్పగలరా?
- **Fix:** _(leave blank if OK)_

### Company display names — `agent/ticker_resolver.py`
- HDFCBANK.NS: **HDFC Bank** → Telugu `హెచ్‌డిఎఫ్‌సి బ్యాంక్`
- HDFCLIFE.NS: **HDFC Life** → Telugu `హెచ్‌డిఎఫ్‌సి లైఫ్`
- HDFCAMC.NS: **HDFC AMC** → Telugu `హెచ్‌డిఎఫ్‌సి ఎఎంసి`
- GAIL.NS: **GAIL** → Telugu `గెయిల్`
- IOC.NS: **Indian Oil (IOC)** → Telugu `ఇండియన్ ఆయిల్`
- GOLDBEES.NS: **GoldBEES** → Telugu `గోల్డ్ బీస్`
- ^NSEI: **Nifty 50** → Telugu `నిఫ్టీ 50`
- ^BSESN: **Sensex** → Telugu `సెన్సెక్స్`