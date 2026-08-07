---
name: thematic-mapping
description: Use when the user wants to decompose a macro trend or investment theme into a structured chain of dependent bets (sector -> sub-sector -> company) and convert that chain into a trackable watchlist. Triggers include "map out this theme," "what's the picks-and-shovels play on X," "build a watchlist around [trend]," "what benefits from [macro shift]," or requests to trace second- and third-order beneficiaries of a trend. Do not use for single-company research (use initiating-coverage), for stress-testing one already-identified thesis (use thesis-validation), or for benchmarking an already-defined peer set (use comparable-companies).
---

# Thematic Mapping

## Purpose

Turn a high-level theme into an explicit dependency chain, then populate that
chain with named companies and convert it into a trackable watchlist. This
skill exists to prevent the most common thematic-investing failure: stopping
at the first, most obvious layer of a trend (the "everyone already owns this"
layer) instead of tracing it down to less-crowded, higher-conviction links
further down the chain.

The output is a bridge artifact — every row it produces is designed to be
handed off to `thesis-tracker` (as a candidate thesis), `catalyst-calendar`
(as a name to watch for dated events), or `initiating-coverage` (for the
names that warrant a full report).

## When to use this skill

- The user names a macro trend, structural shift, or theme and wants
  investable exposure to it.
- The user wants to trace a trend through multiple layers of a value or
  supply chain, not just the first-order beneficiary.
- The user wants to convert a thematic view into a structured, rankable
  watchlist with an explicit rationale attached to each name.
- The user wants to see which layer of a theme is already crowded/priced in
  versus which layer is under-followed.

## When NOT to use this skill

- **Single-company deep dive** on a name already identified -> `initiating-coverage`
- **Pressure-testing** one specific thesis for holes and invalidation
  conditions -> `thesis-validation`
- **Benchmarking** an already-defined peer set on multiples ->
  `comparable-companies`
- **Tracking dated events** for names already on a watchlist ->
  `catalyst-calendar`
- The user already knows exactly which company they want to research — don't
  force a thematic decomposition onto a request that's really a single-name
  question in disguise.
- **Finding out whether a candidate is already covered elsewhere**, or
  filing the finished map -> hand off to `research-workspace`, which owns
  storage and cross-theme overlap detection for every skill in this suite.

## Workflow

### 1. Pin down the theme and its time horizon

Restate the theme as a single falsifiable claim, not a vibe. "AI is
transformative" is not a theme; "AI training compute demand will outpace
current data-center power capacity through 2027" is. Ask the user (or infer
from context) whether the theme is meant to play out over quarters, years, or
a full cycle — this changes which layers of the chain are relevant and how
crowded each layer already is.

### 2. Build the dependency chain

Trace the theme forward as a series of "X requires Y" links, one layer at a
time. Do not stop at the first layer. A useful chain is usually 3-6 layers
deep. For each link, state the dependency logic explicitly in one sentence —
if you can't state why layer N requires layer N+1, the link doesn't belong
in the chain.

Worked structure (using the canonical AI/power example):

1. **Demand driver** — AI model training and inference workloads scale
2. **Direct enabler** — GPU/accelerator compute (Nvidia, AMD, custom silicon)
3. **Second-order enabler** — advanced packaging and memory (HBM, CoWoS
   capacity)
4. **Infrastructure constraint** — data center power availability and
   transmission
5. **Physical bottleneck** — grid equipment, transformers, turbines
6. **Downstream beneficiary** — cooling systems, real estate/REITs with
   power access

Each layer should get progressively less obvious and less crowded as you go
deeper — that's the point of doing this exercise instead of buying the
first name that comes to mind.

### 3. Populate each layer with candidates

For each layer, list 2-5 companies with genuine exposure. For every
candidate, capture:

- **Exposure type** — pure-play vs. one segment among several
- **Dependency logic** — the one-sentence reason this company sits at this
  layer (link back to step 2's stated logic)
- **Crowding assessment** — is this name already a consensus thematic
  holding, or under-followed relative to its exposure
- **Confidence** — how directly the company's fundamentals are tied to the
  theme actually playing out (direct revenue exposure vs. speculative
  optionality)

If a layer's exposure logic is sound but no individual company meets the
confidence bar for a named ticker, do not force a name in. Instead, add a
row using a descriptive category in place of a ticker (e.g., "medical
aesthetics device makers") with `exposure_type` and `confidence` both set to
`speculative`, and note in `dependency_logic` that the row requires
individual screening before it can be treated as a watchlist candidate. An
honest category placeholder is better than a fabricated or low-conviction
ticker.

Do not include a company just because it was mentioned in an article about
the theme. Every entry needs its own stated dependency logic — this is the
same discipline that `note-intake` enforces on notes, applied here to
watchlist candidates.

### 4. Assess chain-level risk

Before finalizing, check the chain itself for two failure modes:

- **Single point of failure** — does one layer's link depend on an
  assumption that, if wrong, breaks every layer below it? State it
  explicitly (e.g., "the entire chain below layer 3 assumes power buildout
  is the binding constraint, not chip supply — if that assumption is wrong,
  layers 4-6 don't matter").
- **Consensus decay** — flag any layer where the dependency logic is now
  widely known and priced in. A theme's edge decays as it moves from
  "second-order enabler" to "any investor could name this."

### 5. Assemble the output

Use `assets/output-template.md` as the starting structure rather than
re-deriving the tables from scratch. Copy it and fill in:

**A. Thematic map** — the dependency chain itself, as an ordered list of
layers, each with its one-sentence dependency logic and a crowding note.

**B. Watchlist** — a flat table of every candidate company across all
layers, in the schema below, ready to hand off to other skills.

### 6. Flag hand-offs

For each watchlist entry, note which downstream skill it should go to next:

- High-conviction, well-understood name -> `initiating-coverage`
- Name with a specific bear case worth stress-testing -> `thesis-validation`
- Name whose only value is comparison to peers already on the watchlist ->
  `comparable-companies`
- Any name with a near-term dated event (earnings, product launch,
  regulatory decision) that could confirm/break the chain -> `catalyst-calendar`

### 7. File the map

The theme map is theme-centric, not company-centric — it spans every
subject on the watchlist, so it gets one master file rather than a copy per
company. Hand off to `research-workspace` to get the canonical path and
write and index the file:

```
python3 scripts/index_manager.py path --skill thematic-mapping \
  --theme <theme-slug> --date <YYYY-MM-DD> --slug map --root research
```

Add this frontmatter to the top of the assembled output before handing off:

| Field | Value |
|---|---|
| `artifact_type` | Always `theme_map` |
| `skill` | Always `thematic-mapping` |
| `id` | `YYYY-MM-DD-<theme-slug>` |
| `date` | Date the map was produced |
| `theme` | The theme slug |
| `subjects` | Every ticker (or descriptive-category placeholder) on the watchlist |

`research-workspace` will flag, at filing time, whether any watchlist
subject already has other artifacts on record or sits on another theme's
watchlist — surface that overlap to the user rather than treating each
theme map as if it starts from a blank slate.

## Output schema

### Thematic map entry (one per layer)

| Field | Description |
|---|---|
| `layer_number` | Position in the chain, 1 = closest to the demand driver |
| `layer_name` | Short label (e.g., "Advanced packaging & memory") |
| `dependency_logic` | One sentence: why this layer requires the layer above it |
| `crowding` | `consensus` / `emerging` / `under-followed` |
| `key_assumption` | The assumption this layer's inclusion rests on |

### Watchlist entry (one per company)

| Field | Description |
|---|---|
| `ticker` | Company ticker |
| `layer_number` | Which layer of the map this company sits at |
| `exposure_type` | `pure-play` / `segment-exposure` / `speculative-optionality` |
| `dependency_logic` | One sentence tying the company to its layer |
| `crowding` | `consensus` / `emerging` / `under-followed` |
| `confidence` | `direct` / `indirect` / `speculative` |
| `next_skill` | Recommended hand-off: `initiating-coverage` / `thesis-validation` / `comparable-companies` / `catalyst-calendar` / `none-yet` |

## Example

**Theme:** "Grid capacity constraints will gate AI data center buildout
growth through 2028, independent of chip supply."

**Map (abridged):**

1. Demand driver — hyperscaler AI capex growth (consensus)
2. Direct enabler — GPU/accelerator supply (consensus — already fully priced)
3. Infrastructure constraint — regional grid interconnection queues
   (emerging)
4. Physical bottleneck — power transformer and turbine manufacturing
   capacity (under-followed)
5. Downstream beneficiary — private power generation / behind-the-meter
   solutions (under-followed)

**Watchlist (abridged, layer 4):**

| ticker | layer | exposure | dependency_logic | crowding | confidence | next_skill |
|---|---|---|---|---|---|---|
| (transformer manufacturer) | 4 | pure-play | Multi-year order backlog directly tied to data-center and grid buildout | under-followed | direct | initiating-coverage |
| (turbine OEM) | 4 | segment-exposure | Power generation segment benefits, but diversified across non-AI end markets | emerging | indirect | comparable-companies |

The point of the exercise: layers 1-2 are where most investors stop, and
they're already consensus. Layers 4-5 are where the differentiated,
under-followed exposure sits — and every name there still has to earn its
place with a stated dependency logic, not just thematic vibes.

## Limitations

- This skill does not manage where the map is stored or whether its
  subjects overlap with other themes' watchlists — that's
  `research-workspace`'s job, run at filing time.
- This skill produces a *hypothesis*, not a validated thesis — every
  watchlist entry should go through `thesis-validation` or
  `initiating-coverage` before sizing a real position.
- Dependency chains are a simplification of real supply/demand networks;
  they will miss feedback loops and substitution effects (e.g., a
  breakthrough in power-efficient chip design could collapse the power
  bottleneck the whole chain assumes).
- Crowding assessments are qualitative and time-sensitive — a layer flagged
  "under-followed" today can become consensus within a single earnings
  season. Re-run this skill periodically for live themes rather than
  treating one map as durable.
- This skill does not forecast timing. It tells you *what* depends on
  *what*, not *when* the chain will play out — pair with `macro-context`/
  `catalyst-calendar` for timing signals.
