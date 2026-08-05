---
retrospective_date: 
scope: 
entries_reviewed: 
date_range: 
chains_reviewed: 
---

## 1. Scope

<!-- The set reviewed, stated precisely enough that another run reproduces it:
     topic / tag / date range / "all entries due" / whole journal.
     Entry count, date range of entries, and the date this report was generated. -->


## 2. Where the view stands

<!-- Live entries only: terminal entry of each chain with status open.
     One line each: topic, direction, conviction, entry price, age, check_by.
     Flag explicitly:
       - open entries that contradict each other
       - entries whose check_by passed long ago (a stale live view is a finding) -->

| Topic | Direction | Conviction | Logged | Check by | Note |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

**Contradictions between open entries:**

<!-- Or: none found. -->


## 3. How the view moved

<!-- Per chain, oldest to newest. One block per link.
     Each link: the delta (direction, conviction, price, legs, valuation,
     criteria) and its classification from references/view-change-taxonomy.md.
     For price-driven links show only: the two dates, the price delta, and the
     absence of a newer cited source. Observation, not verdict.
     Chain-level findings (drift without a break, conviction ratchet, criteria
     loosening) only where the chain runs to three entries or more. -->

### Chain: 

- `` -> ``: **``**


## 4. Scorecard

<!-- One row per graded entry. Cross-tab cell per references/grading-rubric.md.
     Entries with no gradeable legs get an outcome but no cross-tab cell —
     leave it blank rather than guessing. -->

| Entry | Outcome | Legs | Mitigants | Cross-tab |
|---|---|---|---|---|
|  |  |  |  |  |

**Pending — outcome could not be established:**

<!-- Entry id and the specific fact that was missing. Or: none. -->


## 5. What broke

<!-- Legs graded `broke` and mitigants graded `failed`, grouped by recurring
     cause rather than by entry. The unit of insight is the class of error,
     not the individual miss. -->


## 6. Calibration

<!-- Output of scripts/calibration.py. Report every insufficient_data verbatim.
     Do not substitute a caveated percentage, merge buckets to reach the
     sample floor, or fall back to a blended rate. -->

| Conviction | Resolved n | Hit rate | Share of entries |
|---|---|---|---|
| low |  |  |  |
| medium |  |  |  |
| high |  |  |  |
| very high |  |  |  |

**Ordering:** 
**Reasoning cross-tab:** 
**Right for the wrong reasons, share of confirmed:** 
**Brier:**  (uninformative comparator: 0.25)
**Mitigant failure rate over tested mitigants:** 


## 7. Process findings

<!-- Patterns in how the beliefs were written, not in what happened:
       - entries graded inconclusive because section 9 was unspecified
       - legs or mitigants graded unfalsifiable-as-written
       - classes of mitigant that repeatedly fail
       - price-driven revisions
       - horizons set shorter than the theses need
     Each finding needs the entries behind it named. A pattern without its
     instances is an opinion. -->


## 8. Due next

<!-- Open entries with check_by approaching or passed, soonest first. -->

| Entry | Topic | Check by | Status |
|---|---|---|---|
|  |  |  |  |