#!/usr/bin/env python3
"""Mechanical edits to the research tree. Ids, sibling letters and timestamps are owned here.

Usage (from the repo root):
  python3 workflow/manage_research_tree.py pose --parent <id|~> --slug <slug> --question "<text>" --candidates a,b
  python3 workflow/manage_research_tree.py conclude <id> --conclusion <id> [--basis B] [--reason R] [--bypassed-by C]
  python3 workflow/manage_research_tree.py reword <id> --question "<text>"
  python3 workflow/manage_research_tree.py touch <path/to/question.md>

RESEARCH_TREE_NOW=<ISO-8601> fixes the clock (tests).
"""
import argparse
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True  # keep workflow/ free of __pycache__
from validate_research_tree import (  # noqa: E402
    BASES, DEFINITIONS, QUESTIONS, ROOT, SEGMENT, children, effective_children, load_tree)

DEFS_PATH = "./" + str(DEFINITIONS.relative_to(ROOT))
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def now():
    return os.environ.get("RESEARCH_TREE_NOW") or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def letter(i):
    """0 -> a, 25 -> z, 26 -> aa."""
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(97 + r) + s
    return s


def fail(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def pose(args):
    definitions, nodes, _ = load_tree()
    if not SLUG.match(args.slug):
        fail(f"slug '{args.slug}' is not kebab-case")
    candidates = [c.strip() for c in args.candidates.split(",") if c.strip()]
    if len(candidates) < 2:
        fail("need >= 2 candidate conclusions")
    for c in candidates:
        if c not in definitions:
            fail(f"candidate '{c}' is not defined in {DEFS_PATH}")
        if definitions[c].get("always-available"):
            fail(f"candidate '{c}' is always-available; do not list it")

    if args.parent == "~":
        if any(d.is_dir() for d in QUESTIONS.glob("*")):
            fail("root already exists")
        target, parent_id, path = QUESTIONS / f"1a-{args.slug}", "~", "1a"
    else:
        parent = nodes.get(args.parent)
        if parent is None:
            fail(f"no question '{args.parent}'")
        if parent["c"] is not None:
            fail(f"'{args.parent}' is concluded; pose under an open question")
        used = [segs[-1][1] for s in children(nodes, args.parent)
                if (segs := SEGMENT.findall(str(nodes[s]["q"].get("path") or "")))]
        i = 0
        while letter(i) in used:
            i += 1
        target, parent_id = parent["dir"] / "questions" / f"{parent['depth'] + 1}{letter(i)}-{args.slug}", args.parent
        path = f"{parent['q'].get('path')}{parent['depth'] + 1}{letter(i)}"

    if target.name in nodes:
        fail(f"id '{target.name}' already exists")
    target.mkdir(parents=True)
    t = now()
    (target / "question.md").write_text(
        f"---\nid: {target.name}\npath: {path}\nquestion: \"{' '.join(args.question.split())}\"\nparent: {parent_id}\n"
        f"candidate-conclusions: [{', '.join(candidates)}]\n"
        f"candidate-conclusion-definitions-path: {DEFS_PATH}\n"
        f"opened: {t}\nupdated: {t}\n---\n\n## Rationale\n\n")
    print(target.relative_to(ROOT))


def conclude(args):
    definitions, nodes, _ = load_tree()
    n = nodes.get(args.id)
    if n is None:
        fail(f"no question '{args.id}'")
    if n["c"] is not None:
        fail(f"'{args.id}' is already concluded")
    spec = definitions.get(args.conclusion)
    if spec is None:
        fail(f"conclusion '{args.conclusion}' is not defined in {DEFS_PATH}")
    candidates = n["q"].get("candidate-conclusions") or []
    if args.conclusion not in candidates and not spec.get("always-available"):
        fail(f"'{args.conclusion}' is not a candidate for '{args.id}'")
    requires = spec.get("requires") or []
    for field, value in (("basis", args.basis), ("reason", args.reason), ("bypassed_by", args.bypassed_by)):
        if field in requires and not value:
            fail(f"conclusion '{args.conclusion}' requires --{field.replace('_', '-')}")
    if args.basis and args.basis not in BASES:
        fail(f"basis must be one of {', '.join(BASES)}")
    if args.conclusion != "bypassed":
        still_open = [c for c in effective_children(nodes, args.id) if nodes[c]["c"] is None]
        if still_open:
            fail(f"effective children still open: {', '.join(still_open)}")

    lines = [f"id: {args.id}", f"candidate-conclusion-definitions-path: {DEFS_PATH}",
             f"conclusion: {args.conclusion}"]
    if args.basis:
        lines.append(f"basis: {args.basis}")
    lines.append(f"concluded: {now()}")
    if args.reason:
        lines.append(f"reason: \"{' '.join(args.reason.split())}\"")
    if args.bypassed_by:
        lines.append(f"bypassed_by: {args.bypassed_by}")
    body = "\n## Finding\n\n" if "finding" in requires else ""
    if args.basis == "synthesis":
        body += "\n## Synthesis\n\n"
    path = n["dir"] / "conclusion.md"
    path.write_text("---\n" + "\n".join(lines) + "\n---\n" + body)
    print(path.relative_to(ROOT))


def reword(args):
    _, nodes, _ = load_tree()
    n = nodes.get(args.id)
    if n is None:
        fail(f"no question '{args.id}'")
    if n["c"] is not None:
        fail(f"'{args.id}' is concluded; its question is frozen (bypass or abandon it instead)")
    path = n["dir"] / "question.md"
    text = path.read_text()
    line = f"question: \"{' '.join(args.question.split())}\""
    text = re.sub(r"^question: .*$", lambda _: line, text, count=1, flags=re.M)
    text = re.sub(r"^updated: .*$", f"updated: {now()}", text, count=1, flags=re.M)
    path.write_text(text)
    print(path.relative_to(ROOT))


def touch(args):
    path = Path(args.path).resolve()
    if path.name != "question.md" or (path.parent / "conclusion.md").exists():
        return
    text = path.read_text()
    new = re.sub(r"^updated: .*$", f"updated: {now()}", text, count=1, flags=re.M)
    if new != text:
        path.write_text(new)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pose")
    p.add_argument("--parent", required=True)
    p.add_argument("--slug", required=True)
    p.add_argument("--question", required=True)
    p.add_argument("--candidates", required=True)
    p.set_defaults(func=pose)
    c = sub.add_parser("conclude")
    c.add_argument("id")
    c.add_argument("--conclusion", required=True)
    c.add_argument("--basis")
    c.add_argument("--reason")
    c.add_argument("--bypassed-by", dest="bypassed_by")
    c.set_defaults(func=conclude)
    r = sub.add_parser("reword")
    r.add_argument("id")
    r.add_argument("--question", required=True)
    r.set_defaults(func=reword)
    t = sub.add_parser("touch")
    t.add_argument("path")
    t.set_defaults(func=touch)
    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
