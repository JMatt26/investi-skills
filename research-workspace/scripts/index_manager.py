#!/usr/bin/env python3
"""
index_manager.py — deterministic index over a research/ workspace.

The index is never hand-maintained. It is always derived fresh from the
YAML frontmatter of every .md file under the workspace root. This means
the index can never drift from the files on disk: if you're unsure
whether it's current, run `rebuild` — it's cheap and it's the only
correct source of truth.

Frontmatter contract (see references/folder-schema.md for the full spec):

  Every artifact file needs:
    artifact_type: theme_map | screen | belief | coverage | retrospective
    skill:         name of the producing skill
    id:            YYYY-MM-DD-<slug>, unique across the workspace
    date:          ISO date (YYYY-MM-DD)

  Subject-centric artifacts (screen, belief, coverage, retrospective) add:
    subject:       folder key — a ticker (SOFI) or a non-ticker topic
                    slug (hiring-vp-eng)
    is_ticker:     true | false

  Optional on subject-centric artifacts:
    status:        free-form, skill-defined (open/confirmed/falsified/...)
    supersedes:    id of the prior artifact this one replaces

  Theme-centric artifacts (theme_map) add:
    theme:         theme slug
    subjects:      list of subject keys referenced in the watchlist

Usage:
  python3 index_manager.py path --skill belief-journal --subject SOFI \
      --date 2026-08-06 --slug sofi-fintech-view
  python3 index_manager.py path --skill thematic-mapping --theme \
      fintech-unbundling --date 2026-08-06 --slug map

  python3 index_manager.py rebuild [--root research]
  python3 index_manager.py lookup SOFI [--root research]
  python3 index_manager.py list [--theme fintech-unbundling] [--root research]
"""

import argparse
import json
import re
import sys
from pathlib import Path

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
SUBJECT_ARTIFACT_TYPES = {"screen", "belief", "coverage", "retrospective"}
THEME_ARTIFACT_TYPES = {"theme_map"}


def parse_scalar(raw):
    raw = raw.strip()
    if raw == "" or raw.lower() == "null" or raw == "~":
        return None
    if raw.lower() == "true":
        return True
    if raw.lower() == "false":
        return False
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
        return raw[1:-1]
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(item) for item in inner.split(",")]
    return raw


def parse_frontmatter(text):
    """Return (frontmatter_dict, error_or_None). Minimal flat-YAML parser —
    handles `key: value` and `key: [a, b, c]` lines only, which is all this
    contract uses. Deliberately does not pull in a YAML dependency for a
    format this constrained."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None, "no frontmatter block found"
    block = match.group(1)
    data = {}
    for line_no, line in enumerate(block.splitlines(), start=1):
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            return None, f"malformed frontmatter line {line_no}: {line!r}"
        key, _, value = line.partition(":")
        data[key.strip()] = parse_scalar(value)
    return data, None


def load_workspace(root):
    """Walk root for *.md files, parse frontmatter, return
    (records, warnings). Each record carries its source path."""
    records = []
    warnings = []
    if not root.exists():
        return records, [f"root '{root}' does not exist yet — nothing to index"]

    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root)
        text = path.read_text(encoding="utf-8", errors="replace")
        fm, err = parse_frontmatter(text)
        if err:
            warnings.append(f"{rel}: {err} — skipped")
            continue
        artifact_type = fm.get("artifact_type")
        skill = fm.get("skill")
        artifact_id = fm.get("id")
        date = fm.get("date")
        missing = [f for f in ("artifact_type", "skill", "id", "date") if not fm.get(f)]
        if missing:
            warnings.append(f"{rel}: missing required field(s) {missing} — skipped")
            continue

        if artifact_type in SUBJECT_ARTIFACT_TYPES:
            if not fm.get("subject"):
                warnings.append(f"{rel}: artifact_type '{artifact_type}' requires 'subject' — skipped")
                continue
        elif artifact_type in THEME_ARTIFACT_TYPES:
            if not fm.get("theme"):
                warnings.append(f"{rel}: artifact_type 'theme_map' requires 'theme' — skipped")
                continue
        else:
            warnings.append(f"{rel}: unrecognized artifact_type '{artifact_type}' — indexed as-is, but check for a typo")

        fm["_path"] = str(rel)
        records.append(fm)

    return records, warnings


def build_index(root):
    records, warnings = load_workspace(root)

    ids_seen = {}
    for r in records:
        rid = r.get("id")
        if rid in ids_seen:
            warnings.append(
                f"duplicate id '{rid}' in {ids_seen[rid]} and {r['_path']} — "
                f"ids must be unique across the whole workspace"
            )
        else:
            ids_seen[rid] = r["_path"]

    subjects = {}
    themes = {}

    for r in records:
        atype = r.get("artifact_type")
        if atype in SUBJECT_ARTIFACT_TYPES or "subject" in r:
            subj = r["subject"]
            entry = subjects.setdefault(subj, {
                "is_ticker": bool(r.get("is_ticker", False)),
                "artifacts": [],
                "themes": [],
                "last_touched": None,
            })
            entry["artifacts"].append({
                "artifact_type": atype,
                "skill": r.get("skill"),
                "id": r.get("id"),
                "date": r.get("date"),
                "status": r.get("status"),
                "supersedes": r.get("supersedes"),
                "path": r["_path"],
            })
            if entry["last_touched"] is None or r.get("date", "") > entry["last_touched"]:
                entry["last_touched"] = r.get("date")

        if atype in THEME_ARTIFACT_TYPES or "theme" in r:
            theme = r["theme"]
            t_entry = themes.setdefault(theme, {
                "map_path": r["_path"],
                "subjects": list(r.get("subjects") or []),
                "last_touched": r.get("date"),
            })
            if r.get("date", "") >= t_entry["last_touched"]:
                t_entry["map_path"] = r["_path"]
                t_entry["last_touched"] = r.get("date")
                t_entry["subjects"] = list(r.get("subjects") or [])

    # Cross-link: which themes reference which subjects; flag dangling
    # supersedes chains along the way.
    for theme, t in themes.items():
        for subj in t["subjects"]:
            if subj in subjects:
                if theme not in subjects[subj]["themes"]:
                    subjects[subj]["themes"].append(theme)
            else:
                warnings.append(
                    f"theme '{theme}' watchlist references subject '{subj}' "
                    f"which has no artifacts of its own yet"
                )

    for subj, entry in subjects.items():
        artifacts_by_id = {a["id"]: a for a in entry["artifacts"]}
        for a in entry["artifacts"]:
            a["superseded_by"] = None
        for a in entry["artifacts"]:
            sup = a.get("supersedes")
            if sup:
                if sup in artifacts_by_id:
                    artifacts_by_id[sup]["superseded_by"] = a["id"]
                else:
                    warnings.append(
                        f"'{a['id']}' (subject '{subj}') claims to supersede "
                        f"'{sup}', which is not in the index — check for a "
                        f"typo'd id or a missing file"
                    )
        entry["artifacts"].sort(key=lambda a: a["date"])

    index = {
        "root": str(root),
        "subjects": subjects,
        "themes": themes,
        "warnings": warnings,
    }
    return index


def cmd_rebuild(args):
    root = Path(args.root)
    index = build_index(root)
    out_path = root / "_index.json"
    root.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"Rebuilt {out_path}")
    print(f"  subjects: {len(index['subjects'])}")
    print(f"  themes:   {len(index['themes'])}")
    if index["warnings"]:
        print(f"  warnings: {len(index['warnings'])}")
        for w in index["warnings"]:
            print(f"    - {w}")
    else:
        print("  warnings: none")
    return index


def cmd_lookup(args):
    index = cmd_rebuild(argparse.Namespace(root=args.root))
    subj = args.subject
    print()
    if subj not in index["subjects"]:
        print(f"No artifacts found for '{subj}'.")
        if index["subjects"]:
            print("Known subjects: " + ", ".join(sorted(index["subjects"])))
        return
    entry = index["subjects"][subj]
    print(f"{subj}  (last touched {entry['last_touched']})")
    if entry["themes"]:
        print(f"  themes: {', '.join(entry['themes'])}")
    print("  artifacts:")
    for a in entry["artifacts"]:
        flag = " [SUPERSEDED]" if a["superseded_by"] else ""
        status = f" status={a['status']}" if a.get("status") else ""
        print(f"    {a['date']}  {a['skill']:<26} {a['id']}{status}{flag}")
        print(f"        {a['path']}")


def cmd_list(args):
    index = cmd_rebuild(argparse.Namespace(root=args.root))
    print()
    if args.theme:
        t = index["themes"].get(args.theme)
        if not t:
            print(f"No theme '{args.theme}' found.")
            print("Known themes: " + ", ".join(sorted(index["themes"])))
            return
        print(f"Theme: {args.theme}  (last touched {t['last_touched']})")
        print(f"  map: {t['map_path']}")
        print(f"  subjects: {', '.join(t['subjects']) if t['subjects'] else '(none)'}")
        return

    if index["themes"]:
        print("Themes:")
        for theme, t in sorted(index["themes"].items()):
            print(f"  {theme:<28} {len(t['subjects'])} subjects, last touched {t['last_touched']}")
        print()
    print("Subjects:")
    for subj, entry in sorted(index["subjects"].items()):
        kind = "ticker" if entry["is_ticker"] else "topic"
        print(f"  {subj:<12} ({kind})  {len(entry['artifacts'])} artifacts, last touched {entry['last_touched']}")


def cmd_path(args):
    root = Path(args.root)
    if args.theme:
        if not args.slug:
            print("error: --slug is required", file=sys.stderr)
            sys.exit(1)
        p = root / "_themes" / args.theme / f"{args.date}-{args.slug}.md"
    else:
        if not (args.skill and args.subject and args.slug):
            print("error: --skill, --subject, and --slug are required for a subject-centric path", file=sys.stderr)
            sys.exit(1)
        p = root / args.subject / args.skill / f"{args.date}-{args.slug}.md"
    print(p)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_rebuild = sub.add_parser("rebuild", help="Rebuild _index.json from every file's frontmatter")
    p_rebuild.add_argument("--root", default="research")
    p_rebuild.set_defaults(func=cmd_rebuild)

    p_lookup = sub.add_parser("lookup", help="Show everything indexed for one subject (ticker or topic)")
    p_lookup.add_argument("subject")
    p_lookup.add_argument("--root", default="research")
    p_lookup.set_defaults(func=cmd_lookup)

    p_list = sub.add_parser("list", help="List all subjects, or all themes, or one theme's watchlist")
    p_list.add_argument("--theme", default=None)
    p_list.add_argument("--root", default="research")
    p_list.set_defaults(func=cmd_list)

    p_path = sub.add_parser("path", help="Print the canonical path for a new artifact (does not write anything)")
    p_path.add_argument("--skill", help="Producing skill name, e.g. belief-journal")
    p_path.add_argument("--subject", help="Ticker or topic slug (subject-centric artifacts)")
    p_path.add_argument("--theme", help="Theme slug (theme-centric artifacts)")
    p_path.add_argument("--date", required=True, help="YYYY-MM-DD")
    p_path.add_argument("--slug", required=True)
    p_path.add_argument("--root", default="research")
    p_path.set_defaults(func=cmd_path)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
