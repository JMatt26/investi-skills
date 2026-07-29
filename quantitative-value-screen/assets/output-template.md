# Quantitative Value Screen: {TICKER or UNIVERSE NAME}

**Screens run:** {list}
**Data as of:** {fiscal period(s) used, e.g. FY2025 10-K + latest 10-Q}
**Price as of:** {date the market price was observed}
**Data source:** {where every number came from}
**Parameters:** {non-default options, e.g. size_threshold, dividend lookback — omit if all defaults}

---

## {Screen name} — {verdict / score / rank summary}

<!-- One section per screen run. Use the matching table shape below. -->

### Graham Defensive Investor

| # | Criterion | Value | Threshold | Result |
|---|---|---|---|---|
| 1 | Adequate size | | | |
| 2 | Current ratio | | >= 2.0 | |
| 3 | LT debt vs. working capital | | | |
| 4 | 10-year earnings stability | | EPS > 0 every year | |
| 5 | Dividend record ({N} yrs) | | paid every year | |
| 6 | 10-year EPS growth | | >= 33% | |
| 7 | Valuation (P/E, P/E x P/B) | | <= 15 and <= 22.5 | |

**Verdict:** {pass / fail on criterion N / incomplete — N criteria lack data}

### Graham NCAV

| Metric | Value |
|---|---|
| NCAV per share | |
| 2/3 x NCAV | |
| Current price | |
| Price / NCAV | |
| Cash-burn flag | {clear / FLAGGED / not assessed} |

**Verdict:** {pass / fail / incomplete}

### Piotroski F-Score

| # | Test | Detail | Point |
|---|---|---|---|
| 1 | ROA > 0 | | |
| 2 | CFO > 0 | | |
| 3 | ROA improving | | |
| 4 | CFO > net income | | |
| 5 | Leverage decreasing | | |
| 6 | Current ratio improving | | |
| 7 | No share issuance | | |
| 8 | Gross margin improving | | |
| 9 | Asset turnover improving | | |

**Score:** {N}/9 {or "between N and M — K tests lack data"} — {band}

### Magic Formula (universe of {N})

| Rank | Ticker | Earnings yield | EY rank | Return on capital | ROC rank | Combined |
|---|---|---|---|---|---|---|

Excluded for missing data: {tickers, or "none"}

---

## Data gaps

{Every criterion or company reported as insufficient_data, with the
specific missing field(s). Omit this section only if there were none.}

## Read-before-acting notes

{The interpretation caveats that apply to THIS run, drawn from the
relevant reference file(s) — e.g. F-Score computed outside a value
universe, a small Magic Formula universe, a flagged net-net, a
sector-exempted Graham criterion. Not boilerplate: only the ones that
apply.}

## Suggested next step

{Hand-off: moat-assessment / intrinsic-value-estimate for passes;
the disqualifying fact for fails; the exact missing data for
incompletes.}