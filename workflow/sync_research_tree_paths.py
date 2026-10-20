#!/usr/bin/env python3
"""Make the folder nesting follow each question's `parent` field, then recompute every `path` and id.

Usage (from the repo root):
  python3 workflow/sync_research_tree_paths.py

Run by workflow/on_edit_hook.py after any question.md edit. When a question's `parent`
names a different question than the folder it sits in, the folder is moved (git mv when
tracked) into the declared parent's questions/. Then `path` is recomputed top-down:
parent's path + <depth><letter>. Questions already in place keep their letter; a moved
question (or one with a hand-edited path) takes the next free letter among its siblings.
The id (= directory name) follows as <depth><letter>-<slug>; a renamed question's
references are rewritten (`id`, children's `parent`, `bypassed_by`, `## Synthesis` lines).
Idempotent; a no-op when nothing moved.
"""
import re
import subprocess
import sys

sys.dont_write_bytecode = True  # keep workflow/ free of __pycache__
from validate_research_tree import ROOT, children, load_tree  # noqa: E402
from manage_research_tree import letter  # noqa: E402


def fail(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def move(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--", str(src)],
                             capture_output=True, text=True).stdout.strip()
    if tracked:
        subprocess.run(["git", "-C", str(ROOT), "mv", str(src), str(dst)], check=True)
    else:
        src.rename(dst)
    old_questions = src.parent
    if old_questions.name == "questions" and not any(old_questions.iterdir()):
        old_questions.rmdir()


def ancestors(nodes, nid):
    out = []
    while nodes[nid]["parent"] is not None:
        nid = nodes[nid]["parent"]
        out.append(nid)
    return out


def reparent():
    """Move every question whose declared parent differs from its enclosing question."""
    moved = []
    while True:
        _, nodes, _ = load_tree()
        stray = [nid for nid, n in nodes.items()
                 if n["parent"] is not None and n["q"].get("parent") != n["parent"]]
        if not stray:
            return moved
        nid = stray[0]
        target = nodes[nid]["q"].get("parent")
        if target is None:
            fail(f"{nid}: parent is ~ but the tree already has a root")
        if target not in nodes:
            fail(f"{nid}: parent '{target}' is not a question")
        if target == nid or nid in ancestors(nodes, target):
            fail(f"{nid}: parent '{target}' would make a cycle")
        move(nodes[nid]["dir"], nodes[target]["dir"] / "questions" / nid)
        moved.append(f"{nid}: {nodes[nid]['parent']} -> {target}")


def slug(nid):
    return re.sub(r"^\d+[a-z]+-", "", nid)


def set_field(text, field, value, after=None):
    if re.search(rf"^{field}: .*$", text, re.M):
        return re.sub(rf"^{field}: .*$", lambda _: f"{field}: {value}", text, count=1, flags=re.M)
    return re.sub(rf"^({after}: .*)$", lambda m: f"{m.group(1)}\n{field}: {value}", text, count=1, flags=re.M)


def sync_paths():
    """Recompute `path` and id for every question; return a line per change."""
    _, nodes, _ = load_tree()
    want = {}

    def visit(pid, prefix, depth):
        kids = children(nodes, pid)
        # Siblings already under this prefix at this depth keep their letter; the rest
        # (moved or hand-edited) take the next free one, oldest first.
        used, rest = set(), []
        for k in kids:
            m = re.fullmatch(rf"{re.escape(prefix)}{depth}([a-z]+)", str(nodes[k]["q"].get("path") or ""))
            if m and m.group(1) not in used:
                used.add(m.group(1))
                want[k] = m.group(0)
            else:
                rest.append(k)
        for k in sorted(rest, key=lambda k: str(nodes[k]["q"].get("opened"))):
            i = 0
            while letter(i) in used:
                i += 1
            used.add(letter(i))
            want[k] = f"{prefix}{depth}{letter(i)}"
        for k in kids:
            visit(k, want[k], depth + 1)

    visit(None, "", 1)
    rename = {nid: re.findall(r"\d+[a-z]+", path)[-1] + "-" + slug(nid) for nid, path in want.items()}
    rename = {old: new for old, new in rename.items() if old != new}
    taken = set(nodes) - set(rename)
    for old, new in rename.items():
        if new in taken:
            fail(f"{old}: would be renamed to '{new}', which is already an id")
        taken.add(new)

    def ref(value):
        return rename.get(value, value)

    changed = []
    for nid, n in nodes.items():
        q = n["dir"] / "question.md"
        text = before = q.read_text()
        text = set_field(text, "path", want[nid], after="id")
        text = set_field(text, "id", ref(nid))
        if n["parent"] is not None:
            text = set_field(text, "parent", ref(n["parent"]))
        if text != before:
            q.write_text(text)
            changed.append(f"{nid}: path {n['q'].get('path')} -> {want[nid]}"
                           + (f", id -> {rename[nid]}" if nid in rename else ""))
        c = n["dir"] / "conclusion.md"
        if c.is_file() and rename:
            text = before = c.read_text()
            text = set_field(text, "id", ref(nid))
            if (n["c"] or {}).get("bypassed_by"):
                text = set_field(text, "bypassed_by", ref(n["c"]["bypassed_by"]))
            text = re.sub(r"^(- (?:relied on|discounted): )(\S+)", lambda m: m.group(1) + ref(m.group(2)),
                          text, flags=re.M)
            if text != before:
                c.write_text(text)
    # Deepest first, so each source path is still valid when it is renamed.
    for old in sorted(rename, key=lambda k: -nodes[k]["depth"]):
        move(nodes[old]["dir"], nodes[old]["dir"].parent / rename[old])
    return changed


def main():
    for line in reparent() + sync_paths():
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
