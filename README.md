# S&P 500 Dividend Growth Stock Screener

An interactive, single-file HTML screener that filters S&P 500 constituents against four dividend + price-trend criteria. No build tools, no dependencies, no backend — open `index.html` in any browser or host it on GitHub Pages.

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

## Features

- **Filter** by status, sector, and minimum dividend yield
- **Search** by ticker symbol or company name
- **Sort** any column ascending or descending
- **Color-coded** sector badges, trend indicators, status pills, and yield values
- **27 S&P 500 stocks** pre-screened as of April 2026
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

## Stocks Included (April 2026)

| Ticker | Company | Sector | Div Yield | Status |
|--------|---------|--------|-----------|--------|
| KMI | Kinder Morgan | Midstream | ~5.8% | ◎ Monitor |
| OKE | ONEOK | Midstream | ~4.8% | ~ Borderline |
| WMB | Williams Companies | Midstream | ~4.5% | ✔ Meets All |
| CVX | Chevron | Energy | ~4.2% | ✔ Meets All |
| ABBV | AbbVie | Healthcare | ~3.5% | ✔ Meets All |
| PEP | PepsiCo | Consumer Staples | ~3.5% | ◎ Monitor |
| XOM | ExxonMobil | Energy | ~3.5% | ✔ Meets All |
| JNJ | Johnson & Johnson | Healthcare | ~3.2% | ✔ Meets All |
| KO | Coca-Cola | Consumer Staples | ~3.1% | ✔ Meets All |
| COP | ConocoPhillips | Energy | ~3.1% | ~ Borderline |
| MRK | Merck | Healthcare | ~2.8% | ✔ Meets All |
| EOG | EOG Resources | Energy | ~2.8% | ✔ Meets All |
| BLK | BlackRock | Asset Management | ~2.8% | ✦ Likely |
| BAC | Bank of America | Banking | ~2.7% | ⚠ Flagged |
| PG | Procter & Gamble | Consumer Staples | ~2.5% | ◎ Monitor |
| CL | Colgate-Palmolive | Consumer Staples | ~2.4% | ✔ Meets All |
| JPM | JPMorgan Chase | Banking | ~2.4% | ⚠ Flagged |
| ADP | Automatic Data Processing | Technology | ~2.3% | ✔ Meets All |
| AFL | Aflac | Insurance | ~2.2% | ✔ Meets All |
| ABT | Abbott Laboratories | Healthcare | ~1.8% | ✔ Meets All |
| CB | Chubb | Insurance | ~1.4% | ✔ Meets All |
| AVGO | Broadcom | Semiconductors | ~1.2% | ✔ Meets All |
| ZTS | Zoetis | Healthcare | ~1.2% | ✔ Meets All |
| WMT | Walmart | Consumer Staples | ~1.0% | ✔ Meets All |
| MSCI | MSCI Inc. | Financials | ~0.9% | ✔ Meets All |
| MSFT | Microsoft | Technology | ~0.8% | ✔ Meets All |
| INTU | Intuit | Technology | ~0.6% | ✔ Meets All |

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
