"""Tier-2 corpus: short, factual company/instrument one-pagers.

Static reference notes (what each company does) + metadata for filtering. These are the
documents Tier-2 retrieves over, alongside the rolling news headlines fetched live. They are
DATA, not instructions, and contain no numbers that would feed the numeric gate — the answer's
figures still come only from the live tool payloads.

Content is factual background; English (the embedder is multilingual, so Telugu queries match).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Doc:
    id: str
    ticker: str
    sector: str
    doc_type: str
    text: str


NOTES: list[Doc] = [
    Doc("hdfcbank_note", "HDFCBANK.NS", "banking", "company_note",
        "HDFC Bank is India's largest private-sector bank, offering retail and wholesale "
        "banking, loans, credit cards and payments. Its earnings are driven by net interest "
        "income and loan growth. It is a heavyweight in the Nifty and Sensex."),
    Doc("hdfclife_note", "HDFCLIFE.NS", "insurance", "company_note",
        "HDFC Life is a life-insurance company selling protection, savings and pension plans. "
        "Its performance is tracked through new business premium and value of new business."),
    Doc("hdfcamc_note", "HDFCAMC.NS", "asset_management", "company_note",
        "HDFC Asset Management runs HDFC Mutual Fund. It earns fees on the assets it manages, "
        "so its revenue moves with assets under management and market levels."),
    Doc("gail_note", "GAIL.NS", "energy_gas", "company_note",
        "GAIL (India) is the country's largest natural-gas transmission and marketing company, "
        "also present in petrochemicals and LPG. Gas transmission volumes, petrochemical "
        "margins and government gas pricing affect its results."),
    Doc("ioc_note", "IOC.NS", "energy_oil", "company_note",
        "Indian Oil Corporation (IOC) is a state-owned oil refiner and fuel retailer. Its "
        "profit depends heavily on refining margins and marketing margins on petrol and diesel, "
        "which move with crude-oil prices and government policy."),
    Doc("goldbees_note", "GOLDBEES.NS", "etf_gold", "etf_note",
        "GoldBEES is an exchange-traded fund that tracks the domestic price of physical gold. "
        "It is not a company and has no earnings or P/E. Its price follows the gold price and "
        "the rupee-dollar rate, minus a small expense ratio."),
    Doc("nifty_note", "^NSEI", "index", "index_note",
        "The Nifty 50 is an index of 50 large companies listed on the NSE, spanning banking, "
        "IT, energy and consumer sectors. It is a broad gauge of the Indian market."),
    Doc("sensex_note", "^BSESN", "index", "index_note",
        "The Sensex is an index of 30 large companies on the BSE and is India's oldest market "
        "index. It moves closely with the Nifty 50."),
]

BY_ID = {d.id: d for d in NOTES}
