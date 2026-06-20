# S&P 500 Dividend Growth Stock Screener

A dynamic, data-driven stock screener that applies four dividend + price-trend criteria to ~100 S&P 500 dividend-paying stocks. Data is fetched server-side via a daily GitHub Actions workflow — no API key, no backend, no CORS issues.

🔗 **Live site:** https://dblasing.github.io/sp500screener

---

## Architecture

```
screener.py  ──▶  data.json  ──▶  index.html
(GitHub Actions,    (committed      (reads data.json,
 runs daily)         to repo)        served via Pages)
```

- **`screener.py`** — Python script that pulls live data from Yahoo Finance (`yfinance`), applies all four criteria, and writes `data.json`
- **`.github/workflows/screen.yml`** — runs `screener.py` automatically at 7am ET on weekdays; commits `data.json` back to the repo
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
- **~100 S&P 500 dividend stocks** evaluated with live market data
- **All criteria computed programmatically** — no manual status assignments
- **Filter** by status, sector, minimum yield, and criteria pass count
- **Search** by ticker or company name
- **Sort** any column ascending or descending
- **Export** filtered results to **CSV** or **XLS** directly from the browser — exports reflect whatever is currently on screen after filters are applied
- **Color-coded** sector badges, trend indicators, status pills, and yield values
- **Per-row criteria dots** (● ● ● ●) showing exactly which of the 4 criteria each stock passes or fails
- **Auto-generated detail notes** with real figures: `5yr: +142% · 90d: +8.2% · Rev: +6.1% YoY · Div streak: 15 yrs`
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

## Ticker Universe (~100 S&P 500 Dividend Stocks)

Results vary by date based on live market data. Stocks that don't pay a dividend are automatically excluded.

| Sector | Tickers |
|--------|---------|
| Technology | AAPL, MSFT, AVGO, TXN, QCOM, IBM, ADI, ADP, INTU, PAYX, KLAC, MCHP |
| Healthcare | JNJ, ABBV, MRK, ABT, MDT, BMY, AMGN, PFE, ZTS, SYK, BDX, DHR, EW |
| Consumer Staples | KO, PEP, PG, CL, KMB, WMT, MO, PM, GIS, HRL, CLX, CHD, ECL, MKC |
| Energy | XOM, CVX, COP, EOG, PSX, VLO, MPC, KMI, WMB, OKE |
| Financials | JPM, BAC, WFC, GS, BLK, AFL, CB, ALL, TRV, AXP, USB, PNC, TFC, MSCI, SPGI, MCO, ICE, CME |
| Industrials | HON, MMM, RTX, LMT, CAT, DE, EMR, ETN, ITW, DOV, ROP, AME |
| Utilities | NEE, DUK, SO, AEP, WEC, XEL, ES, AWK, ED, PPL |
| Real Estate | O, PLD, AMT, DLR, PSA |
| Materials | LIN, APD, SHW, NUE, PKG |
| Communication | VZ, T, CMCSA, OMC |
| Consumer Discretionary | HD, LOW, TGT, MCD, SBUX, NKE, YUM, DRI |

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
pip install yfinance pandas

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

---

## Project Structure

```
sp500screener/
├── index.html                      # Frontend — reads data.json, renders table
├── screener.py                     # Screening logic — writes data.json
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
