# S&P 500 Dividend Growth Stock Screener

An interactive, single-file HTML screener that fetches **live data from Yahoo Finance** and applies four dividend + price-trend criteria dynamically across ~100 S&P 500 dividend-paying stocks. No build tools, no dependencies, no backend, no API key required — open `index.html` in any browser or host it on GitHub Pages.

🔗 **Live demo:** https://dblasing.github.io/sp500screener

---

## Screening Criteria

Every stock on the screen must pass (or be evaluated against) all four of the following criteria:

| # | Criterion | Definition |
|---|-----------|------------|
| 1 | **5-Year Trend** | Net upward price movement over the trailing 5-year period |
| 2 | **90-Day Trend** | Upward price momentum over the trailing 90 calendar days |
| 3 | **YoY Revenue Growth** | Most recent fiscal year top-line revenue (or NII for banks) exceeds the prior year |
| 4 | **Dividend Growth** | Dividend per share increased consistently over the past 3–5+ years |

---

## Status Key

| Badge | Meaning |
|-------|---------|
| ✔ Meets All | Passes all four criteria cleanly |
| ✦ Likely | Very likely meets all criteria; confirm 90-day chart |
| ◎ Monitor | Strong long-term fit; one criterion has a near-term concern |
| ~ Borderline | Meets most criteria; one is marginal (e.g., shorter dividend streak) |
| ⚠ Flagged | 90-day trend broken (e.g., tariff-driven selloff); re-evaluate after earnings |

## Trend Key

| Symbol | Meaning |
|--------|---------|
| ⬆ Uptrend | Clear upward price trend over the specified period |
| ↗ Moderate | Upward but pace has slowed or shows choppiness |
| ↔ Mixed | Direction unclear; near-term concern vs. long-term trend |
| ⚠ Flagged | Recent significant decline broke the uptrend |

---

## How It Works

1. Click **Run Screen** — the app fetches live data from Yahoo Finance (no API key needed)
2. Batch quote calls retrieve current price, dividend yield, and sector for all tickers
3. Per-stock chart data (5-year weekly prices + dividend events) determines both price trends and dividend streak
4. Per-stock `financialData` determines YoY revenue growth
5. All four criteria are applied programmatically; status is computed automatically
6. Results are cached in `localStorage` for 24 hours — a stale-data banner appears when the cache is old

## Features

- **Live data** — fetches directly from Yahoo Finance, no API key, no backend
- **~100 S&P 500 dividend stocks** screened dynamically
- **Streams results** as each stock finishes — no waiting for all 100 to complete
- **Filter** by status, sector, minimum yield, and criteria pass count
- **Search** by ticker or company name
- **Sort** any column ascending or descending
- **Color-coded** sector badges, trend indicators, status pills, and yield values
- **Per-row criteria dots** (●●●●) showing which of the 4 criteria each stock passes
- **Auto-generated detail notes** with actual % figures (e.g. `5yr: +142% · 90d: +8.2% · Rev: +6.1% YoY`)
- **24-hour localStorage cache** with version invalidation
- Zero dependencies — pure HTML, CSS, and vanilla JavaScript

---

## Sector Coverage

| Color | Sectors |
|-------|---------|
| 🔵 Blue | Technology, Semiconductors |
| 🟢 Green | Healthcare |
| 🟡 Yellow | Consumer Staples |
| 🟠 Orange | Energy, Midstream |
| 🟣 Purple | Financials, Insurance, Banking, Asset Management |

---

## Ticker Universe (~100 S&P 500 Dividend Stocks)

The screener evaluates these tickers on every run. Results vary by date based on live data.

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

### View locally
```bash
# Clone the repo
git clone https://github.com/dblasing/sp500screener.git
cd sp500screener

# Open directly in your browser
open index.html

# Or serve it locally
python3 -m http.server 3456
# then visit http://localhost:3456
```

### Deploy to GitHub Pages
1. Go to **Settings → Pages** in this repo
2. Set Source to **Deploy from a branch**
3. Select **main** branch, **/ (root)** folder
4. Click **Save** — live at `https://dblasing.github.io/sp500screener` within ~1 minute

### Update the stock data
All stock data lives in the `STOCKS` array near the top of the `<script>` block in `index.html`. Each entry follows this shape:

```js
{
  ticker:     'XOM',
  company:    'ExxonMobil',
  sector:     'Energy',
  trend5:     'up',        // 'up' | 'moderate' | 'mixed' | 'flagged'
  trend90:    'up',        // 'up' | 'moderate' | 'mixed' | 'flagged'
  revenue:    'Positive',  // free-text description
  streakRaw:  '43 yrs',    // display string
  streakNum:  43,          // numeric (used for sorting; estimate if non-numeric)
  yieldRaw:   '~3.5%',     // display string
  yieldNum:   3.5,         // numeric (used for filtering/sorting)
  statusKey:  'meets',     // 'meets' | 'likely' | 'monitor' | 'border' | 'flagged'
  notes:      'Permian Basin driving volume growth; cleanest energy fit',
}
```

---

## Data Sources

- [Sure Dividend](https://www.suredividend.com)
- [Simply Safe Dividends](https://www.simplysafedividends.com)
- [Seeking Alpha](https://seekingalpha.com)
- [MarketBeat](https://www.marketbeat.com)
- [Macrotrends](https://www.macrotrends.net)
- Company investor relations pages

---

## Disclaimer

This screener is for **research and educational purposes only**. It is not investment advice. Dividend yields and revenue figures are approximate as of April 2026. The 90-day trend assessment is qualitative. Verify all data independently before making any investment decisions.

---

## License

MIT — free to use, fork, and adapt.
