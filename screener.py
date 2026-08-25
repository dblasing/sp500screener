"""
S&P 500 Dividend Growth Screener
Applies 4 criteria to ~150 S&P 500 dividend stocks and writes data.json.
Run manually or via GitHub Actions (.github/workflows/screen.yml).
"""

from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta

import yfinance as yf
import pandas as pd

TICKERS = [
    # Technology
    "AAPL","MSFT","AVGO","TXN","QCOM","IBM","ADI","ADP","INTU","PAYX","KLAC","MCHP",
    "CSCO","TEL","MSI","GLW",
    # Healthcare
    "JNJ","ABBV","MRK","ABT","MDT","BMY","AMGN","PFE","ZTS","SYK","BDX","DHR","EW",
    "GILD","CVS",
    # Consumer Staples
    "KO","PEP","PG","CL","KMB","WMT","MO","PM","GIS","HRL","CLX","CHD","ECL","MKC",
    "COST","SYY","ADM","HSY",
    # Energy
    "XOM","CVX","COP","EOG","PSX","VLO","MPC","KMI","WMB","OKE",
    "SLB","OXY",
    # Financials / Insurance / Banking
    "JPM","BAC","WFC","GS","BLK","AFL","CB","ALL","TRV","AXP","USB","PNC","TFC",
    "MSCI","SPGI","MCO","ICE","CME",
    "MS","C",
    # Industrials
    "HON","MMM","RTX","LMT","CAT","DE","EMR","ETN","ITW","DOV","ROP","AME",
    "UNP","GE","PH","FDX","UPS",
    # Utilities
    "NEE","DUK","SO","AEP","WEC","XEL","ES","AWK","ED","PPL",
    "SRE","D","EXC",
    # Real Estate
    "O","PLD","AMT","DLR","PSA",
    "EQIX","SPG","VICI","WELL","AVB","EQR",
    # Materials
    "LIN","APD","SHW","NUE","PKG",
    "NEM","FCX","DOW","VMC","MLM",
    # Communication
    "VZ","T","CMCSA","OMC",
    "GOOGL","META","TMUS","EA","IPG",
    # Consumer Discretionary
    "HD","LOW","TGT","MCD","SBUX","NKE","YUM","DRI",
    "TJX","BKNG","MAR",
]


def calculate_cagr(start_val, end_val, years):
    """Compound Annual Growth Rate between two dividend totals `years` apart."""
    if not start_val or not end_val or start_val <= 0 or end_val <= 0 or years <= 0:
        return None
    try:
        return round(((end_val / start_val) ** (1.0 / years) - 1.0) * 100, 2)
    except Exception:
        return None


def assign_tier(streak_years: int) -> str:
    """Dividend category tier based on consecutive years of growth."""
    if streak_years >= 50:
        return "Dividend King"
    if streak_years >= 25:
        return "Dividend Aristocrat"
    if streak_years >= 10:
        return "Dividend Contender"
    if streak_years >= 5:
        return "Dividend Challenger"
    if streak_years >= 3:
        return "Dividend Starter"
    return "No Streak"


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
    """Count consecutive years of dividend growth using only completed calendar years,
    plus 1/3/5-year CAGR on the annual dividend total."""
    empty = {"pass": False, "streak": 0, "cagr_1y": None, "cagr_3y": None, "cagr_5y": None, "tier": assign_tier(0)}
    if divs is None or divs.empty:
        return empty

    divs = divs[divs > 0]
    if len(divs) < 4:
        return empty

    by_year = divs.groupby(divs.index.year).sum()

    # Exclude the current (incomplete) year — partial year totals are always
    # lower than completed years, which would incorrectly break the streak.
    current_year = datetime.now(timezone.utc).year
    by_year = by_year[by_year.index < current_year].sort_index()

    if len(by_year) < 2:
        return empty

    amounts = by_year.values
    streak = 0
    for i in range(len(amounts) - 1, 0, -1):
        if amounts[i] >= amounts[i - 1] * 0.98:
            streak += 1
        else:
            break

    cagr_1y = calculate_cagr(amounts[-2], amounts[-1], 1) if len(amounts) >= 2 else None
    cagr_3y = calculate_cagr(amounts[-4], amounts[-1], 3) if len(amounts) >= 4 else None
    cagr_5y = calculate_cagr(amounts[-6], amounts[-1], 5) if len(amounts) >= 6 else None

    return {
        "pass": streak >= 3,
        "streak": int(streak),
        "cagr_1y": cagr_1y,
        "cagr_3y": cagr_3y,
        "cagr_5y": cagr_5y,
        "tier": assign_tier(int(streak)),
    }


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

        # Guard: must pay a dividend
        if div_yield < 0.001:
            return None

        # Guard: yield sanity check — anything above 20% is almost certainly a
        # stale/bad data artifact from Yahoo Finance (e.g. a special one-time
        # dividend inflating the trailing figure)
        if div_yield > 0.20:
            print(f"  [{ticker}] skipped — yield {div_yield*100:.1f}% looks like bad data")
            return None

        hist = stock.history(period="5y", interval="1wk", auto_adjust=True)
        divs = stock.dividends

        # Guard: need enough price history to assess trends
        if hist.empty or len(hist) < 13:
            return None

        t5  = price_trend(hist, 365 * 5)
        t90 = price_trend(hist, 90)
        div = dividend_analysis(divs)

        rev_growth = info.get("revenueGrowth")
        rev_avail  = rev_growth is not None

        # Guard: revenue growth sanity check — values outside ±200% are likely bad data
        if rev_avail and abs(rev_growth) > 2.0:
            rev_avail = False
            rev_growth = None

        rev_pass = bool(rev_growth > 0) if rev_avail else None

        status_key = compute_status(t5["pass"], t90["pass"], rev_pass, div["pass"], rev_avail)
        if not status_key:
            return None

        # Payout ratio — informational safety metric, sector-aware threshold.
        # Does not affect status_key/pass criteria; shown as an extra signal.
        raw_payout = info.get("payoutRatio")
        payout_ratio_pct = round(raw_payout * 100, 2) if raw_payout is not None else None
        sector_norm = normalize_sector(info.get("sector", ""))
        max_payout = 85.0 if sector_norm in ("Utilities", "Real Estate") else 75.0
        payout_flag = payout_ratio_pct is not None and payout_ratio_pct > max_payout

        # Build detail note
        parts = []
        if t5["pct"]  is not None: parts.append(f"5yr: {'+' if t5['pct'] >= 0 else ''}{t5['pct']*100:.1f}%")
        if t90["pct"] is not None: parts.append(f"90d: {'+' if t90['pct'] >= 0 else ''}{t90['pct']*100:.1f}%")
        if rev_avail:               parts.append(f"Rev: {'+' if rev_growth >= 0 else ''}{rev_growth*100:.1f}% YoY")
        if div["streak"] > 0:       parts.append(f"Div streak: {div['streak']} yr{'s' if div['streak'] != 1 else ''}")
        if div["cagr_3y"] is not None: parts.append(f"3Y div CAGR: {div['cagr_3y']:+.1f}%")
        if payout_ratio_pct is not None: parts.append(f"Payout: {payout_ratio_pct:.1f}%{' ⚠' if payout_flag else ''}")

        yield_num = round(div_yield * 100, 2)

        return {
            "ticker":         ticker,
            "company":        info.get("longName") or info.get("shortName") or ticker,
            "sector":         sector_norm,
            "t5":             t5,
            "t90":            t90,
            "revPass":        rev_pass,
            "revPct":         round(rev_growth, 4) if rev_avail else None,
            "revAvail":       rev_avail,
            "divPass":        div["pass"],
            "divStreak":      div["streak"],
            "cagr1y":         div["cagr_1y"],
            "cagr3y":         div["cagr_3y"],
            "cagr5y":         div["cagr_5y"],
            "tier":           div["tier"],
            "payoutPct":      payout_ratio_pct,
            "payoutFlag":     payout_flag,
            "yieldNum":       yield_num,
            "yieldRaw":       f"{yield_num:.1f}%",
            "statusKey":      status_key,
            "note":           " · ".join(parts),
        }

    except Exception as e:
        print(f"  [{ticker}] failed: {e}", file=sys.stderr)
        return None


def main():
    print(f"Screening {len(TICKERS)} tickers (10 workers)…")
    results = []
    done = 0
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(screen_ticker, t): t for t in TICKERS}
        for future in as_completed(futures):
            ticker = futures[future]
            done += 1
            result = future.result()
            if result:
                print(f"  {done}/{len(TICKERS)} {ticker} → {result['statusKey']} ({result['yieldRaw']})")
                results.append(result)
            else:
                print(f"  {done}/{len(TICKERS)} {ticker} → skipped")

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
