---
name: research-workspace
description: Use whenever an investment-research skill (belief-journal, thematic-mapping, quantitative-value-screen, initiating-coverage, belief-retrospective, or similar) is about to save an artifact to disk, and whenever the user asks what exists on a given company or topic. Triggers include "where should this go," "file this," "what do I have on X," "what's on my watchlist," "have I looked at X before," "pull up everything on X," or a hand-off from another research skill that has just produced a memo, screen, map, or grading and needs to write it somewhere durable. Also use to reconcile watchlists when the same ticker surfaces from more than one theme. Do not use this skill to perform any research, analysis, or judgment about a company — it only manages where artifacts live and how to find them again. For the analysis itself, use the specific research skill (thematic-mapping, initiating-coverage, thesis-validation, comparable-companies, quantitative-value-screen, belief-journal, belief-retrospective).
---

# Research Workspace

## Purpose

Give every other skill in the research suite one place to put things, and
give the user one place to ask about them. On its own, none of the research
skills knows or cares where its output ends up — that's a feature, they
should stay focused on the analysis. But without something that *does* care,
outputs land wherever a given conversation happened to put them, the same
ticker accumulates parallel, disconnected files across skills, and "what do
I have on SOFI" has no answer short of manually searching everything.

This skill is pure bookkeeping. It defines where a file goes, tags it so it
can be found again, and answers lookups. It never opens a filing cabinet and
starts reading what's inside — it has no opinion on whether a thesis is
good, whether a screen passed, or whether a belief was right. That judgment
belongs entirely to the skill that produced the artifact.

## When to use this skill

- **Filing**: another skill (or the user, pasting in analysis from
  elsewhere) has a finished artifact — a memo, a screen result, a thematic
  map, a retrospective grading — and needs a canonical place to save it.
- **Lookup**: the user asks what exists on a ticker or topic — "what do I
  have on SOFI," "have I written this up before," "what's my history with
  this name."
- **Watchlist reconciliation**: a thematic-mapping run surfaces a ticker
  that already has artifacts elsewhere, or that already sits on another
  theme's watchlist, and the overlap is worth surfacing rather than quietly
  duplicating.
- **Workspace health check**: the user wants to know if anything is
  inconsistent — dangling `supersedes` references, duplicate ids, files
  missing frontmatter.

## When NOT to use this skill

- **Doing the actual research** — decomposing a theme, writing a memo,
  running a screen, grading a thesis. Use the specific skill; hand off to
  this one only once that skill has something to save.
- **Judging an artifact's content** — whether a thesis is convincing,
  whether a screen result is bullish or bearish. This skill doesn't read
  for meaning, only for frontmatter.
- **Tracking an active thesis's live, mutable status** (price targets,
  catalyst progress) — that belongs to `thesis-tracker`. This skill's
  artifacts are dated and durable, not something to update in place.

## Workflow

### 1. Filing a new artifact

When another skill (or the user) has a finished artifact ready to save:

1. Determine `artifact_type`: `theme_map`, `screen`, `belief`, `coverage`,
   or `retrospective`, based on which skill produced it.
2. Get the canonical path — don't build it by hand:
   ```
   python3 scripts/index_manager.py path --skill <skill-name> \
     --subject <TICKER-or-topic-slug> --date <YYYY-MM-DD> --slug <slug> \
     --root research
   ```
   or, for a theme-level artifact:
   ```
   python3 scripts/index_manager.py path --skill thematic-mapping \
     --theme <theme-slug> --date <YYYY-MM-DD> --slug <slug> --root research
   ```
3. Add the required frontmatter block to the top of the artifact (see
   `references/folder-schema.md` for the full field list — the short
   version: every file needs `artifact_type`, `skill`, `id`, `date`; subject
   artifacts also need `subject` and `is_ticker`; theme artifacts also need
   `theme` and `subjects`).
4. If this artifact supersedes a prior one on the same subject (a changed
   belief, a re-run screen), set `supersedes` to the prior artifact's `id`.
   Never edit the prior file — it stays as a historical record.
5. Write the file to the path from step 2.
6. Rebuild the index and report back what happened:
   ```
   python3 scripts/index_manager.py rebuild --root research
   ```
   Surface any warnings the rebuild reports — a dangling `supersedes`, a
   duplicate id — rather than letting them pass silently. These are cheap to
   fix the moment they're introduced and much more annoying to track down
   later.

### 2. Looking something up

```
python3 scripts/index_manager.py lookup <SUBJECT> --root research
```

This always rebuilds first, so the answer is never stale. Report what comes
back plainly: every artifact on the subject, which skill produced it, its
date, its status if it has one, and whether it's been superseded. If nothing
comes back, say so — don't imply coverage exists that doesn't.

To see everything at once, or everything under one theme:

```
python3 scripts/index_manager.py list --root research
python3 scripts/index_manager.py list --theme <theme-slug> --root research
```

### 3. Reconciling watchlists

After a `thematic-mapping` run produces a new watchlist, check whether any
of its subjects already appear elsewhere in the index (another theme, or
existing standalone artifacts):

```
python3 scripts/index_manager.py list --root research
```

Compare the new theme's subject list against what's already indexed. Don't
re-run or duplicate anything — just report the overlap plainly ("SOFI is
also on the fintech-unbundling watchlist from January, and already has a
belief-journal entry and a failed Graham screen from February"). What the
user does with that overlap is their call, not this skill's.

### 4. Workspace health check

Run `rebuild` and report the warnings section verbatim, grouped by type
(missing frontmatter, duplicate ids, dangling supersedes references, theme
watchlists pointing at subjects with no artifacts of their own). These
warnings are the whole point of deriving the index from frontmatter instead
of hand-maintaining it — they surface exactly the kind of quiet drift that a
manually-updated index would hide.

## Output

This skill doesn't produce a report of its own. Its output is: a file
written to the correct path, an updated `_index.json`, and a plain-language
summary of what changed or what a lookup found. Keep that summary short —
a table of artifacts and their dates is more useful here than prose.

## Example

**User:** "Log this SOFI belief" (hand-off from belief-journal, which has
just produced a finished memo).

**This skill:**
1. `python3 scripts/index_manager.py path --skill belief-journal --subject SOFI --date 2026-08-06 --slug sofi-backlog-thesis --root research`
   → `research/SOFI/belief-journal/2026-08-06-sofi-backlog-thesis.md`
2. Adds frontmatter (`artifact_type: belief`, `skill: belief-journal`,
   `id: 2026-08-06-sofi-backlog-thesis`, `date: 2026-08-06`,
   `subject: SOFI`, `is_ticker: true`, `status: open`, plus belief-journal's
   own fields like `conviction` and `check_by`).
3. Writes the file, runs `rebuild`.
4. Reports: "Filed to `research/SOFI/belief-journal/2026-08-06-sofi-backlog-thesis.md`.
   SOFI now has 3 artifacts on record: this belief, a February belief it
   doesn't supersede (different thesis leg), and a failed Graham screen from
   February. SOFI is also on the fintech-unbundling theme watchlist from
   January."

## Limitations

- **This is a filing convention, not a database.** There's no locking, no
  concurrent-write handling, no transaction log — it assumes one person (or
  one Claude session at a time) is writing to the workspace. Fine for an
  individual research practice; not built for a shared team drive with
  simultaneous writers.
- **The workspace only exists where you keep it.** Claude's own filesystem
  resets between sessions. `research/` needs to live somewhere that
  persists — a git repo, a synced folder, a location you re-upload — or
  every session starts from an empty index.
- **The index trusts frontmatter, not content.** If a file's frontmatter
  claims `status: pass` but the body says otherwise, the index will report
  `pass`. This skill never reads artifact bodies for meaning, only for the
  frontmatter block — accuracy there is the producing skill's
  responsibility.
- **`is_ticker` and `subject` are self-reported.** Nothing here validates
  that `SOFI` is a real ticker. That's fine for filing and lookup, which
  don't need to know; it does mean a typo'd ticker silently becomes its own
  subject rather than erroring.
