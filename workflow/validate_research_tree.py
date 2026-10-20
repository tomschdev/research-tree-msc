#!/usr/bin/env python3
"""Validate a research tree against workflow/methodology.md.

Usage (from the repo root):
  python3 workflow/validate_research_tree.py     # one line per violation; exit 1 if any

A node is research-tree/questions/.../<id>/question.md. It is concluded when a
conclusion.md sits beside it. Children live in <id>/questions/<child>/.

Stdlib only. Parses the block-YAML subset used by the definitions file and frontmatter.
"""
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUESTIONS = ROOT / "research-tree" / "questions"
DEFINITIONS = ROOT / "workflow" / "candidate-conclusion-definitions.yaml"
NAME = re.compile(r"^(\d+[a-z]+)-[a-z0-9]+(?:-[a-z0-9]+)*$")
PATH = re.compile(r"^(?:\d+[a-z]+)+$")
SEGMENT = re.compile(r"(\d+)([a-z]+)")
BASES = ("literature", "activity", "synthesis")
SYNC_HINT = " (run python3 workflow/sync_research_tree_paths.py)"
QUESTION_FIELDS = ["id", "path", "question", "parent", "candidate-conclusions",
                   "candidate-conclusion-definitions-path", "opened", "updated"]


# --- minimal YAML (block mappings, scalars, inline lists, ~ for null) ---

def parse_scalar(raw):
    raw = raw.strip()
    if raw in ("", "~", "null"):
        return None
    if raw in ("true", "false"):
        return raw == "true"
    if raw.startswith("[") and raw.endswith("]"):
        return [s.strip() for s in raw[1:-1].split(",") if s.strip()]
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "'\"":
        return raw[1:-1]
    return raw


def parse_yaml(text):
    lines = []
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not re.match(r"^\s*[\w-]+:\s*[\"']", line):  # quoted values may hold " # "
            line = re.sub(r"\s+#\s.*$", "", line)  # trailing comment
        lines.append((len(line) - len(line.lstrip()), line.strip()))

    def block(i, indent):
        out = {}
        while i < len(lines) and lines[i][0] == indent:
            key, _, value = lines[i][1].partition(":")
            i += 1
            if value.strip():
                out[key.strip()] = parse_scalar(value)
            elif i < len(lines) and lines[i][0] > indent:
                out[key.strip()], i = block(i, lines[i][0])
            else:
                out[key.strip()] = None
        return out, i

    return block(0, 0)[0] if lines else {}


def load_markdown(path):
    """Return (frontmatter dict, body) or (None, text) if there is no frontmatter."""
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return None, text
    return parse_yaml(m.group(1)), m.group(2)


def section(body, name):
    m = re.search(rf"^## {name}\s*$(.*?)(?=^## |\Z)", body, re.S | re.M)
    return m.group(1).strip() if m else ""


def parse_time(value):
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def git(*args):
    """Run git in the repo; return stripped stdout, or "" if git fails."""
    r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def frozen_violation(node):
    """Rule 5: question.md must not change once conclusion.md is committed.

    `id`, `parent` and `path` are exempt: they record where the question sits, and
    change when a subtree is reparented.
    """
    q, c = node["dir"] / "question.md", node["dir"] / "conclusion.md"
    added = git("log", "--diff-filter=A", "--format=%H", "-1", "--", str(c))
    if not added:
        return None  # conclusion not committed yet; the question may change in the same commit
    then = git("show", f"{added}:./{q.relative_to(ROOT)}")  # ./ = relative to ROOT, not the git top
    if not then:
        return None  # question.md not present at that commit under this name

    def substance(text):
        return re.sub(r"^(id|parent|path): .*\n?", "", text.strip(), flags=re.M)

    if substance(then) != substance(q.read_text()):
        return "question.md changed after conclusion.md was committed"
    return None


# --- load ---

def load_tree():
    """Walk the nested questions/ folders. Returns (definitions, nodes, errors).

    nodes[id] = {"q": question frontmatter, "c": conclusion frontmatter or None,
                 "c_body": str, "dir": Path, "rel": str, "parent": derived parent id,
                 "depth": int}
    """
    definitions = parse_yaml(DEFINITIONS.read_text())
    nodes, errors = {}, []

    def walk(qdir, parent, depth):
        if not qdir.is_dir():
            return
        dirs = sorted(d for d in qdir.iterdir() if d.is_dir())
        if parent is None and len(dirs) != 1:
            errors.append(f"{qdir.relative_to(ROOT)}: rule 1: expected exactly one root question, found {len(dirs)}")
        for d in dirs:
            rel = d.relative_to(ROOT)
            if not (d / "question.md").is_file():
                errors.append(f"{rel}: rule 1: every directory under questions/ must hold question.md")
                continue
            if not NAME.match(d.name):
                errors.append(f"{rel}: rule 2: name '{d.name}' is not <depth><letter>-<slug>")
            if d.name in nodes:
                errors.append(f"{rel}: rule 2: id '{d.name}' already used at {nodes[d.name]['rel']}")
                continue
            q, _ = load_markdown(d / "question.md")
            if q is None:
                errors.append(f"{rel}/question.md: frontmatter missing or malformed")
                continue
            c, c_body = (None, "")
            if (d / "conclusion.md").is_file():
                c, c_body = load_markdown(d / "conclusion.md")
                if c is None:
                    errors.append(f"{rel}/conclusion.md: frontmatter missing or malformed")
            nodes[d.name] = dict(q=q, c=c, c_body=c_body, dir=d, rel=str(rel), parent=parent, depth=depth)
            walk(d / "questions", d.name, depth + 1)

    walk(QUESTIONS, None, 1)
    return definitions, nodes, errors


def children(nodes, nid):
    return [cid for cid, n in nodes.items() if n["parent"] == nid]


def effective_children(nodes, nid):
    """Children, with each bypassed child replaced by its bypassed_by (recursively)."""
    out = []
    for cid in children(nodes, nid):
        seen = set()
        while cid in nodes and (nodes[cid]["c"] or {}).get("conclusion") == "bypassed" and cid not in seen:
            seen.add(cid)
            cid = nodes[cid]["c"].get("bypassed_by")
        if cid in nodes:
            out.append(cid)
    return out


# --- validate ---

def validate(definitions, nodes):
    errs = []
    in_git = git("rev-parse", "--is-inside-work-tree") == "true"
    expected_defs = "./" + str(DEFINITIONS.relative_to(ROOT))

    for nid, n in nodes.items():
        q, c = n["q"], n["c"]

        def err(rule, msg, f="question.md"):
            errs.append(f"{n['rel']}/{f}: rule {rule}: {msg}")

        # rule 3 — question.md frontmatter
        for field in QUESTION_FIELDS:
            if field not in q:
                err(3, f"missing field '{field}'")
        if list(q)[:len(QUESTION_FIELDS)] != QUESTION_FIELDS:
            err(3, f"fields out of order; expected {', '.join(QUESTION_FIELDS)}")
        if q.get("id") != nid:
            err(3, f"id '{q.get('id')}' != directory name '{nid}'")

        # rule 2 — path = parent's path + <depth><letter>, letter unique among siblings
        path = str(q.get("path") or "")
        parent_path = str(nodes[n["parent"]]["q"].get("path") or "") if n["parent"] else ""
        if not PATH.match(path):
            err(2, f"path '{path}' is not a sequence of <depth><letter>{SYNC_HINT}")
        elif SEGMENT.findall(path)[:-1] != SEGMENT.findall(parent_path):
            err(2, f"path '{path}' does not extend the parent's path '{parent_path}'{SYNC_HINT}")
        elif int(SEGMENT.findall(path)[-1][0]) != n["depth"]:
            err(2, f"path '{path}' ends at depth {SEGMENT.findall(path)[-1][0]} "
                   f"but nesting depth is {n['depth']}{SYNC_HINT}")
        else:
            clash = [s for s in children(nodes, n["parent"]) if s != nid and nodes[s]["q"].get("path") == path]
            if clash:
                err(2, f"path '{path}' also used by sibling '{clash[0]}'{SYNC_HINT}")
            m = NAME.match(nid)
            if m and m.group(1) != SEGMENT.findall(path)[-1][0] + SEGMENT.findall(path)[-1][1]:
                err(2, f"id prefix '{m.group(1)}' does not match the end of path '{path}'{SYNC_HINT}")
        declared = q.get("parent")
        if declared != n["parent"]:
            err(3, f"parent '{declared}' != enclosing question '{n['parent']}'{SYNC_HINT}")
            if declared in nodes:
                want = str(nodes[declared]["q"].get("path") or "")
                if SEGMENT.findall(path)[:-1] != SEGMENT.findall(want):
                    err(2, f"path '{path}' does not extend declared parent '{declared}' path '{want}'{SYNC_HINT}")
        if not q.get("question"):
            err(3, "question text is empty")
        if q.get("candidate-conclusion-definitions-path") != expected_defs:
            err(3, f"candidate-conclusion-definitions-path must be '{expected_defs}'")
        candidates = q.get("candidate-conclusions") or []
        if not isinstance(candidates, list) or len(candidates) < 2:
            err(3, "candidate-conclusions needs >= 2 ids")
            candidates = []
        for cand in candidates:
            if cand not in definitions:
                err(3, f"candidate '{cand}' not defined in {expected_defs}")
            elif definitions[cand].get("always-available"):
                err(3, f"candidate '{cand}' is always-available; do not list it")
        opened, updated = parse_time(q.get("opened")), parse_time(q.get("updated"))
        if not opened or not updated:
            err(3, "opened and updated must be ISO-8601 timestamps")
        elif updated < opened:
            err(3, "updated is before opened")

        if c is None:
            continue

        # rule 4 — conclusion.md frontmatter
        def cerr(rule, msg):
            err(rule, msg, "conclusion.md")

        # rule 5 — question.md frozen once concluded (skipped outside git)
        frozen = frozen_violation(n) if in_git else None
        if frozen:
            err(5, frozen)

        if c.get("id") != nid:
            cerr(4, f"id '{c.get('id')}' != directory name '{nid}'")
        if c.get("candidate-conclusion-definitions-path") != expected_defs:
            cerr(4, f"candidate-conclusion-definitions-path must be '{expected_defs}'")
        conclusion = c.get("conclusion")
        spec = definitions.get(conclusion)
        if not spec:
            cerr(4, f"conclusion '{conclusion}' not defined in {expected_defs}")
            continue
        if conclusion not in candidates and not spec.get("always-available"):
            cerr(4, f"conclusion '{conclusion}' is not one of this question's candidate-conclusions")
        for req in spec.get("requires") or []:
            present = section(n["c_body"], "Finding") if req == "finding" else c.get(req)
            if not present:
                cerr(4, f"conclusion '{conclusion}' requires '{req}'")
        concluded = parse_time(c.get("concluded"))
        if not concluded:
            cerr(4, "concluded must be an ISO-8601 timestamp")
        elif opened and concluded < opened:
            cerr(4, "concluded is before opened")

        # rule 6 — no conclusion while an effective child is open
        effective = effective_children(nodes, nid)
        if conclusion != "bypassed":
            for cid in effective:
                if nodes[cid]["c"] is None:
                    cerr(6, f"concluded while effective child '{cid}' has no conclusion.md")

        # rule 7 — bypass target
        if conclusion == "bypassed":
            by = c.get("bypassed_by")
            if by not in children(nodes, nid):
                cerr(7, f"bypassed_by '{by}' is not a child")

        # rule 8 — basis
        basis = c.get("basis")
        if basis is not None:
            if basis not in BASES:
                cerr(8, f"basis '{basis}' not one of {', '.join(BASES)}")
            elif (basis == "synthesis") != bool(effective):
                cerr(8, "basis is synthesis exactly when the question has effective children")

        # rule 9 — synthesis weighs every effective child
        if basis == "synthesis":
            synth = section(n["c_body"], "Synthesis")
            for cid in effective:
                if not re.search(rf"^- (relied on|discounted): {re.escape(cid)}\b", synth, re.M):
                    cerr(9, f"## Synthesis does not weigh effective child '{cid}'")

    return errs


def main():
    definitions, nodes, errors = load_tree()
    errors += validate(definitions, nodes)
    for e in errors:
        print(e)
    concluded = sum(1 for n in nodes.values() if n["c"])
    print(f"{len(nodes)} questions ({concluded} concluded), {len(errors)} violations")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
