# Graham NCAV ("Net-Net") Screen

Source: Benjamin Graham, *Security Analysis* (1934) and *The Intelligent
Investor*. A single **absolute** criterion: is the stock priced below
two-thirds of its net current asset value — a rough proxy for
liquidation value that gives fixed assets a value of zero?

## The test

```
NCAV            = current_assets - total_liabilities - preferred_stock
NCAV_per_share  = NCAV / shares_outstanding

Qualifies if:  price <= (2/3) x NCAV_per_share
```

Notes on the formula:

- **Total liabilities**, not just debt — every claim senior to common
  equity comes out, including deferred taxes, pension obligations, and
  operating lease liabilities as reported.
- **Preferred stock** is subtracted at its balance-sheet carrying value
  (liquidation preference if disclosed and materially different).
- Fixed assets, goodwill, and all other non-current assets are valued
  at **zero**. That severity is the point: the screen asks whether the
  business is priced below what its most liquid assets would fetch
  after paying everyone off.
- The one-third discount to NCAV is Graham's margin of safety against
  the current assets themselves being worth less than book (stale
  inventory, uncollectible receivables).

## The cash-burn advisory flag

The raw NCAV test is a snapshot. A company burning cash every year is
consuming the asset value the screen is based on — the classic
"melting ice cube." If `cfo_history` (annual operating cash flow, oldest
first, at least 2 values) is provided, the script adds an advisory flag
that trips when every recent year's operating cash flow is negative.

The flag **does not change the pass/fail verdict** — a company can pass
the NCAV test while flagged. Report both. A flagged pass means the
discount must be large enough to outrun the burn rate, which is a
judgment call outside this skill's scope.

## Data requirements

| Script field | Statement | Notes |
|---|---|---|
| `current_assets` | Balance sheet | Most recent quarter preferred — net-nets decay fast |
| `total_liabilities` | Balance sheet | All liabilities, not just debt |
| `preferred_stock` | Balance sheet | 0 if none |
| `shares_outstanding` | Cover page / balance sheet | Latest reported |
| `price` | Market | As-of date stated in report |
| `cfo_history` | Cash flow statement | Optional; enables the cash-burn flag |

## Interpretation

- Net-nets are, by construction, companies the market has priced for
  serious trouble. A pass identifies a statistical bargain in Graham's
  sense, **not** a healthy business.
- Graham ran net-nets as a **basket strategy** — dozens of positions,
  expecting individual failures. A single passing name is a candidate
  for a basket, not a concentrated position.
- Qualifying net-nets are rare in large-cap developed markets outside of
  broad selloffs. Finding zero passes in a normal market is the expected
  result, not a screen malfunction — say so rather than loosening the
  threshold to force a hit.
- NCAV uses balance-sheet carrying values. Off-balance-sheet
  liabilities, pending litigation, or restricted cash can make a
  "pass" illusory; note any such items visible in the data source.
