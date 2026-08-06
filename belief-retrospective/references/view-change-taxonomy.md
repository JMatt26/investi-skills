# View Change Taxonomy

How to classify each link in a supersession chain. A chain is built by
following `supersedes` backwards; each adjacent pair of entries is one link,
and every link gets exactly one classification.

This is the machinery behind the report's "how the view moved" section. The
question it answers is not *what* changed — a diff answers that — but *what
moved it*.

---

## Delta fields

Compare these fields between the superseded entry (A) and the superseding
one (B), in this order. The first material difference usually determines the
classification.

| Field | What a change indicates |
|---|---|
| `direction` | A flip. Always `reversal`. |
| `conviction` | Tier movement, up or down. |
| `entry_price` | Where the view was re-struck. Context for every other delta. |
| Section 3 legs | Legs added, dropped, or restated. The substance of the change. |
| Section 5 valuation | Target and methodology. A target moving without a methodology change is usually mark-following. |
| Section 4 catalyst / `horizon_type` | A `dated` horizon becoming `open-ended` is patience replacing a thesis about timing. |
| Section 9 criteria | Loosened criteria are a warning sign; tightened ones are the chain working. |
| Section 10 sources | **The classification test.** See below. |

---

## Classifications

### `refinement`

Same direction, same or near-same conviction, legs narrowed or made more
specific, criteria tightened. The view didn't change; its statement got
sharper. This is what a healthy chain looks like and it needs no comment
beyond noting which leg got sharper.

### `reversal`

`direction` flipped. Report the full delta and the elapsed time. Reversals
are not failures — a fast reversal on new information is the system working
— but they should always carry the reason and the source that drove them.

### `conviction-shift`

Direction unchanged, `conviction` tier moved. Report which legs changed to
justify it. A conviction tier that moves with no leg changing is the same
belief asserted more loudly, and should be reported as such.

### `horizon-driven`

The thesis did not break; the willingness to wait ran out, or a `dated`
horizon lapsed and was replaced. Distinguish carefully from `falsified` —
an entry abandoned at horizon with no criterion met is `inconclusive`, and
its successor is `horizon-driven`. Frequent `horizon-driven` links mean
horizons are being set shorter than the theses need.

### `price-driven`

Direction or conviction moved, and **section 10 of entry B cites no source
dated after entry A's `date_logged`**, while `entry_price` moved materially
between them.

This is the classification that earns the taxonomy its keep. It identifies a
view that changed after the mark changed, with reasoning assembled
afterwards. It is not dishonesty and it is not rare; it is the ordinary way
conviction tracks P&L in a person who is trying hard not to let it.

**Report it as an observation, never as a verdict.** Show three things and
stop: the two dates, the price delta between them, and the fact that no
newer source is cited. The user is better placed than the retrospective to
know whether something they knew but didn't write down drove the change.

Do not apply `price-driven` when:

- Section 10 of B cites any source dated after A. Classify by what changed
  instead, and note the price move as context.
- The price move *is* the news — a gap on an announcement, a halt, a break.
  The event is the source; classify as `refinement` or `reversal`.
- The entry is explicitly a re-strike at a new level with the thesis
  unchanged. That is a position decision, not a belief change.

---

## Chain-level findings

Beyond individual links, report on the chain as a whole:

- **Drift without a break.** Every link `refinement`, no link `reversal`,
  and the terminal entry's legs share little substance with the first
  entry's. The view changed completely without ever being wrong. Show the
  first and last entries' legs side by side and let the user see it.
- **Conviction ratchet.** `conviction` only ever rises across the chain.
  Over a long chain this is close to definitional evidence that the tier
  tracks commitment rather than evidence.
- **Criteria loosening.** Section 9 gets less specific at each link. The
  belief is being made progressively harder to falsify, usually while the
  position is losing.
- **Chain length against horizon.** A chain of six entries inside a
  two-quarter horizon means the view is being restated more often than the
  evidence can possibly turn over.

Report chain-level findings only where the chain is at least three entries
long. Two entries is a change, not a pattern.