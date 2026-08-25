# S&P 500 Dividend Growth Stock Screener

A dynamic, data-driven stock screener that applies four dividend + price-trend criteria to ~150 S&P 500 dividend-paying stocks, screened concurrently and enriched with dividend CAGR, payout ratio, and dividend tier badges. Data is fetched server-side via a daily GitHub Actions workflow — no API key, no backend, no CORS issues.

🔗 **Live site:** https://dblasing.github.io/sp500screener

---

## Architecture

```
screener.py  ──▶  data.json  ──▶  index.html
(GitHub Actions,    (committed      (reads data.json,
 runs daily)         to repo)        served via Pages)
```

- **`screener.py`** — Python script that pulls live data from Yahoo Finance (`yfinance`) concurrently (10 worker threads), applies all four criteria, and writes `data.json`
- **`requirements.txt`** — pinned dependencies (`yfinance`, `pandas`)
- **`.github/workflows/screen.yml`** — runs `screener.py` automatically at 7am ET on weekdays; pip-caches dependencies, cancels overlapping runs, and commits `data.json` back to the repo
- **`index.html`** — pure HTML/CSS/JS; fetches `data.json` from the same GitHub Pages domain on load; no external API calls from the browser

---

## Screening Criteria

Every stock is evaluated against all four criteria. The criteria are applied programmatically from real market data — no manual curation.

| # | Criterion | Definition | Data Source |
|---|-----------|------------|-------------|
| 1 | **5-Year Trend** | Net price change over trailing ~5 years > +5% | Weekly price history via `yfinance` |
| 2 | **90-Day Trend** | Net price change over trailing 90 days > 0% | Weekly price history via `yfinance` |
| 3 | **YoY Revenue Growth** | TTM revenue growth > 0% | `revenueGrowth` via `yfinance` |
| 4 | **Dividend Growth** | Annual dividends increased for 3+ consecutive completed calendar years | Dividend history via `yfinance` |

> **Note on criterion 4:** Only fully completed calendar years are used to compute the streak — the current (incomplete) year is excluded to avoid falsely breaking a streak mid-year.

---

## Data Quality Guards

`screener.py` applies the following sanity checks before including any stock in results:

| Guard | Rule | Reason |
|-------|------|--------|
| **Yield cap** | Yield > 20% → stock excluded | Yahoo Finance sometimes reports stale or one-time special dividend data that inflates the trailing yield to obviously wrong levels (e.g. 484%) |
| **Revenue sanity** | \|Revenue growth\| > 200% → treated as unavailable | Extreme revenue swings are usually M&A or restatement artifacts, not organic growth; flagging as N/A is more honest than passing/failing on bad data |
| **Min price history** | < 13 weeks of price data → stock excluded | Can't meaningfully assess either trend without at least one quarter of weekly data |

---

## Dividend Safety & Tier Metrics

These are informational metrics layered on top of the four screening criteria — they don't affect `passed`/`Status`, but help judge dividend quality at a glance:

| Metric | Definition |
|--------|------------|
| **Dividend Tier** | Badge based on consecutive years of dividend growth: **King** (50+ yrs), **Aristocrat** (25+ yrs), **Contender** (10+ yrs), **Challenger** (5+ yrs), **Starter** (3+ yrs) |
| **Dividend CAGR (1Y/3Y/5Y)** | Compound annual growth rate of the total annual dividend, computed over completed calendar years |
| **Payout Ratio** | `payoutRatio` from `yfinance`, flagged with ⚠ when it exceeds a sector-aware threshold (85% for Utilities/Real Estate, 75% elsewhere) — a high payout ratio can signal a dividend at risk |

> **Note:** Payout ratio for REITs (Real Estate) is based on net income, not FFO/AFFO, so it commonly reads high for otherwise healthy REITs — treat the ⚠ flag as a prompt to check FFO payout independently, not a fail.

---

## Status Key

Status is computed automatically based on which criteria pass:

| Badge | Logic |
|-------|-------|
| ✔ Meets All | All 4 criteria pass |
| ✦ Likely | 5yr ✔ · 90d ✔ · Div ✔ · Revenue data unavailable |
| ◎ Monitor | 3 pass; 90-day trend is the failing criterion |
| ~ Borderline | 3 pass; dividend streak or revenue is the failing criterion |
| ⚠ Flagged | 90-day trend broken (significant recent decline) |

## Trend Key

| Symbol | Meaning | Threshold |
|--------|---------|-----------|
| ⬆ Uptrend | Clear upward movement | 5yr > +5% · 90d > 0% |
| ↗ Moderate | Positive but slowing | 5yr > -10% · 90d > -5% |
| ↔ Mixed | Choppy / marginal | 5yr > -25% · 90d > -12% |
| ⚠ Flagged | Significant decline | Below mixed thresholds |

---

## Features

- **Automated daily data** — GitHub Actions runs `screener.py` every weekday at 7am ET
- **~150 S&P 500 dividend stocks** evaluated with live market data, fetched concurrently (10 worker threads)
- **All criteria computed programmatically** — no manual status assignments
- **Dividend tier badges** (King / Aristocrat / Contender / Challenger / Starter) based on streak length
- **Dividend CAGR (1Y/3Y/5Y)** and **sector-aware payout ratio safety flag**
- **Filter** by status, sector, minimum yield, criteria pass count, and dividend tier
- **Search** by ticker or company name
- **Sort** any column ascending or descending
- **Export** filtered results to **CSV** or **XLS** directly from the browser — exports reflect whatever is currently on screen after filters are applied, including tier, CAGR, and payout ratio
- **Color-coded** sector badges, trend indicators, status pills, tier badges, and yield values
- **Per-row criteria dots** (● ● ● ●) showing exactly which of the 4 criteria each stock passes or fails
- **Auto-generated detail notes** with real figures: `5yr: +142% · 90d: +8.2% · Rev: +6.1% YoY · Div streak: 15 yrs · 3Y div CAGR: +6.2% · Payout: 58.3%`
- **Data timestamp** shown on the page — always know when the last run was
- Zero frontend dependencies — pure HTML, CSS, and vanilla JavaScript

---

## Sector Coverage

| Color | Sectors |
|-------|---------|
| 🔵 Blue | Technology |
| 🟢 Green | Healthcare |
| 🟡 Yellow | Consumer Staples / Consumer Defensive |
| 🟠 Orange | Energy |
| 🟣 Purple | Financials, Insurance, Banking |
| 🩵 Cyan | Utilities |
| 🩷 Pink | Real Estate |
| ⚫ Gray | Industrials, Materials, Communication, Consumer Discretionary |

---

## Ticker Universe (~150 S&P 500 Dividend Stocks)

Results vary by date based on live market data. Stocks that don't pay a dividend are automatically excluded.

| Sector | Tickers |
|--------|---------|
| Technology | AAPL, MSFT, AVGO, TXN, QCOM, IBM, ADI, ADP, INTU, PAYX, KLAC, MCHP, CSCO, TEL, MSI, GLW |
| Healthcare | JNJ, ABBV, MRK, ABT, MDT, BMY, AMGN, PFE, ZTS, SYK, BDX, DHR, EW, GILD, CVS |
| Consumer Staples | KO, PEP, PG, CL, KMB, WMT, MO, PM, GIS, HRL, CLX, CHD, ECL, MKC, COST, SYY, ADM, HSY |
| Energy | XOM, CVX, COP, EOG, PSX, VLO, MPC, KMI, WMB, OKE, SLB, OXY |
| Financials | JPM, BAC, WFC, GS, BLK, AFL, CB, ALL, TRV, AXP, USB, PNC, TFC, MSCI, SPGI, MCO, ICE, CME, MS, C |
| Industrials | HON, MMM, RTX, LMT, CAT, DE, EMR, ETN, ITW, DOV, ROP, AME, UNP, GE, PH, FDX, UPS |
| Utilities | NEE, DUK, SO, AEP, WEC, XEL, ES, AWK, ED, PPL, SRE, D, EXC |
| Real Estate | O, PLD, AMT, DLR, PSA, EQIX, SPG, VICI, WELL, AVB, EQR |
| Materials | LIN, APD, SHW, NUE, PKG, NEM, FCX, DOW, VMC, MLM |
| Communication | VZ, T, CMCSA, OMC, GOOGL, META, TMUS, EA, IPG |
| Consumer Discretionary | HD, LOW, TGT, MCD, SBUX, NKE, YUM, DRI, TJX, BKNG, MAR |

---

## Usage

### View the live site
```
https://dblasing.github.io/sp500screener
```
The page auto-loads the latest `data.json` on open. Click **Refresh Data** to re-fetch without a full page reload.

### Trigger a manual screen run
1. Go to **github.com/dblasing/sp500screener/actions**
2. Click **Run Dividend Growth Screen** → **Run workflow** → **Run workflow**
3. Wait ~5 minutes for it to complete
4. Hard reload the site (`Cmd + Shift + R`)

### Run locally
```bash
# Clone the repo
git clone https://github.com/dblasing/sp500screener.git
cd sp500screener

# Install dependencies
pip install -r requirements.txt

# Run the screener (generates data.json)
python screener.py

# Serve the site locally
python3 -m http.server 3456
# then visit http://localhost:3456
```

### Add or remove tickers
Edit the `TICKERS` list in `screener.py`, then trigger a new run. Any stock not paying a dividend will be automatically skipped regardless of whether it's in the list.

### Adjust criteria thresholds
Edit the `price_trend()` and `compute_status()` functions in `screener.py`. Thresholds are clearly labeled with comments.

### Adjust tier or payout ratio thresholds
Edit `assign_tier()` (streak-to-tier cutoffs) or the `max_payout` sector check inside `screen_ticker()` in `screener.py`.

---

## Project Structure

```
sp500screener/
├── index.html                      # Frontend — reads data.json, renders table
├── screener.py                     # Screening logic — writes data.json
├── requirements.txt                # Pinned Python dependencies
├── data.json                       # Generated output — committed by GitHub Actions
├── .github/
│   └── workflows/
│       └── screen.yml              # Runs screener.py daily at 7am ET (weekdays)
└── README.md
```

---

## Data Source

All market data comes from **Yahoo Finance** via the [`yfinance`](https://github.com/ranaroussi/yfinance) Python library (unofficial API, no key required). Specifically:

- `stock.history(period="5y", interval="1wk")` — weekly price history for trend analysis
- `stock.dividends` — historical dividend payments for streak calculation
- `stock.info["revenueGrowth"]` — TTM YoY revenue growth
- `stock.info["trailingAnnualDividendYield"]` — current dividend yield

---

## Disclaimer

This screener is for **research and educational purposes only**. It is not investment advice.

All data is sourced from Yahoo Finance via the unofficial `yfinance` API. Yahoo Finance occasionally returns spurious, stale, or otherwise incorrect values — particularly for dividend yields, revenue growth, and sector classifications. **Always sanity-check results before acting on them.** Verify all figures independently through primary sources (company filings, investor relations pages, or a paid data provider) before making any investment decisions.

---

## License

MIT — free to use, fork, and adapt.
