"""
S&P 500 Dividend Growth Screener
Applies 4 criteria to ~100 S&P 500 dividend stocks and writes data.json.
Run manually or via GitHub Actions (.github/workflows/screen.yml).
"""

import json
import sys
from datetime import datetime, timezone, timedelta

import yfinance as yf
import pandas as pd

TICKERS = [
    # Technology
    "AAPL","MSFT","AVGO","TXN","QCOM","IBM","ADI","ADP","INTU","PAYX","KLAC","MCHP",
    # Healthcare
    "JNJ","ABBV","MRK","ABT","MDT","BMY","AMGN","PFE","ZTS","SYK","BDX","DHR","EW",
    # Consumer Staples
    "KO","PEP","PG","CL","KMB","WMT","MO","PM","GIS","HRL","CLX","CHD","ECL","MKC",
    # Energy
    "XOM","CVX","COP","EOG","PSX","VLO","MPC","KMI","WMB","OKE",
    # Financials / Insurance / Banking
    "JPM","BAC","WFC","GS","BLK","AFL","CB","ALL","TRV","AXP","USB","PNC","TFC",
    "MSCI","SPGI","MCO","ICE","CME",
    # Industrials
    "HON","MMM","RTX","LMT","CAT","DE","EMR","ETN","ITW","DOV","ROP","AME",
    # Utilities
    "NEE","DUK","SO","AEP","WEC","XEL","ES","AWK","ED","PPL",
    # Real Estate
    "O","PLD","AMT","DLR","PSA",
    # Materials
    "LIN","APD","SHW","NUE","PKG",
    # Communication
    "VZ","T","CMCSA","OMC",
    # Consumer Discretionary
    "HD","LOW","TGT","MCD","SBUX","NKE","YUM","DRI",
]


def price_trend(hist: pd.DataFrame, days: int) -> dict:
    """Assess price trend over the last `days` calendar days."""
    if hist.empty or len(hist) < 4:
        return {"label": "Unknown", "cls": "t-unk", "order": 5, "pct": None, "pass": None}

    cutoff = hist.index[-1] - timedelta(days=days)
    subset = hist[hist.index >= cutoff]["Close"].dropna()
    if len(subset) < 2:
        return {"label": "Unknown", "cls": "t-unk", "order": 5, "pct": None, "pass": None}

    start, end = float(subset.iloc[0]), float(subset.iloc[-1])
    pct = (end - start) / start

    if days >= 365 * 4:  # 5-year
        if pct > 0.05:
            return {"label": "⬆ Uptrend",  "cls": "t-up",   "order": 1, "pct": round(pct, 4), "pass": True}
        if pct > -0.10:
            return {"label": "↗ Moderate",  "cls": "t-mod",  "order": 2, "pct": round(pct, 4), "pass": True}
        if pct > -0.25:
            return {"label": "↔ Mixed",     "cls": "t-mix",  "order": 3, "pct": round(pct, 4), "pass": False}
        return     {"label": "⚠ Flagged",  "cls": "t-flag", "order": 4, "pct": round(pct, 4), "pass": False}
    else:  # 90-day
        if pct > 0.00:
            return {"label": "⬆ Uptrend",  "cls": "t-up",   "order": 1, "pct": round(pct, 4), "pass": True}
        if pct > -0.05:
            return {"label": "↗ Moderate",  "cls": "t-mod",  "order": 2, "pct": round(pct, 4), "pass": True}
        if pct > -0.12:
            return {"label": "↔ Mixed",     "cls": "t-mix",  "order": 3, "pct": round(pct, 4), "pass": False}
        return     {"label": "⚠ Flagged",  "cls": "t-flag", "order": 4, "pct": round(pct, 4), "pass": False}


def dividend_analysis(divs: pd.Series) -> dict:
    """Count consecutive years of dividend growth using only completed calendar years."""
    if divs is None or divs.empty:
        return {"pass": False, "streak": 0}

    divs = divs[divs > 0]
    if len(divs) < 4:
        return {"pass": False, "streak": 0}

    by_year = divs.groupby(divs.index.year).sum()

    # Exclude the current (incomplete) year — partial year totals are always
    # lower than completed years, which would incorrectly break the streak.
    current_year = datetime.now(timezone.utc).year
    by_year = by_year[by_year.index < current_year]

    if len(by_year) < 2:
        return {"pass": False, "streak": 0}

    amounts = by_year.values
    streak = 0
    for i in range(len(amounts) - 1, 0, -1):
        if amounts[i] >= amounts[i - 1] * 0.98:
            streak += 1
        else:
            break

    return {"pass": streak >= 3, "streak": int(streak)}


def normalize_sector(sector: str) -> str:
    if not sector:
        return "Other"
    s = sector.lower()
    if "technology" in s or "semiconductor" in s:
        return "Technology"
    if "health" in s:
        return "Healthcare"
    if "staple" in s:
        return "Consumer Staples"
    if "energy" in s:
        return "Energy"
    if "real estate" in s:
        return "Real Estate"
    if "util" in s:
        return "Utilities"
    if "material" in s:
        return "Materials"
    if "communic" in s:
        return "Communication"
    if "industrial" in s:
        return "Industrials"
    if "discret" in s:
        return "Consumer Discretionary"
    if any(k in s for k in ("financial", "bank", "insur", "asset")):
        return "Financials"
    return sector


def compute_status(t5_pass, t90_pass, rev_pass, div_pass, rev_avail: bool) -> str | None:
    passes = sum(v is True for v in [t5_pass, t90_pass, rev_pass if rev_avail else None, div_pass])

    if not rev_avail:
        if t5_pass and t90_pass and div_pass:
            return "likely"
        if sum([t5_pass, t90_pass, div_pass]) >= 2:
            return "border"
        return None

    if passes == 4:
        return "meets"
    if passes == 3:
        if not t90_pass:
            return "monitor"
        return "border"
    if passes == 2:
        return "border"
    return None


def screen_ticker(ticker: str) -> dict | None:
    try:
        stock = yf.Ticker(ticker)
        info  = stock.info or {}

        div_yield = info.get("trailingAnnualDividendYield") or info.get("dividendYield") or 0
        if div_yield < 0.001:
            return None  # not a dividend payer

        hist = stock.history(period="5y", interval="1wk", auto_adjust=True)
        divs = stock.dividends

        t5  = price_trend(hist, 365 * 5)
        t90 = price_trend(hist, 90)
        div = dividend_analysis(divs)

        rev_growth = info.get("revenueGrowth")
        rev_avail  = rev_growth is not None
        rev_pass   = bool(rev_growth > 0) if rev_avail else None

        status_key = compute_status(t5["pass"], t90["pass"], rev_pass, div["pass"], rev_avail)
        if not status_key:
            return None

        # Build detail note
        parts = []
        if t5["pct"]  is not None: parts.append(f"5yr: {'+' if t5['pct'] >= 0 else ''}{t5['pct']*100:.1f}%")
        if t90["pct"] is not None: parts.append(f"90d: {'+' if t90['pct'] >= 0 else ''}{t90['pct']*100:.1f}%")
        if rev_avail:               parts.append(f"Rev: {'+' if rev_growth >= 0 else ''}{rev_growth*100:.1f}% YoY")
        if div["streak"] > 0:       parts.append(f"Div streak: {div['streak']} yr{'s' if div['streak'] != 1 else ''}")

        yield_num = round(div_yield * 100, 2)

        return {
            "ticker":    ticker,
            "company":   info.get("longName") or info.get("shortName") or ticker,
            "sector":    normalize_sector(info.get("sector", "")),
            "t5":        t5,
            "t90":       t90,
            "revPass":   rev_pass,
            "revPct":    round(rev_growth, 4) if rev_avail else None,
            "revAvail":  rev_avail,
            "divPass":   div["pass"],
            "divStreak": div["streak"],
            "yieldNum":  yield_num,
            "yieldRaw":  f"{yield_num:.1f}%",
            "statusKey": status_key,
            "note":      " · ".join(parts),
        }

    except Exception as e:
        print(f"  [{ticker}] failed: {e}", file=sys.stderr)
        return None


def main():
    print(f"Screening {len(TICKERS)} tickers…")
    results = []
    for i, ticker in enumerate(TICKERS, 1):
        print(f"  {i}/{len(TICKERS)} {ticker}", end=" ", flush=True)
        result = screen_ticker(ticker)
        if result:
            print(f"→ {result['statusKey']} ({result['yieldRaw']})")
            results.append(result)
        else:
            print("→ skipped")

    results.sort(key=lambda x: x["yieldNum"], reverse=True)

    output = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count":     len(results),
        "results":   results,
    }

    with open("data.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Wrote {len(results)} stocks to data.json")


if __name__ == "__main__":
    main()
