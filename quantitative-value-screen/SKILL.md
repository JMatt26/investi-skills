---
name: quantitative-value-screen
description: Use when the user wants to run a mechanical, published value-investing screen on a company or list of tickers - Graham's Defensive Investor criteria, Graham NCAV/net-net, the Piotroski F-Score, or the Greenblatt Magic Formula. Triggers include "run a value screen on X," "does X pass the Graham criteria," "what's X's F-Score / Piotroski score," "is X a net-net," "rank these on the Magic Formula," or any request to check a stock against Graham, Piotroski, or Greenblatt's published criteria, even if the user just says "screen this stock" or "is this a value stock by the numbers." Do not use for qualitative competitive-advantage analysis (use moat-assessment), for DCF or intrinsic-value estimation (use intrinsic-value-estimate), for general peer benchmarking on multiples with no named methodology (use comparable-companies), or for finding candidate names from a theme (use thematic-mapping).
---

# Quantitative Value Screen

## Purpose

Apply published, mechanical value-investing screens exactly as their
authors specified them: numbers in, pass/fail (or score, or rank) out,
with zero judgment calls inside the screen itself. This skill exists to
prevent the two ways screening usually goes wrong: **vibes-based
application** ("this feels like a Graham stock") and **silent arithmetic
drift** (misremembered thresholds, hand-computed multi-year deltas,
criteria quietly skipped when data is missing).

Every screen here is a candidate filter, not a verdict. A pass earns a
company deeper work in `moat-assessment` or `intrinsic-value-estimate`;
it never by itself justifies a position.

## The four screens

| Screen | Nature | Question it answers | Reference |
|---|---|---|---|
| Graham Defensive Investor | Absolute, 7 criteria | Does this company meet Graham's conservative eligibility bar? | `references/graham-defensive.md` |
| Graham NCAV (net-net) | Absolute, 1 criterion | Is this priced below 2/3 of liquidation-proxy value? | `references/graham-ncav.md` |
| Piotroski F-Score | Absolute, 9 binary tests | Are the fundamentals improving or deteriorating? | `references/piotroski-fscore.md` |
| Greenblatt Magic Formula | **Relative**, peer ranking | Which of these names best combines cheap and good? | `references/magic-formula.md` |

Read the reference file for each screen being run before sourcing data —
it lists the exact input fields, the formula definitions, and the
interpretation caveats the final report must carry.

## When to use this skill

- The user names one of the four screens, their author, or an
  unambiguous alias ("net-net," "F-Score," "Magic Formula").
- The user asks for "a value screen" generically — default to Graham
  Defensive Investor, **say so explicitly**, and offer the others.
- A name surfaced by `thematic-mapping` or under review in
  `initiating-coverage` needs a mechanical value check.

## When NOT to use this skill

- **Qualitative competitive analysis** (pricing power, switching costs,
  moat trend) -> `moat-assessment`
- **Valuing the business** (DCF, owner earnings, margin of safety vs.
  intrinsic value) -> `intrinsic-value-estimate`
- **Peer benchmarking on multiples** with no named screen methodology ->
  `comparable-companies`. The Magic Formula overlaps with this: if the
  user wants Greenblatt's specific EY + ROC ranking, it lives here; if
  they just want names compared on P/E, EV/EBITDA, etc., hand off.
- **"Act like Buffett/Graham"** persona requests — offer the mechanical
  screens instead and explain the difference: this skill encodes their
  published algorithms, not their voice or their un-codified judgment.
- The company is a **bank, insurer, or utility** and the user wants
  Graham Defensive, NCAV, or Magic Formula — these screens' formulas
  don't map onto those capital structures. Piotroski is the least
  distorted, but flag the caveat. See per-screen references.

## Workflow

### 1. Pin down screen(s), subject, and parameters

Establish which screen(s) to run and on what. Two structural rules:

- The Magic Formula needs a **universe** (multiple companies the user
  specifies or agrees to). Never run it on one ticker; never invent a
  peer set silently — propose one and get confirmation, since the
  ranking is only meaningful relative to the universe chosen.
- The other three run on a **single company** each (loop over a list if
  given one).

Surface any non-default parameters now: the Graham size threshold
(default $800M, inflation-adjusted from Graham's $100M/1970) and the
dividend lookback (default 10 years vs. Graham's original 20). Defaults
are fine unstated preferences; changed parameters go in the report
header.

### 2. Source the data — never fabricate it

Read the relevant reference file(s) for the exact field list, then
gather real reported figures:

- **Prefer a connected financial-data tool** (e.g. a fundamentals MCP
  connector) — search available tools before asking the user to paste
  numbers.
- Otherwise use filings/web data or user-provided figures.
- Record, for the report header: fiscal periods used, the price
  observation date, and the source of every number.
- Keep all monetary values in **one currency and one unit** (all
  absolute, not "millions" for some fields).
- A field that cannot be sourced stays missing. The calculator reports
  it as `insufficient_data`; that is the correct outcome. Never estimate
  a line item to make a criterion computable.

### 3. Compute with the script, not by hand

Build the input JSON (schema documented in the script's docstring and
each reference file) and run:

```
python scripts/screen_calculator.py input.json --pretty
```

The script returns per-criterion values, thresholds, and results, plus a
summary per screen. Do not re-derive any figure the script computed, and
do not compute screen arithmetic manually even for "obvious" cases —
the multi-year deltas (F-Score) and two-part tests (Graham criterion 7)
are exactly where hand arithmetic drifts. Histories are **oldest
first**; the F-Score needs three years of data (the reference explains
why).

Each criterion returns one of four states: `pass`, `fail`,
`insufficient_data`, or `determinable_fail` (a fail reached from partial
data, because the sourced values already violate the rule no matter what
the missing inputs are — see `references/graham-defensive.md`). The key
discipline: **if a criterion returns `insufficient_data`, do not override
it with your own reasoning that it "obviously" fails.** The calculator
already emits `determinable_fail` for every case where partial data
settles the question; anything it left as `insufficient_data` is
genuinely undetermined. Hand-reasoning a fail in prose next to the
script's output is the exact drift this skill exists to prevent.

### 4. Assemble the report

Copy `assets/output-template.md` and fill it in. Non-negotiable
elements:

- Data-as-of dates and sources in the header
- The per-criterion table(s), not just verdicts — a fail on the
  valuation test is different information than a fail on earnings
  stability
- A **data gaps** section listing every `insufficient_data` item and the
  specific missing field. An incomplete screen is reported as
  incomplete, never rounded to a pass; an incomplete F-Score is a range,
  never a point score.
- The interpretation caveats **that apply to this run**, drawn from the
  reference files (e.g. F-Score used outside a cheap-stock universe,
  a sub-10-name Magic Formula universe, a cash-burn-flagged net-net).
  Only the applicable ones — a caveat section that fires on everything
  informs on nothing.

### 5. Flag hand-offs

- **Pass / strong score** -> `moat-assessment` (is the business durable?)
  then `intrinsic-value-estimate` (what is it worth?). A screen pass is
  the *start* of that chain.
- **Fail** -> state the disqualifying criterion and stop. Do not shop
  the company across screens until one passes — passing NCAV after
  failing Graham Defensive is not redemption, it's a different question.
  Running multiple screens is fine when asked upfront; sequential
  retries to manufacture a pass are not.
- **Incomplete** -> state exactly which fields would complete it.
- **Magic Formula output** -> the top-ranked names are candidates for
  the single-company screens or `initiating-coverage`; the ranking
  itself is not a buy list.

## Example

**Request:** "Does Acme Industrial pass the Graham defensive criteria?
Also give me its F-Score."

**Flow:** Read `references/graham-defensive.md` and
`references/piotroski-fscore.md` -> pull FY data from the connected
fundamentals tool (10 years of EPS and dividends; 3 years of full
statements for the F-Score; current price) -> build `input.json` with
`"screens": ["graham_defensive", "fscore"]` -> run the calculator ->
report shows 6/7 Graham criteria passing with a fail on criterion 7
(P/E x P/B = 31.4 vs. 22.5 ceiling) and an F-Score of 7/9 (missed on
gross margin and dilution).

**Report conclusion:** "Acme fails the defensive screen on valuation
alone — the business criteria all pass, but at the current price the
combined multiplier is 40% above Graham's ceiling. F-Score of 7
indicates improving fundamentals. If the thesis is 'good business,
wrong price,' the next step is `intrinsic-value-estimate` to establish
what price would change the answer — not re-running screens until one
passes."

## Limitations

- **Thresholds are era-calibrated.** Graham's numbers assume 1970s U.S.
  accounting and market structure. The size threshold is
  inflation-adjusted by default, but the deeper issue — e.g. asset-light
  businesses that fail book-value tests while being genuinely cheap —
  is a known blind spot of the methodology, not a bug to patch silently.
- **Sector applicability is narrow.** Financials, REITs, and utilities
  break most of these formulas. The script exempts what Graham exempted
  and the references explain the substitutions; forcing the standard
  formulas onto these sectors produces confident nonsense.
- **A pass is a candidate, not a buy signal.** Nothing here assesses
  moat, management, fraud risk beyond Piotroski's narrow accrual test,
  or price versus intrinsic value beyond Graham's crude multiples.
- **Point-in-time data quality is the binding constraint.** Restated
  financials, non-standard fiscal years, and ADR share-count confusion
  corrupt results silently. The screens are only as good as the reported
  figures fed in; the report's source documentation exists so errors
  can be traced.
- **Backtested performance does not transfer automatically.** The
  F-Score and Magic Formula results were demonstrated on specific
  universes with specific rebalancing rules; applying them to a
  hand-picked handful of tickers is a research aid, not a replication
  of the published strategy.