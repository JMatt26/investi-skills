# Calibration Methodology

What `scripts/calibration.py` computes, how to read each figure, and the
specific ways each one misleads. Read before reporting calibration for the
first time in a session.

Calibration answers one narrow question: **do the user's stated confidence
levels mean anything?** It says nothing about whether the beliefs were good,
whether the process is sound, or whether the positions made money. Those
live in the scorecard and the process findings. Keeping calibration in its
lane is most of what makes it useful.

---

## Minimum sample size

The script gates every bucket at `min_bucket_n`, default 5, and returns
`insufficient_data` below it rather than a number.

This is the most important behavior in the script and the one most likely to
be worked around. A hit rate over three entries carries no information, but
once written down as "67%" it will be remembered as a fact and repeated
without its caveat. **Report `insufficient_data` verbatim.** Do not
substitute a percentage with a warning attached, do not merge adjacent
conviction tiers to reach the threshold, and do not report a total hit rate
across all tiers as a stand-in — a blended hit rate is exactly the number
calibration exists to decompose.

Raising `min_bucket_n` above the default is reasonable. Lowering it is not,
and the report should say so if it was lowered.

---

## Figures

### Hit rate by conviction tier

Of entries graded `confirmed` or `falsified`, the share `confirmed`, split
by `low` / `medium` / `high` / `very high`.

**What good looks like:** monotonic. Higher tiers hit more often. The
absolute levels matter far less than the ordering.

**How it misleads:** it says nothing about *whether the tiers are spread
correctly*. A user whose tiers rank perfectly but who logs everything as
`high` has a well-ordered scale they never use. Report the distribution of
entries across tiers alongside the hit rates — a tier holding 80% of entries
is not functioning as a tier.

Non-monotonic ordering, once `n` is adequate, means the scale is decorative.
That is a finding about the user's self-assessment, not about their
analysis, and it is fixable in a way that being wrong often is not.

### Brier score

Mean squared error between stated probability and outcome, over resolved
entries that recorded a probability in section 5. Lower is better; 0 is
perfect.

**Reference point:** 0.25 is what you score by saying 50% to everything.
Above 0.25 means the stated probabilities are worse than useless — they are
actively pointing the wrong way. The script reports this comparator
alongside the score because a Brier score in isolation is uninterpretable to
most readers, including experienced ones.

**How it misleads:** Brier rewards confidence when right and punishes it
when wrong, so it blends calibration with discrimination. A cautious
forecaster who says 60% to everything and is right 60% of the time is
perfectly calibrated with a mediocre Brier. Read it next to the bucket
table, never alone.

It is also dominated by base rates. Someone who only logs beliefs about
likely events scores well by saying 90% constantly. The bucket table exposes
this; the score alone doesn't.

### Probability bucket table

Stated probabilities grouped into bands, each showing the observed
`confirmed` rate against the band's midpoint. Overconfidence looks like
observed rates consistently below stated ones in the high bands.

Bands below `min_bucket_n` return `insufficient_data`, which for most
journals will be most bands for a long time.

### Reasoning cross-tab

Counts across the four cells from `references/grading-rubric.md`. The figure
to watch is **right for the wrong reasons** as a share of all `confirmed`
entries. A high share means the outcomes are not coming from the stated
mechanisms, which makes the hit rates above much less meaningful than they
look — the user may be well calibrated about outcomes while reasoning
poorly about causes.

### Leg-break frequency by position

Which numbered leg breaks most often. Leg 1 is usually the core claim and
later legs are usually supporting; a user whose leg 1 holds and whose leg 3
breaks is building sound theses with decorative support, while the reverse
means the supporting analysis is carrying a weak core.

Only meaningful if the user numbers legs consistently by importance. If they
don't, this figure is noise — check a sample before reporting it.

### Mitigant failure rate

Of mitigants actually tested (`held` + `failed`), the share `failed`. Report
by class of mitigant where classes are visible, not just in aggregate; the
aggregate rate is far less actionable than "the ones resting on documents
hold and the ones resting on assumptions about other people don't."

`untested` mitigants are excluded from the denominator and reported
separately. A very high `untested` share is normal and not a finding.

### Change classification counts

Counts by class from `references/view-change-taxonomy.md`, across all links
in scope. The `price-driven` count is the one to surface. Report it as a
count with the links listed, not as a rate — a rate invites comparison
against an imagined normal, and no such benchmark exists.

---

## What is deliberately not computed

- **Returns, P&L, or attribution.** Not in scope, and mixing them in would
  let profitable-but-falsified entries score well, which defeats the rubric.
- **Statistical significance.** No confidence intervals, no p-values. At
  these sample sizes they would imply a precision the data cannot support,
  and the `insufficient_data` gate is a blunter but more honest instrument.
- **A single composite score.** Every attempt to net these figures into one
  number hides the disagreement between them, and the disagreement is the
  finding.