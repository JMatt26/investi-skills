# Folder schema and frontmatter contract

This is the convention every skill in the research suite writes to. It has
two parts: where a file goes, and what its frontmatter must say. Both are
required — a file in the right folder with no frontmatter is invisible to
the index, and correct frontmatter in the wrong folder just means the next
person has to go find it.

## Directory layout

```
research/
  _index.json                          <- generated, never hand-edited
  _themes/
    <theme-slug>/
      YYYY-MM-DD-<slug>.md             <- thematic-mapping output
  <SUBJECT>/
    belief-journal/
      YYYY-MM-DD-<slug>.md
    quantitative-value-screen/
      YYYY-MM-DD-<slug>.md
    initiating-coverage/
      YYYY-MM-DD-<slug>.md
    belief-retrospective/
      YYYY-MM-DD-<slug>.md
```

`<SUBJECT>` is a ticker (`SOFI`) for anything investment-related, or a
short slug (`hiring-vp-eng`) for the non-ticker predictions belief-journal
also supports. One folder per subject, one subfolder per skill that has
touched it — never a skill-first layout, because the whole point is that
"everything on SOFI" should be one folder, not a search across five.

Theme-level artifacts (the dependency chain + full watchlist thematic-mapping
produces) are the one exception to subject-first: a theme spans many
subjects, so its master file lives once under `_themes/<theme-slug>/`, and
each subject it touches is cross-referenced through the index rather than
copied. Don't duplicate a theme map into every subject folder it mentions —
that's exactly the drift this convention exists to prevent.

## Filenames

`YYYY-MM-DD-<slug>.md`, where `<slug>` is a short, human-readable
hyphenated description (`sofi-fintech-view`, `graham-defensive`,
`fintech-unbundling-map`). Never reuse a filename for a new version of the
same thing — a changed view is a new dated file with `supersedes` set, not
an edit to the old one.

Use `scripts/index_manager.py path` to construct the path rather than
building it by hand — it takes the skill name, subject or theme, date, and
slug, and prints the exact path this convention specifies. This removes an
entire class of avoidable typo.

## Frontmatter contract

Every file gets a YAML frontmatter block at the top. The index is built
entirely by reading these blocks — nothing else about the file's content is
parsed. A file with no frontmatter, or missing a required field, is invisible
to the index (and `rebuild` will tell you so).

### Every artifact, no exceptions

| Field | Value |
|---|---|
| `artifact_type` | `theme_map` / `screen` / `belief` / `coverage` / `retrospective` |
| `skill` | Name of the producing skill, e.g. `belief-journal` |
| `id` | `YYYY-MM-DD-<slug>`, unique across the entire workspace |
| `date` | ISO date the artifact was produced |

### Subject-centric artifacts (`screen`, `belief`, `coverage`, `retrospective`)

| Field | Value |
|---|---|
| `subject` | The folder key — ticker or topic slug |
| `is_ticker` | `true` if `subject` is a tradeable ticker, `false` for a non-ticker topic |
| `status` | Optional, skill-defined free text (`open`, `fail`, `pass`, `confirmed`...) |
| `supersedes` | Optional — `id` of the prior artifact this one replaces |

### Theme-centric artifacts (`theme_map`)

| Field | Value |
|---|---|
| `theme` | Theme slug |
| `subjects` | List of every subject key referenced in the watchlist, e.g. `[SOFI, UPST, AFRM]` |

A skill can carry additional frontmatter fields of its own (belief-journal's
`conviction` and `check_by`, for instance) — the index ignores anything it
doesn't recognize. It only requires the fields above to be present and
correctly named.

## Why the index is always rebuilt, never edited

`_index.json` is a derived file, the same way a compiled binary is derived
from source. Every command in `index_manager.py` that reads the index
rebuilds it first. This means:

- The index can never silently drift from what's actually on disk.
- Manually moving, renaming, or deleting a file is safe — the next
  `rebuild` picks up the change automatically.
- There's no "did someone forget to register this" failure mode, because
  there's no separate registration step to forget. Writing the file with
  correct frontmatter *is* registering it.

The cost is that `rebuild` re-parses every file in the workspace every time.
For a research workspace measured in hundreds of files, this is milliseconds
— not worth trading away the guarantee for.
