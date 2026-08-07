---
name: belief-retrospective
description: Use when the user wants to review a body of past belief-journal entries rather than write a new one — grading what was believed against what actually happened, tracing how a view moved across superseded entries, and producing a dated report of where the book of beliefs currently stands. Triggers include "how has my view on X changed," "grade my past calls," "review my journal," "summarize my memos on X," "what did I get wrong," "am I calibrated," or a sweep of entries past their check_by date. Do not use to log a new belief or a changed view (use belief-journal — a changed view is a new entry, never an edit), to see the current editable status of one live thesis (use thesis-tracker), or to stress-test a thesis that has not yet been logged (use thesis-validation).
---

# Belief Retrospective

## Purpose

Turn a write-only journal into a reviewed one. `belief-journal` produces
dated, immutable entries; nothing in that skill ever looks back. This skill
is the read path: it takes a set of entries, checks them against what
actually happened, follows how the view moved from one entry to the next,
and returns a single report that answers three questions a researcher
reviewing a stack of old memos actually asks.

1. **Where does the view stand now?** Across every live entry in the set —
   the current position, its conviction, and where two open entries
   contradict each other.
2. **How did it get here?** The path each view took through its superseded
   entries, and *what moved it* each time — new evidence, or the price.
3. **Was the reasoning any good?** Graded per thesis leg and per mitigant,
   not just per outcome, because those come apart more often than they meet.

The third question is the one that makes the other two worth asking. An
outcome-only scorecard rewards being right, which the market already does.
This skill is built to separate being right from reasoning well, and to make
the gap between them visible over a run of entries.

## When to use this skill

- The user asks how their thinking on a topic has changed over time, or
  wants a stack of entries summarized into one current view.
- Entries have passed their `check_by` date and need grading.
- A thesis resolved — the deal closed, the quarter printed, the ruling
  landed — and the record needs to reflect it.
- The user asks whether their conviction tiers or stated probabilities mean
  anything, i.e. wants calibration.
- Periodic review: quarterly or annually across the whole journal, or across
  one tag.

## When NOT to use this skill

- **Logging a new belief, or a changed one** -> `belief-journal`. If the
  review causes the user to revise a view, that revision is a new entry
  written by that skill, not something recorded here.
- **The current, editable state of one active thesis** -> `thesis-tracker`.
- **Stress-testing a thesis before it's committed** -> `thesis-validation`.
- **A single entry that hasn't resolved and isn't due.** Grading early
  invites reading interim price action as evidence. Leave it `open`.
- The user wants a performance report — returns, attribution, position
  sizing. This skill grades *beliefs*, not a portfolio, and the two diverge
  wherever sizing and timing did work the thesis didn't.
- **Locating entries or filing the finished report** — hand off to
  `research-workspace`, which owns storage and lookup for every skill in
  this suite.

## What this skill may and may not write

Load-bearing, and the reason the journal is trustworthy at all:

- **Never edit anything above the checkpoint line.** Not frontmatter, not
  prose, not a typo, not a number that turned out wrong. The value of the
  record is that it cannot be improved after the fact.
- **May append** a `## Checkpoint — YYYY-MM-DD` section to the bottom of an
  entry file, using `assets/checkpoint-template.md`. Multiple checkpoints
  accumulate; a later one never rewrites an earlier one. Locate the entry's
  exact file via `research-workspace`'s `index_manager.py lookup <subject>`
  — don't assume a path. `belief-journal` files by subject and skill name,
  not by a flat guessable location.
- **May update exactly one frontmatter field:** `status`. This is the single
  mutation `belief-journal` delegates here. Once every checkpoint in a run
  is written, run `index_manager.py rebuild` so the index reflects the new
  statuses — the index is always derived from what's on disk, never trusted
  as accumulated state, so a status change that isn't followed by a rebuild
  is invisible to every other skill's lookups until the next one happens.
- **Writes the report** through `research-workspace`. Get the canonical path
  with `index_manager.py path`, add the required frontmatter
  (`artifact_type: retrospective`, `skill: belief-retrospective`, plus
  `subject`/`is_ticker` or a scope-descriptive slug — see step 7), then hand
  off to write and index it. The report is derived and disposable —
  regenerating it must never require touching an entry.

## Workflow

### 1. Define the review set

Ask what scope to review if it isn't clear: one topic and its chain, one
tag, a date range, everything due (`check_by` in the past, `status: open`),
or the whole journal. State the resolved scope back before starting — a
retrospective over an unstated set produces a scorecard nobody can reproduce.

Locate the entries in scope through `research-workspace` rather than
guessing paths. A single-topic scope is a direct lookup:

```
python3 scripts/index_manager.py lookup <subject> --root research
```

Broader scopes (a tag, a date range, "everything due," the whole journal)
cut across subjects, and the index doesn't filter on those fields — it
only knows subject, theme, skill, date, and status. For those, run
`index_manager.py list --root research` to enumerate every subject, then
open each subject's `belief-journal` artifacts to check the field the scope
actually filters on (`tags`, `date`, `check_by`). This is slower than
a direct lookup but still starts from the index rather than an unbounded
filesystem search.

Read every entry in scope in full. Section 3's numbered legs, section 6's
mitigants, and section 9's falsification criteria are the grading inputs;
partial reads produce outcome-only grading, which is the failure mode this
skill exists to avoid.

### 2. Reconstruct the chains

Follow `supersedes` backwards to build each chain of entries on one topic,
oldest to newest. The terminal entry is the live view; every earlier one is
history. An entry with no successor and `status: open` is live regardless of
age — flag it if its `check_by` has long passed, since a stale live view is
a finding in itself.

### 3. Source outcomes — never grade from memory

For each entry due for grading, establish what actually happened: the price
or level now versus `entry_price`, whether the catalyst in section 4
occurred and when, and whether any falsification criterion in section 9 was
met. Use available tools to source this.

If the outcome cannot be established, grade the entry `pending` and say
which fact was missing. A guess here corrupts every downstream number, and
unlike a missing fact it leaves no trace.

### 4. Grade the entry

Three separate gradings, in this order — legs, mitigants, then outcome. Read
`references/grading-rubric.md` for the fixed vocabularies and the decision
procedure before the first grading in a session.

- **Each numbered thesis leg**: `held` / `broke` / `unresolved` /
  `unfalsifiable-as-written`.
- **Each mitigant** from section 6: `untested` / `held` / `failed`. A
  mitigant is only tested if its risk actually materialized. `failed` is the
  diagnostic grade — it means the risk landed and the thing the user told
  themselves would absorb it didn't.
- **Outcome**: `confirmed` / `falsified` / `inconclusive` / `superseded`.

Grade against section 9 **as written**, not as reinterpreted. If a criterion
was met, the entry is `falsified` even where the position made money. If
section 9 was logged `unspecified`, the entry grades `inconclusive` and that
is recorded as a process failure, not smoothed over — an entry that cannot
be falsified was never really a belief.

Then cross-tabulate outcome against legs. This is the report's core finding
per entry:

| | All legs held | Some legs broke |
|---|---|---|
| **Confirmed** | Right for the right reasons | **Right for the wrong reasons** |
| **Falsified** | **Wrong for the right reasons** | Wrong for the wrong reasons |

The two bolded cells carry the information. *Right for the wrong reasons*
is the dangerous one — it pays out, feels like skill, and reinforces a
process that didn't work. Name it explicitly whenever it occurs.

### 5. Classify each change of view

For every link in every chain, compare the superseding entry to the one it
replaced and classify what moved: `refinement`, `reversal`,
`conviction-shift`, `horizon-driven`, or `price-driven`. Read
`references/view-change-taxonomy.md` for the classification test and the
delta fields to compare.

The one to apply carefully is `price-driven`: a view that changed after the
price moved, with no source in section 10 dated later than the prior entry.
That is reasoning written to fit a mark. It is a normal thing for a careful
person to do without noticing, so report it as an observation with the dates
and the delta shown, and let the user judge it — not as an accusation.

### 6. Compute calibration with the script

Do not compute hit rates or Brier scores by hand. Build the input JSON from
the gradings and run:

```bash
python scripts/calibration.py graded.json --pretty
```

The script returns hit rate by conviction tier, the reasoning cross-tab,
leg-break frequency by position, mitigant failure rate, probability
calibration, and change-classification counts. Any bucket below the minimum
sample size returns `insufficient_data` rather than a number. Report that
verbatim — do not fill the gap with a percentage carrying a caveat, because
the percentage is what gets remembered.

Read `references/calibration-methodology.md` for what each figure means and
the specific ways these numbers mislead.

### 7. Assemble the report, then append checkpoints

Assemble the report from `assets/retrospective-template.md`. Get its
canonical path from `research-workspace` before writing:

```
python3 scripts/index_manager.py path --skill belief-retrospective \
  --subject <subject> --date <YYYY-MM-DD> --slug retrospective --root research
```

A single-topic scope files under that topic's subject, same as any other
subject-centric artifact. A scope that spans multiple subjects (a tag
sweep, a date range, the whole journal) doesn't belong to any one of
them — file it the same way `quantitative-value-screen` files a Magic
Formula ranking: under a descriptive slug for the scope itself (e.g.
`fintech-unbundling-tag-sweep-2026-08`), with `is_ticker: false`, and list
the individual subjects covered in the report body rather than duplicating
the file across each one.

Add this frontmatter before writing:

| Field | Value |
|---|---|
| `artifact_type` | Always `retrospective` |
| `skill` | Always `belief-retrospective` |
| `id` | `YYYY-MM-DD-<subject-or-scope-slug>` |
| `date` | Date the retrospective was generated |
| `subject` | The topic reviewed, or a scope slug for a multi-subject sweep |
| `is_ticker` | `true` for a single-ticker topic, `false` otherwise |

Then append a checkpoint to each graded entry from
`assets/checkpoint-template.md` and update its `status`, locating each
entry's file via `index_manager.py lookup` as described above. Report
first, writes second: the writes are irreversible in spirit even where
they're technically reversible on disk. Once every checkpoint is written,
run `index_manager.py rebuild` so the index picks up the new statuses and
the newly filed report.

Confirm back the scope reviewed, the count graded by outcome, and any entry
left `pending` with the missing fact named.

## Output schema

### Report sections

| # | Section | Content |
|---|---|---|
| 1 | Scope | Set reviewed, entry count, date range, generation date |
| 2 | Where the view stands | Live entries only: topic, direction, conviction, age; contradictions between open entries flagged |
| 3 | How the view moved | Per chain, oldest to newest: each link's delta and change classification |
| 4 | Scorecard | Per graded entry: outcome, leg grades, mitigant grades, cross-tab cell |
| 5 | What broke | Legs and mitigants that failed, grouped by recurring cause rather than by entry |
| 6 | Calibration | Script output, verbatim, including `insufficient_data` buckets |
| 7 | Process findings | Patterns in how beliefs were written: unfalsifiable entries, fabricated catalysts, mitigant classes that repeatedly fail, price-driven revisions |
| 8 | Due next | Open entries with `check_by` approaching or passed |

### Checkpoint block (appended to an entry)

| Field | Content |
|---|---|
| `checkpoint_date` | Date of this review |
| `outcome` | `confirmed` / `falsified` / `inconclusive` / `superseded` / `pending` |
| `legs` | Per-leg grade with the observation that settled it |
| `mitigants` | Per-mitigant grade |
| `cross_tab` | Which of the four cells this entry lands in |
| `evidence` | What was sourced to establish the outcome, and when |
| `notes` | Anything the vocabularies don't capture |

## Example

**User:** "Review everything I've logged on the transformer name."

**Chain found:** three entries, `2026-01-14` -> `2026-04-30` -> `2026-07-22`,
each superseding the last.

**Section 3 — How the view moved (abridged):**

- `2026-01-14` -> `2026-04-30`: **`price-driven`.** Conviction `medium` ->
  `high`, entry price 48 -> 61, thesis legs unchanged in substance but
  rewritten with more force. Section 10 of the April entry cites no source
  dated after January. The stock moved 27% between the two; the reasoning
  did not move with it. Flagged for the user's judgment, not graded.
- `2026-04-30` -> `2026-07-22`: **`refinement`.** Same direction, same
  conviction. Leg 2 narrowed from "capacity is expanding" to the specific
  and checkable "no published sell-side model has revised capacity
  assumptions post-call." Falsification criteria tightened accordingly. This
  is the chain working as intended.

**Section 4 — Scorecard, entry `2026-01-14`:** outcome `superseded` before
resolution; legs ungraded. Entry `2026-04-30`: outcome `confirmed` — the
Q2 print converted backlog above the trailing average. Legs: 1 `held`,
2 `broke` (two sell-side models had in fact revised, published pre-print),
3 `held`. Mitigants: input supply `untested`, already-priced `failed` — the
revisions the mitigant claimed did not exist were the specific thing that
existed. Cross-tab: **right for the wrong reasons.** The call paid; the
mechanism claimed was not the mechanism that operated.

**Section 7 — Process findings:** across eleven graded entries, mitigants of
the form "the market hasn't noticed yet" graded `failed` four times out of
five tested, while contractual and structural mitigants graded `held` in
six of seven. The user's mitigants are reliable when they rest on a document
and unreliable when they rest on an assumption about other people's
attention.

**Section 6 — Calibration:** `high` conviction, n=7, hit rate 71%.
`very high`, n=2, `insufficient_data`. `medium`, n=4, `insufficient_data`.
Brier over the four probabilistic entries: `insufficient_data`. Reported as
returned — three of five buckets have no usable number yet, and saying so is
the finding.

## Limitations

- This skill does not manage where entries or reports live or how they're
  found — that's `research-workspace`'s job. This skill only reads entries
  it's pointed at and appends checkpoints to them.
- A retrospective can only be as good as the entries. Vague theses and
  `unspecified` falsification criteria produce `inconclusive` grades, and no
  amount of care at review time recovers what wasn't written at entry time.
  Persistent `inconclusive` rates are a signal to fix `belief-journal`
  discipline, not this skill.
- Calibration needs volume. Below the script's minimum bucket size the
  numbers are noise, and a plausible-looking hit rate over six entries is
  more misleading than a blank.
- Grading is retrospective and therefore hindsight-contaminated by
  construction. The rubric's insistence on section 9 as written is the only
  real defense, and it fails silently whenever criteria were written loosely
  enough to be read either way.
- A single outcome does not falsify a probability. An 80% call that broke
  was not necessarily wrong; only the run of them says anything, which is
  why per-entry grades and calibration are reported separately and never
  netted against each other.
- Chain classification assumes `supersedes` was set honestly. A revised view
  logged as a fresh entry breaks the chain and will read as two independent
  beliefs.
- This skill grades reasoning, not results. It will mark a profitable
  position `falsified` and an unprofitable one `wrong for the right
  reasons`, and that divergence is the intended output, not a defect to
  reconcile against a P&L.