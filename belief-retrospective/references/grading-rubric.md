# Grading Rubric

Fixed vocabularies and decision procedures. These terms carry the same
meaning across every retrospective, in every session, forever. A grade that
drifts in meaning silently destroys the comparability that makes a run of
retrospectives worth anything — which is the whole reason the vocabulary is
closed rather than descriptive.

Grade in the order below: legs, then mitigants, then outcome. Grading the
outcome first anchors the leg grades to it, and the point of grading them
separately is to let them disagree.

---

## 1. Thesis legs

Grade each numbered leg from section 3 of the entry independently. A leg is
a claim about a fact or mechanism, so it can be checked without reference to
whether the position worked.

| Grade | Applies when |
|---|---|
| `held` | The claimed fact or mechanism was observed to operate as stated. |
| `broke` | The claimed fact or mechanism was observed **not** to operate as stated. |
| `unresolved` | The horizon passed without the claim becoming observable either way. |
| `unfalsifiable-as-written` | The leg cannot be checked against any observation, because it was written as an adjective, a preference, or a tautology. |

`unfalsifiable-as-written` is not a soft `unresolved`. It records a defect in
the entry rather than in the world, and it is the grade that drives the
process findings in the report. Apply it whenever the honest answer to "what
observation would settle this leg?" is that none would.

**A leg does not inherit the outcome.** A leg that claimed margin expansion
grades `broke` if margins were flat, even where revenue growth carried the
thesis to a `confirmed` outcome. This separation is the source of the
cross-tab in section 4.

---

## 2. Mitigants

Grade each mitigant from section 6. `belief-journal` requires every mitigant
to be stated as a checkable claim precisely so this grading is possible; a
mitigant that reads as reassurance rather than a claim grades
`unfalsifiable-as-written` and is reported as an entry defect.

| Grade | Applies when |
|---|---|
| `untested` | The paired risk never materialized. The mitigant was never called on and learns us nothing. |
| `held` | The risk materialized and the mitigant absorbed it as claimed. |
| `failed` | The risk materialized and the mitigant did not absorb it. |
| `unfalsifiable-as-written` | The mitigant was not stated as a checkable claim. |

Two rules:

- **Only a materialized risk tests its mitigant.** Do not grade a mitigant
  `held` because the position worked. Most mitigants in most entries will be
  `untested`, and that is the correct result.
- **`failed` is the highest-value grade in this skill.** It identifies the
  specific sentence the user wrote to talk themselves past a risk that then
  landed. Repeated `failed` grades on structurally similar mitigants are the
  strongest pattern the retrospective can surface, and they should be
  reported by *class* of mitigant rather than by entry.

Risks logged with no mitigant (`this risk stands unoffset`) are not graded.
Note separately whether unoffset risks materialized more or less often than
offset ones — a user whose unoffset risks rarely land is being appropriately
honest about which risks they can't answer.

---

## 3. Outcome

Grade the entry as a whole, against section 9 **as written**.

| Grade | Applies when |
|---|---|
| `confirmed` | The horizon completed, no falsification criterion was met, and the recommendation in section 1 played out as stated. |
| `falsified` | Any falsification criterion in section 9 was met — regardless of whether the position made money. |
| `inconclusive` | The horizon completed without either condition being satisfied, or section 9 was logged `unspecified`. |
| `superseded` | A later entry replaced this one before it resolved. Legs and mitigants are left ungraded. |
| `pending` | The outcome could not be established from available data. Not written to `status`; the entry stays `open` and the report names the missing fact. |

### Decision procedure

1. Was this entry superseded before its horizon completed? -> `superseded`. Stop.
2. Has the horizon completed, or has a falsification criterion been met early?
   If neither -> leave `open`. Stop.
3. Could the outcome be established from sourced data? If not -> `pending`. Stop.
4. Was any section 9 criterion met? -> `falsified`. Stop.
5. Was section 9 logged `unspecified`? -> `inconclusive`, flagged as a
   process failure. Stop.
6. Did section 1's recommendation play out as stated? -> `confirmed`,
   otherwise `inconclusive`.

Step 4 precedes step 6 deliberately. An entry whose criterion was met is
`falsified` even where the outcome looks favorable — that combination is the
most informative thing a journal can produce, because it means the user
correctly identified in advance what would prove them wrong, watched it
happen, and got paid anyway. Letting the P&L overwrite that grade throws
away the only evidence that the criterion was well chosen.

### Horizon handling

- `horizon_type: dated` — the horizon completes when the stated event
  occurs or its date passes, whichever is first.
- `horizon_type: open-ended` — there is no completion, only review. Grade at
  the stated cadence: `falsified` if a criterion was met, otherwise
  `open` with a checkpoint appended recording that the review happened and
  nothing broke. Never grade an open-ended entry `inconclusive` for failing
  to resolve; not resolving is what it was written to do.

---

## 4. The cross-tab

Every entry graded `confirmed` or `falsified` lands in one cell:

| | All legs `held` | Any leg `broke` |
|---|---|---|
| **`confirmed`** | Right for the right reasons | **Right for the wrong reasons** |
| **`falsified`** | **Wrong for the right reasons** | Wrong for the wrong reasons |

- **Right for the right reasons** — the process worked. Nothing to fix.
- **Right for the wrong reasons** — the outcome paid, the mechanism claimed
  did not operate. Always name this explicitly in the report. It is the only
  cell that reinforces a broken process with a positive result, and it is
  invisible to any outcome-only review.
- **Wrong for the right reasons** — the mechanism operated and the outcome
  still went against the entry. Usually horizon, sizing, or a risk correctly
  identified and accepted. Rarely a reason to change the process.
- **Wrong for the wrong reasons** — the ordinary miss. Diagnostic value sits
  in *which* leg broke, not in the cell.

Entries where every leg is `unresolved` or `unfalsifiable-as-written` do not
enter the cross-tab. Count them separately; a high count there is the report's
most important process finding, and averaging them into the cross-tab hides it.