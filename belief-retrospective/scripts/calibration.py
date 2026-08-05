#!/usr/bin/env python3
"""Deterministic calibration calculator for graded belief-journal entries.

Computes the aggregate figures reported in section 6 of a retrospective:

  - hit rate by conviction tier, with tier distribution
  - the reasoning cross-tab (right/wrong x right/wrong reasons)
  - leg-break frequency by leg position
  - mitigant grade tally and failure rate over tested mitigants
  - probability calibration: Brier score and observed-vs-stated buckets
  - change-classification counts across supersession links

The script performs arithmetic only. It does not grade entries, source
outcomes, or interpret results. Every bucket below `min_bucket_n` returns
the string "insufficient_data" instead of a number -- see
references/calibration-methodology.md for why this must be reported
verbatim rather than replaced with a caveated percentage.

Usage:
    python calibration.py graded.json
    python calibration.py graded.json --pretty
    python calibration.py graded.json --min-bucket-n 8

Input schema:

{
  "scope": "transformer chain",            # optional, echoed in output
  "min_bucket_n": 5,                       # optional, default 5
  "entries": [
    {
      "id": "2026-04-30-transformer-backlog",
      "conviction": "high",                # low|medium|high|very high
      "outcome": "confirmed",              # confirmed|falsified|inconclusive
                                           #   |superseded|pending|open
      "stated_probability": 0.8,           # optional, 0..1
      "legs": [                            # optional
        {"position": 1, "grade": "held"}   # held|broke|unresolved
      ],                                   #   |unfalsifiable-as-written
      "mitigants": [                       # optional
        {"label": "already priced", "grade": "failed"}
      ]                                    # untested|held|failed
    }                                      #   |unfalsifiable-as-written
  ],
  "links": [                               # optional, supersession links
    {
      "from": "2026-01-14-transformer-backlog",
      "to": "2026-04-30-transformer-backlog",
      "classification": "price-driven"     # refinement|reversal
    }                                      #   |conviction-shift
  ]                                        #   |horizon-driven|price-driven
}

Output: JSON to stdout. Exit code 0 on success, 1 on malformed input.
"""

import argparse
import json
import sys

INSUFFICIENT = "insufficient_data"
DEFAULT_MIN_BUCKET_N = 5

CONVICTION_TIERS = ["low", "medium", "high", "very high"]
RESOLVED_OUTCOMES = ["confirmed", "falsified"]
OUTCOMES = RESOLVED_OUTCOMES + ["inconclusive", "superseded", "pending", "open"]
LEG_GRADES = ["held", "broke", "unresolved", "unfalsifiable-as-written"]
MITIGANT_GRADES = ["untested", "held", "failed", "unfalsifiable-as-written"]
CHANGE_CLASSES = [
    "refinement",
    "reversal",
    "conviction-shift",
    "horizon-driven",
    "price-driven",
]

# Brier score obtained by answering 50% to every question. Reported as a
# comparator because a Brier score in isolation is uninterpretable.
UNINFORMATIVE_BRIER = 0.25

PROBABILITY_BANDS = [
    (0.0, 0.2),
    (0.2, 0.4),
    (0.4, 0.6),
    (0.6, 0.8),
    (0.8, 1.0),
]


class InputError(Exception):
    """Raised on malformed input. Never raised on sparse-but-valid input."""


# ---------------------------------------------------------------------------
# validation
# ---------------------------------------------------------------------------

def _require(condition, message):
    if not condition:
        raise InputError(message)


def _check_enum(value, allowed, field, entry_id):
    _require(
        value in allowed,
        "entry '{}': {} must be one of {}, got {!r}".format(
            entry_id, field, allowed, value
        ),
    )


def validate(data):
    """Validate structure and vocabularies. Missing optional data is fine."""
    _require(isinstance(data, dict), "top level must be a JSON object")
    entries = data.get("entries")
    _require(isinstance(entries, list), "'entries' must be a list")

    seen = set()
    for entry in entries:
        _require(isinstance(entry, dict), "each entry must be an object")
        entry_id = entry.get("id")
        _require(
            isinstance(entry_id, str) and entry_id,
            "every entry needs a non-empty string 'id'",
        )
        _require(entry_id not in seen, "duplicate entry id: {}".format(entry_id))
        seen.add(entry_id)

        _check_enum(entry.get("outcome"), OUTCOMES, "outcome", entry_id)

        if entry.get("conviction") is not None:
            _check_enum(
                entry["conviction"], CONVICTION_TIERS, "conviction", entry_id
            )

        prob = entry.get("stated_probability")
        if prob is not None:
            _require(
                isinstance(prob, (int, float)) and 0.0 <= prob <= 1.0,
                "entry '{}': stated_probability must be between 0 and 1".format(
                    entry_id
                ),
            )

        for leg in entry.get("legs") or []:
            _require(isinstance(leg, dict), "each leg must be an object")
            _check_enum(leg.get("grade"), LEG_GRADES, "leg grade", entry_id)

        for mit in entry.get("mitigants") or []:
            _require(isinstance(mit, dict), "each mitigant must be an object")
            _check_enum(
                mit.get("grade"), MITIGANT_GRADES, "mitigant grade", entry_id
            )

    for link in data.get("links") or []:
        _require(isinstance(link, dict), "each link must be an object")
        _check_enum(
            link.get("classification"),
            CHANGE_CLASSES,
            "link classification",
            "{} -> {}".format(link.get("from"), link.get("to")),
        )

    min_n = data.get("min_bucket_n", DEFAULT_MIN_BUCKET_N)
    _require(
        isinstance(min_n, int) and min_n >= 1,
        "'min_bucket_n' must be a positive integer",
    )


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _rate(numerator, denominator, min_n):
    """Share as a percentage, or INSUFFICIENT below the sample floor."""
    if denominator < min_n:
        return INSUFFICIENT
    return round(100.0 * numerator / denominator, 1)


def _tally(values, vocabulary):
    counts = {term: 0 for term in vocabulary}
    for value in values:
        counts[value] += 1
    return counts


def _resolved(entries):
    return [e for e in entries if e.get("outcome") in RESOLVED_OUTCOMES]


# ---------------------------------------------------------------------------
# figures
# ---------------------------------------------------------------------------

def outcome_summary(entries):
    return {
        "total_entries": len(entries),
        "by_outcome": _tally([e["outcome"] for e in entries], OUTCOMES),
        "resolved": len(_resolved(entries)),
    }


def conviction_calibration(entries, min_n):
    """Hit rate per tier, plus the distribution of entries across tiers.

    Distribution matters as much as the rates: a well-ordered scale that is
    never used is still a broken scale.
    """
    resolved = _resolved(entries)
    total_logged = len([e for e in entries if e.get("conviction")])
    tiers = {}

    for tier in CONVICTION_TIERS:
        in_tier = [e for e in resolved if e.get("conviction") == tier]
        hits = len([e for e in in_tier if e["outcome"] == "confirmed"])
        logged = len([e for e in entries if e.get("conviction") == tier])
        tiers[tier] = {
            "resolved_n": len(in_tier),
            "confirmed": hits,
            "hit_rate_pct": _rate(hits, len(in_tier), min_n),
            "share_of_all_entries_pct": (
                round(100.0 * logged / total_logged, 1) if total_logged else None
            ),
        }

    usable = [
        t for t in CONVICTION_TIERS if tiers[t]["hit_rate_pct"] != INSUFFICIENT
    ]
    if len(usable) < 2:
        ordering = INSUFFICIENT
    else:
        rates = [tiers[t]["hit_rate_pct"] for t in usable]
        ordering = (
            "monotonic"
            if all(a <= b for a, b in zip(rates, rates[1:]))
            else "non-monotonic"
        )

    return {
        "by_tier": tiers,
        "tiers_with_usable_sample": usable,
        "ordering": ordering,
    }


def reasoning_cross_tab(entries, min_n):
    """Cross-tabulate outcome against whether any thesis leg broke.

    Entries whose legs are all unresolved or unfalsifiable do not enter the
    cross-tab; they are counted separately so a high count stays visible
    instead of being averaged away.
    """
    cells = {
        "right_for_right_reasons": 0,
        "right_for_wrong_reasons": 0,
        "wrong_for_right_reasons": 0,
        "wrong_for_wrong_reasons": 0,
    }
    excluded = []

    for entry in _resolved(entries):
        legs = entry.get("legs") or []
        gradeable = [l for l in legs if l["grade"] in ("held", "broke")]
        if not gradeable:
            excluded.append(entry["id"])
            continue

        any_broke = any(l["grade"] == "broke" for l in gradeable)
        confirmed = entry["outcome"] == "confirmed"

        if confirmed and not any_broke:
            cells["right_for_right_reasons"] += 1
        elif confirmed:
            cells["right_for_wrong_reasons"] += 1
        elif not any_broke:
            cells["wrong_for_right_reasons"] += 1
        else:
            cells["wrong_for_wrong_reasons"] += 1

    confirmed_total = (
        cells["right_for_right_reasons"] + cells["right_for_wrong_reasons"]
    )

    return {
        "cells": cells,
        "in_cross_tab": sum(cells.values()),
        "excluded_no_gradeable_legs": excluded,
        "right_for_wrong_reasons_share_of_confirmed_pct": _rate(
            cells["right_for_wrong_reasons"], confirmed_total, min_n
        ),
    }


def leg_analysis(entries, min_n):
    """Grade tally overall, and break rate by leg position."""
    all_grades = [l["grade"] for e in entries for l in (e.get("legs") or [])]
    by_position = {}

    for entry in entries:
        for leg in entry.get("legs") or []:
            position = leg.get("position")
            if position is None:
                continue
            bucket = by_position.setdefault(
                str(position), {"held": 0, "broke": 0}
            )
            if leg["grade"] in bucket:
                bucket[leg["grade"]] += 1

    positions = {}
    for position, counts in sorted(by_position.items()):
        tested = counts["held"] + counts["broke"]
        positions[position] = {
            "tested_n": tested,
            "broke": counts["broke"],
            "break_rate_pct": _rate(counts["broke"], tested, min_n),
        }

    return {
        "grade_tally": _tally(all_grades, LEG_GRADES),
        "by_position": positions,
    }


def mitigant_analysis(entries, min_n):
    """Failure rate over tested mitigants only; untested reported apart."""
    all_grades = [m["grade"] for e in entries for m in (e.get("mitigants") or [])]
    tally = _tally(all_grades, MITIGANT_GRADES)
    tested = tally["held"] + tally["failed"]

    return {
        "grade_tally": tally,
        "tested_n": tested,
        "failure_rate_pct": _rate(tally["failed"], tested, min_n),
        "note": (
            "Untested mitigants are excluded from the denominator. A high "
            "untested share is normal and is not a finding."
        ),
    }


def probability_calibration(entries, min_n):
    """Brier score and observed-vs-stated bands over probabilistic entries."""
    scored = [
        e
        for e in _resolved(entries)
        if isinstance(e.get("stated_probability"), (int, float))
    ]

    if len(scored) < min_n:
        brier = INSUFFICIENT
    else:
        total = sum(
            (e["stated_probability"] - (1.0 if e["outcome"] == "confirmed" else 0.0))
            ** 2
            for e in scored
        )
        brier = round(total / len(scored), 4)

    bands = {}
    for low, high in PROBABILITY_BANDS:
        label = "{:.0%}-{:.0%}".format(low, high)
        # Bands are half-open except the last, so 1.0 is captured.
        in_band = [
            e
            for e in scored
            if low <= e["stated_probability"] < high
            or (high == 1.0 and e["stated_probability"] == 1.0)
        ]
        confirmed = len([e for e in in_band if e["outcome"] == "confirmed"])
        bands[label] = {
            "n": len(in_band),
            "stated_midpoint_pct": round(100.0 * (low + high) / 2, 1),
            "observed_confirmed_pct": _rate(confirmed, len(in_band), min_n),
        }

    return {
        "scored_n": len(scored),
        "brier_score": brier,
        "uninformative_brier_comparator": UNINFORMATIVE_BRIER,
        "brier_note": (
            "A Brier score of {} is what answering 50% to everything scores. "
            "Higher than that means the stated probabilities point the wrong "
            "way. Read alongside the bands, never alone.".format(
                UNINFORMATIVE_BRIER
            )
        ),
        "bands": bands,
    }


def change_classification(links):
    counts = _tally([l["classification"] for l in links], CHANGE_CLASSES)
    return {
        "total_links": len(links),
        "by_classification": counts,
        "price_driven_links": [
            "{} -> {}".format(l.get("from"), l.get("to"))
            for l in links
            if l["classification"] == "price-driven"
        ],
    }


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------

def compute(data):
    entries = data["entries"]
    links = data.get("links") or []
    min_n = data.get("min_bucket_n", DEFAULT_MIN_BUCKET_N)

    return {
        "scope": data.get("scope"),
        "min_bucket_n": min_n,
        "outcome_summary": outcome_summary(entries),
        "conviction_calibration": conviction_calibration(entries, min_n),
        "reasoning_cross_tab": reasoning_cross_tab(entries, min_n),
        "legs": leg_analysis(entries, min_n),
        "mitigants": mitigant_analysis(entries, min_n),
        "probability_calibration": probability_calibration(entries, min_n),
        "change_classification": change_classification(links),
        "reporting_rule": (
            "Report every '{}' verbatim. Do not substitute a caveated "
            "percentage, merge buckets to reach the floor, or fall back to a "
            "blended rate.".format(INSUFFICIENT)
        ),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Compute calibration figures for graded belief entries."
    )
    parser.add_argument("input", help="path to the graded-entries JSON file")
    parser.add_argument(
        "--pretty", action="store_true", help="indent the JSON output"
    )
    parser.add_argument(
        "--min-bucket-n",
        type=int,
        default=None,
        help="override the minimum sample size per bucket (default {})".format(
            DEFAULT_MIN_BUCKET_N
        ),
    )
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError) as exc:
        print("could not read input: {}".format(exc), file=sys.stderr)
        return 1

    if args.min_bucket_n is not None:
        data["min_bucket_n"] = args.min_bucket_n

    try:
        validate(data)
        result = compute(data)
    except InputError as exc:
        print("invalid input: {}".format(exc), file=sys.stderr)
        return 1

    json.dump(result, sys.stdout, indent=2 if args.pretty else None)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())