---
name: belief-journal
description: Use when the user forms a specific belief, prediction, thesis, or forecast and wants it captured on a permanent, dated, falsifiable record structured as a full investment memo — recommendation, business overview, thesis, catalyst, valuation, risks and mitigants, market view — plus the conviction level and falsification criteria a memo normally omits. Triggers include "log this belief," "write this up," "note my conviction on X," "I want this on the record," "remember that I said X would happen," or a hand-off from thesis-validation, initiating-coverage, or thematic-mapping once a thesis is ready to commit. Do not use to review or grade past entries (use belief-retrospective), to see the current mutable status of an active thesis (use thesis-tracker), or to edit a previously logged belief — view changes are logged as a new dated entry that supersedes the old one, never as an edit to it.
---

# Belief Journal

## Purpose

Capture a single belief at the moment it's held — what is believed, when, why,
and how strongly — in a form specific enough to be checked later without
argument. Once written, an entry is never edited. If a view changes, that
becomes a new entry, not a correction to the old one.

The entry is structured as a standard equity investment memo, because that
skeleton already exists as a discipline tool: investors across otherwise
incompatible styles use memo writing to force clarity and create a record to
check against later, more than to sell a position. This skill takes that
practice literally. The memo sections do the work of making the reasoning
explicit; the journal adds the three things a memo leaves out — a stated
conviction level, explicit falsification criteria, and a check-by date — so
the record can actually be graded rather than just re-read.

The whole entry answers one question: *why this, at this price, right now* —
and then commits to what would prove that answer wrong.

Entries produced here are the raw material for `belief-retrospective`, which
reads the journal later and grades it against what actually happened. A
belief that can't eventually be checked against reality doesn't belong in
this journal.

## When to use this skill

- The user states a specific prediction, thesis, or strong view and wants it
  written up and on a permanent record.
- A thesis has survived `thesis-validation`, or a name has come out of
  `initiating-coverage` or `thematic-mapping`, and the user wants to commit it
  to the historical ledger rather than just the live tracker.
- The user's conviction on an existing topic has changed and they want that
  shift on the record — this produces a new entry, not a revision.
- The user wants to make a non-investment prediction accountable — a hiring
  call, a product bet, a forecast about a market or a decision. Sections that
  don't apply are marked `n/a`, not force-fitted.

## When NOT to use this skill

- **Reviewing or grading past entries** against outcomes -> `belief-retrospective`.
- **Seeing the current, editable status** of an active thesis -> `thesis-tracker`.
- **Decomposing a theme into candidates** before a thesis exists ->
  `thematic-mapping`.
- **Stress-testing a thesis for holes** before it's ready to log ->
  `thesis-validation` (run first; log what survives).
- The user wants a document optimized to persuade an allocator or investment
  committee. This entry shares the memo's skeleton but not its goal — it is
  written to be checked, not to win a vote, and the two diverge wherever
  honest uncertainty would weaken a pitch.
- The user wants to change what a past entry says, for any reason, including
  "I explained it badly" — that's a new entry with `supersedes` set, never an
  edit to the old one.

## Workflow

Sections 1-7 follow the standard memo sequence. Sections 8-10 are the journal
layer. Work through them in order; each has a failure mode worth guarding
against, noted inline.

### 1. Recommendation

One sentence: the subject, the price or level at which the view is taken, the
direction (buy/sell/short/hold, or the non-financial equivalent), and the core
reason. If it takes more than one sentence, the belief isn't yet clear enough
to log — keep compressing until it fits.

### 2. Business overview

What the subject does and how it makes money, written *for this decision* —
only the parts of the business the thesis actually depends on. A general
company summary is a sign this section is being padded. Two to five sentences
is usually right.

### 3. Investment thesis

Two to four specific reasons the market is currently wrong. Each should be a
claim about a fact or a mechanism, not an adjective — "management is good"
isn't a thesis point; "the reinvestment rate has run above the peer group for
six straight years and guidance implies that continues" is. Number them, so
`belief-retrospective` can later report which specific leg broke.

### 4. Catalyst

The specific reason the mispricing closes now rather than persisting. Set
`horizon_type` to match one of two honest answers:

- **`dated`** — a real event resolves this: an outside date, an earnings
  report, a ruling, a launch, a contract renewal. Record the event and its
  date.
- **`open-ended`** — there is no catalyst, and the honest answer to "why now"
  is "it's right and I'm willing to wait." Record that as the answer. Do not
  invent a catalyst to fill the section — a fabricated "why now" imports
  trading logic into a patience thesis and hands the retrospective a fake
  deadline to grade against. Set a review cadence instead (e.g., every six
  months).

### 5. Valuation

A target and the explicit methodology behind it — DCF, comps, sum-of-parts —
with implied upside and downside. Two allowances:

- Where the outcome is **binary** (a deal closes or breaks; a ruling goes one
  way), record a probability-weighted set of outcomes rather than a single
  point target, with the odds stated: a point estimate hides the thing that
  actually matters. Where a market price implies different odds than the
  user's, record both — the gap is the position.
- Where the belief is **non-financial**, state the success threshold in
  whatever unit applies and mark methodology `n/a`.

### 6. Risks and mitigants

The two or three strongest reasons the thesis could be wrong, each paired
with what offsets it. Two rules make this section a record rather than
reassurance:

- **Write the risks as the strongest critic of this belief would write them**,
  not as their author would. If every risk listed is one the user already
  feels comfortable with, the section is doing nothing.
- **Every mitigant is itself a claim, and gets recorded as one.** In a memo a
  mitigant ends the conversation; here it becomes a second thing the
  retrospective can check. "Regulatory risk, but the divestiture package
  covers it" is logged so that if the deal breaks on regulatory grounds, the
  record shows the mitigant was the thing that failed. A mitigant that can't
  be stated as a checkable claim isn't a mitigant — drop it and let the risk
  stand unoffset.

Where downside is **asymmetric or open-ended** — shorts, deal breaks that
trade through the pre-announcement price, anything with squeeze or financing
risk — say so explicitly here. "Reverts to the prior level" is not the worst
case for these, and recording it as though it were will make the eventual
retrospective grade against the wrong bar.

### 7. Market view

How this differs from consensus and why it isn't already priced in. The
honest answer is sometimes that it *is* consensus — in hard-catalyst
situations everyone can see the same announced event, and the edge sits in
timeline, legal, or process analysis rather than in a differentiated view of
value. Record that when it's true. A manufactured variant perception is worse
than none, because it disguises where the belief is actually load-bearing.

### 8. Conviction

One of four fixed tiers. Ask the user which applies, or infer from their
language and confirm it back:

| Tier | Meaning |
|---|---|
| `low` | A lean. Would not be surprised to be wrong. |
| `medium` | More likely than not; real evidence behind it, but a plausible case exists on the other side. |
| `high` | Would be genuinely surprised to be wrong. The user has acted on this — sized a position, made a decision, changed a plan. |
| `very high` | Near-certainty. The user would stake something significant — money, a decision, a reputation — on it. |

Push back gently when the stated tier doesn't match the language used ("not
sure, but I guess high conviction" is probably medium). Conviction is
distinct from any probability stated in section 5: a `medium`-conviction 80%
and a `very high`-conviction 80% are different beliefs, and only the record
keeps them apart. Keeping this scale stable across entries is what makes
calibration scoring in `belief-retrospective` mean anything.

### 9. Falsification criteria

Distinct from section 6. Risks are what could go wrong; falsification
criteria are the **specific observations that would make the user admit they
were wrong** — a number, a date, an event, a threshold. Ask directly and
reject answers that merely negate the claim ("if it doesn't work out").

List the criteria for each numbered thesis leg where they differ, so a
partial break is recordable as a partial break. If the user can't produce a
real criterion after a reasonable attempt, set `falsification_criteria:
unspecified` rather than fabricating one — a fabricated criterion is worse
than an honest gap, because it will silently mislead the retrospective.

### 10. Context, provenance, and write

Record what was known and available at the moment of writing — the filing,
the transcript, the price, the conversation that prompted this. This is what
later lets a retrospective separate "the user missed available information"
from "that information didn't exist yet."

Then check for a prior entry on the same topic; if one exists, set
`supersedes` to its id and leave that file untouched. Copy
`assets/belief-template.md`, assign an id (`YYYY-MM-DD-<slug>`), write to
`beliefs/`, and confirm back: the recommendation line, the conviction tier,
and the check-by date. If anything was logged as unspecified or `n/a`, say so
plainly rather than letting the confirmation imply a cleaner entry than what
was captured.

## Output schema

### Frontmatter

| Field | Description |
|---|---|
| `id` | `YYYY-MM-DD-<slug>`, unique |
| `date_logged` | Date written — never changes |
| `topic` | Short subject line (ticker, theme, decision) |
| `direction` | `long` / `short` / `hold` / `n/a` |
| `entry_price` | Price or level at which the view is taken, if applicable |
| `conviction` | `low` / `medium` / `high` / `very high` |
| `horizon_type` | `dated` / `open-ended` |
| `horizon` | Resolving event and date, or review cadence |
| `check_by` | Date `belief-retrospective` should surface this |
| `status` | `open` / `confirmed` / `falsified` / `inconclusive` / `superseded` — the only field `belief-retrospective` may update |
| `supersedes` | Optional id of the entry this one replaces |
| `tags` | Optional, free-form |

### Body sections

| # | Section | Content |
|---|---|---|
| 1 | Recommendation | One sentence: subject, price, direction, core reason |
| 2 | Business overview | How it makes money, only as it bears on this decision |
| 3 | Investment thesis | 2-4 numbered reasons the market is wrong |
| 4 | Catalyst | Dated event, or an explicit "no catalyst, willing to wait" |
| 5 | Valuation | Target + methodology + implied upside/downside; probability-weighted where binary |
| 6 | Risks and mitigants | 2-3 strongest counter-cases, each mitigant stated as a checkable claim; asymmetric downside flagged |
| 7 | Market view | Why not already priced in — or an honest note that the edge is process, not variance |
| 8 | Conviction | Tier, with a one-line justification |
| 9 | Falsification criteria | Observable conditions that would prove it wrong, per thesis leg where they differ |
| 10 | Context at time of writing | Sources, data, and price available when logged |

Checkpoints are appended later by `belief-retrospective` as new sections at
the bottom of the file. This skill never writes them and never edits anything
above them once saved.

## Example

**User:** "Log my view on the transformer manufacturer from the grid theme.
I'm long at 64, high conviction — the backlog converts faster than the Street
models it."

**Logged entry (abridged):**

```
id: 2026-07-22-transformer-backlog-conversion
direction: long
entry_price: 64.00
conviction: high
horizon_type: dated
horizon: 2027-01-31 (two reported quarters)
check_by: 2026-10-31 (after next earnings)
status: open
```

**1. Recommendation** — Long at $64; the market is modelling backlog-to-revenue
conversion off a capacity base that management has already expanded past.

**2. Business overview** — Designs and manufactures large power transformers
sold on multi-year contracts to utilities and data-center developers. Revenue
recognizes on delivery, so reported revenue is gated by production capacity,
not by order intake — which is why the backlog and the capacity line matter
more here than demand commentary does.

**3. Investment thesis**
1. Backlog has grown faster than the production-capacity guidance the Street
   is modelling conversion against.
2. The capacity expansion referenced on the last call is further along than
   sell-side models reflect — no published model has updated for it.
3. Pricing on new backlog is struck above the legacy book, so conversion
   lifts margin as well as revenue.

**4. Catalyst** — Next two earnings reports (next: 2026-10-28). Conversion rate
becomes observable in reported revenue against the disclosed backlog figure.

**5. Valuation** — $82 target, comps-based: 14x forward EBITDA against a peer
set at 12-16x, applied to FY27 estimates adjusted for the higher conversion
rate. Implied upside 28%. Downside to $55 (-14%) on a return to consensus
conversion assumptions at the peer-median multiple.

**6. Risks and mitigants**
- *Input supply.* Transformer-grade steel is the binding input; a supply
  disruption caps conversion regardless of capacity. **Mitigant, as a
  checkable claim:** supply is contracted through FY27 at fixed volume — so
  if conversion misses on input constraints before FY28, this mitigant was
  the thing that failed.
- *Already priced.* The capacity expansion may be understood by holders even
  if unmodelled. **Mitigant, as a checkable claim:** no published sell-side
  model has revised capacity assumptions post-call; if revisions appear
  before the print and the stock doesn't move on them, this was priced.
- *Utility capex deferral.* Orders can be pushed rather than cancelled,
  deferring conversion without showing up as backlog decline. No credible
  mitigant — this risk stands unoffset.

**7. Market view** — Consensus treats the backlog as a demand signal and models
conversion off historical throughput. The variant view is narrow and
mechanical: it's a claim about capacity, not about demand. If capacity is
already correctly modelled by others, there is no thesis left — the demand
story alone is consensus.

**8. Conviction** — `high`. Position sized on it; would be surprised to be
wrong on the capacity point specifically, less so on timing within the
two-quarter window.

**9. Falsification criteria**
- Leg 1/2: either of the next two quarters converts backlog at or below the
  trailing three-year average rate.
- Leg 2: management walks back or delays the capacity-expansion timeline on
  any call before FY27.
- Leg 3: incremental gross margin comes in flat or down against the prior
  year despite revenue growth.
- Whole thesis: revenue misses consensus by more than 2% in either of the
  next two quarters.

**10. Context at time of writing** — Q2 transcript and the backlog figure
disclosed that quarter; no sell-side revisions published since; $64.00 close
on the logging date; steel supply contract terms per the last 10-K.

**Flex points shown by other entry types:** a merger-arb entry replaces
section 5's point target with probability-weighted close/break outcomes and
the odds implied by the current spread; a long-horizon compounder entry sets
`horizon_type: open-ended` and records "no catalyst — willing to wait" in
section 4 rather than manufacturing one; a non-financial entry (a hiring
call, a product bet) marks sections 2 and 5 `n/a` and carries the weight in
sections 3, 6, and 9.

## Limitations

- This skill does not evaluate whether the belief is *correct* — only that
  it's captured cleanly enough to be checked later.
- The memo skeleton is borrowed for its clarity-forcing properties, not its
  persuasive ones. It rewards confident, linear narratives, and that pressure
  doesn't disappear just because the audience is the author — sections 6, 7,
  and 9 exist to push against it, and they only work if written adversarially
  rather than filled in.
- A single outcome cannot falsify a probability-weighted claim: an 80% call
  that breaks was not automatically wrong. Individual entries record what
  happened; whether stated odds mean anything emerges only across many
  entries, in `belief-retrospective`'s calibration scoring.
- The conviction scale is only meaningful if used consistently by one person
  over time. A tier that drifts in meaning silently breaks calibration.
- Sections marked `n/a` are fine; sections filled with padding to look
  complete are not, and are harder to detect later.
- This is a historical ledger, not a dashboard. For the current best view on
  an active thesis, use `thesis-tracker` — this skill records what was
  thought on a given date, not what to think today.