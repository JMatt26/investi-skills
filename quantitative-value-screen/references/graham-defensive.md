# Graham Defensive Investor Screen

Source: Benjamin Graham, *The Intelligent Investor* (1973 revised edition),
Chapter 14, "Stock Selection for the Defensive Investor." Seven criteria,
all of which must pass. This is an **absolute** screen: it evaluates one
company against fixed thresholds, not against peers.

## The seven criteria

### 1. Adequate size
```
revenue >= size_threshold
```
Graham's original figure was $100M in annual sales (1970 dollars),
intended to exclude small companies "subject to more than average
vicissitudes." Applied literally today it excludes almost nothing, so the
threshold must be inflation-adjusted. The script defaults to **$800M**
(roughly $100M in 1970 CPI-adjusted to the mid-2020s). Pass a different
value via `options.size_threshold` if the user wants Graham's original
number, a different base year, or a non-USD currency.

### 2. Strong current ratio
```
current_assets / current_liabilities >= 2.0
```
Applies to industrial companies only. Graham explicitly exempted
utilities (and by extension financials) because their working-capital
structure makes the ratio meaningless — for those, see the sector note
below. The script auto-skips this test when `sector_type` is `utility`
or `financial` and reports it as `insufficient_data` with an explanation.

### 3. Long-term debt covered by working capital
```
long_term_debt <= (current_assets - current_liabilities)
```
Also industrial-only. For utilities Graham substituted a capitalization
test: debt should not exceed twice equity (at book value). The script
does not compute the utility variant automatically; if screening a
utility, compute `long_term_debt <= 2 x total_equity` manually and
report it in place of this criterion, labeled as the utility variant.

### 4. Earnings stability
```
EPS > 0 in each of the last 10 fiscal years
```
Diluted EPS from continuing operations is the preferred series. One
negative year fails the test — no averaging, no exclusion of
"one-time" items unless the reported figure itself excludes them.

### 5. Dividend record
```
dividend paid in each of the last N years  (default N = 10)
```
Graham's original test was **20 years** of uninterrupted dividends.
Modern practitioners commonly relax this to 10 because 20 years excludes
nearly every company that IPO'd after the 2000s. The script defaults to
10 via `options.dividend_years_required`; state in the report which
lookback was used. Buybacks do not count as dividends under this test.

### 6. Earnings growth
```
avg(EPS years 8-10) / avg(EPS years 1-3) >= 1.33
```
At least one-third growth in per-share earnings over the decade, using
three-year averages at both endpoints to smooth single-year noise
(Graham's own method). If the starting three-year average is not
positive, the ratio is undefined and the test fails.

### 7. Moderate valuation (two-part test)
```
price / avg(EPS last 3 years) <= 15
AND
(P/E on 3-yr avg EPS) x (price / book_value_per_share) <= 22.5
```
The 22.5 product is Graham's combined multiplier: it permits a P/E above
15 or a P/B above 1.5 only if the other is proportionally lower (15 x
1.5 = 22.5). Use tangible book value if intangibles are a large share of
equity and the data is available; otherwise stated book value is
acceptable — say which was used.

## Data requirements

| Script field | Statement | Notes |
|---|---|---|
| `revenue` | Income statement | Most recent fiscal year |
| `current_assets`, `current_liabilities` | Balance sheet | Most recent |
| `long_term_debt` | Balance sheet | Exclude operating lease liabilities only if peer treatment is consistent |
| `eps_history` | Income statement | 10 annual values, **oldest first**, diluted |
| `dividend_history` | Cash flow / dividend record | Per-share amounts or booleans, oldest first |
| `price` | Market | Current or as-of date stated in report |
| `book_value_per_share` or `total_equity` + `shares_outstanding` | Balance sheet | Script derives BVPS if not given directly |
| `sector_type` | — | `industrial` (default), `utility`, or `financial` |

## Interpretation

- **7/7 pass** — the company qualifies as a defensive-investor candidate.
  This is an eligibility bar, not a buy signal.
- **Any fail** — the company does not qualify. Report which criterion
  failed and by how much; a near-miss on criterion 7 is different
  information than a 10-year earnings gap on criterion 4.
- **Any insufficient_data** — the verdict is incomplete. Never round an
  incomplete screen up to a pass.