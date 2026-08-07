# Greenblatt Magic Formula

Source: Joel Greenblatt, *The Little Book That Beats the Market* (2005).
Ranks a set of companies on the combination of two metrics — how cheap
the business is (earnings yield) and how good it is (return on
capital). This is the one **relative** screen in this skill: it produces
rankings, not pass/fail verdicts, and is meaningless for a single
ticker.

## The two metrics

### Earnings yield
```
earnings_yield = EBIT / enterprise_value
enterprise_value = market_cap + total_debt - cash
```
EBIT rather than net income makes companies with different capital
structures and tax situations comparable; enterprise value rather than
market cap prices the whole business including its debt.

### Return on capital
```
return_on_capital = EBIT / (max(net_working_capital, 0) + net_fixed_assets)
net_working_capital = current_assets - current_liabilities   (if not given directly)
net_fixed_assets    = net property, plant & equipment
```
The denominator is Greenblatt's "tangible capital employed" — the
capital actually required to run the business, excluding goodwill and
intangibles (which record what was *paid* for acquisitions, not what
the business *needs*).

Two implementation notes:

- Greenblatt's book description adjusts working capital to exclude
  excess cash and interest-bearing short-term debt. Those adjustments
  require line-item detail that is often unavailable; the script uses
  the plain `current_assets - current_liabilities` definition. State
  this in the report — it can modestly overstate capital (and understate
  ROC) for cash-rich companies.
- Negative working capital is floored at zero in the denominator. A
  negative-NWC business (e.g., one funded by customer float) would
  otherwise show a *smaller* capital base than fixed assets alone,
  inflating ROC in a way that double-counts the advantage.

## The ranking procedure

1. Rank all companies on earnings yield, descending (rank 1 = highest).
2. Rank all companies on return on capital, descending.
3. Sum the two ranks per company.
4. Final ranking: ascending by combined rank sum. Ties break toward the
   higher earnings yield, then alphabetically.

Companies missing either metric are **excluded from the ranking
entirely** (listed separately in the output), because a partial rank
would distort every other company's position.

## Universe requirements — read before running

The output is only as meaningful as the universe it ranks:

- **Minimum 2 companies**, but rankings over fewer than ~10 names carry
  little information. Greenblatt's own implementation ranks thousands.
- **Exclude financials and utilities.** Greenblatt excludes them because
  EBIT and tangible-capital definitions don't map onto their business
  models (a bank's "debt" is its raw material). Flag rather than
  silently rank them if the user includes one.
- **Comparable accounting.** Mixing currencies or fiscal-year
  conventions inside one universe corrupts the ranking. All monetary
  inputs must be in the same currency.
- Greenblatt also excluded very small companies and applied the formula
  as a 20-30 stock, annually-rebalanced portfolio strategy. A one-time
  ranking of a hand-picked universe is a research aid, not a replication
  of the published strategy — say so in the report.

## Data requirements (per company in `universe`)

| Field | Statement | Notes |
|---|---|---|
| `ticker` | — | Label |
| `ebit` | Income statement | Operating income; trailing twelve months preferred |
| `market_cap` or `price` + `shares_outstanding` | Market | Script derives market cap if needed |
| `total_debt` | Balance sheet | Short-term + long-term interest-bearing debt |
| `cash` | Balance sheet | Cash and equivalents (add short-term investments if clearly liquid) |
| `net_working_capital` or `current_assets` + `current_liabilities` | Balance sheet | Script derives NWC if needed |
| `net_fixed_assets` | Balance sheet | Net PP&E |

## Interpretation

- Rank 1 means "best combination of cheap and good **within this
  universe**" — nothing more. Change the universe, change the ranking.
- The two component ranks matter as much as the sum: a #1 built from
  extreme cheapness and mediocre ROC is a different situation than a
  balanced #1. Report all three columns.
- Overlap warning: if the user's real question is "rank these peers on
  valuation multiples" with no interest in the specific EY+ROC
  methodology, that is the `comparable-companies` skill's job, not this
  screen.
