# Piotroski F-Score

Source: Joseph Piotroski, "Value Investing: The Use of Historical
Financial Statement Information to Separate Winners from Losers"
(*Journal of Accounting Research*, 2000). Nine binary tests of
fundamental health, one point each, summed to a 0-9 score. An
**absolute** screen computed from two consecutive fiscal years (plus one
earlier balance sheet — see data requirements).

Piotroski designed the score to separate improving from deteriorating
companies *within a universe of high book-to-market (cheap) stocks*.
That context matters for interpretation — see below.

## The nine tests

Year `t` is the most recent fiscal year; `t-1` the prior; `t-2` the one
before that (balance sheet only).

### Profitability (4 points)

| # | Test | Point if |
|---|---|---|
| 1 | ROA positive | `net_income(t) / total_assets(t-1) > 0` |
| 2 | Operating cash flow positive | `cfo(t) > 0` |
| 3 | ROA improving | `ROA(t) > ROA(t-1)` where `ROA(t-1) = net_income(t-1) / total_assets(t-2)` |
| 4 | Accrual quality | `cfo(t) > net_income(t)` |

Test 4 is the earnings-quality check: profits backed by cash rather
than accruals.

### Leverage, liquidity, dilution (3 points)

| # | Test | Point if |
|---|---|---|
| 5 | Leverage decreasing | `long_term_debt(t) / avg_assets(t) <= long_term_debt(t-1) / avg_assets(t-1)` |
| 6 | Liquidity improving | `current_ratio(t) > current_ratio(t-1)` |
| 7 | No dilution | `shares_outstanding(t) <= shares_outstanding(t-1)` |

`avg_assets(t) = (total_assets(t) + total_assets(t-1)) / 2`. Test 7
awards the point for flat or shrinking share count; buybacks are fine,
issuance is not.

### Operating efficiency (2 points)

| # | Test | Point if |
|---|---|---|
| 8 | Gross margin improving | `gross_profit(t)/revenue(t) > gross_profit(t-1)/revenue(t-1)` |
| 9 | Asset turnover improving | `revenue(t)/total_assets(t-1) > revenue(t-1)/total_assets(t-2)` |

## Why three years of balance-sheet data

Piotroski's ROA and asset-turnover definitions use **beginning-of-year**
total assets. Computing the year-over-year change in those ratios
therefore requires total assets at `t-2`. This is the original paper's
definition, not a simplification. If only two years are available, the
score cannot be computed faithfully — report it as incomplete rather
than silently switching to end-of-year assets.

## Data requirements

The script takes `company.years`: a list of at least 3 annual dicts,
**oldest first**. Each year dict:

| Field | Statement |
|---|---|
| `net_income` | Income statement |
| `cfo` | Cash flow statement (operating activities) |
| `total_assets` | Balance sheet |
| `long_term_debt` | Balance sheet |
| `current_assets`, `current_liabilities` | Balance sheet |
| `gross_profit`, `revenue` | Income statement |
| `shares_outstanding` | Cover page / balance sheet |

The `t-2` year only needs `total_assets` for the score itself, but
providing the full dict costs nothing and future-proofs the input.

## Interpretation

- **8-9**: strong fundamentals in Piotroski's framework
- **0-2**: weak — the deteriorating cohort his paper found underperforms
- **3-7**: middle — the score offers little signal here

Two caveats the report must carry:

1. The published performance results come from applying the score to
   **already-cheap (high book-to-market) stocks**. An F-Score of 9 on an
   expensive growth stock is outside the tested regime — the score says
   the fundamentals improved, not that the stock is a value candidate.
   Pairing the F-Score with a valuation screen (Graham criterion 7, or
   the Magic Formula's earnings yield) restores the original context.
2. If any test lacks data, report the score as a **range** (earned
   points to earned-points-plus-missing), never as a point estimate.
   The script does this automatically in the `band` field.
