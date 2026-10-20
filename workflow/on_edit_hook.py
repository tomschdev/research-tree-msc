#!/usr/bin/env python3
"""Claude Code PostToolUse hook: keep `updated` current, follow `parent` changes, validate.

Wired in .claude/settings.json. Reads the hook payload on stdin and acts only on
research-tree/**/question.md and conclusion.md. After a question.md edit it runs
sync_research_tree_paths.py, which moves a question whose `parent` changed and
recomputes `path` down the tree. Exit 2 sends errors and violations to Claude.
"""
import json
import subprocess
import sys
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parent
QUESTIONS = (WORKFLOW.parent / "research-tree" / "questions").resolve()


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    file_path = (payload.get("tool_input") or {}).get("file_path")
    if not file_path:
        return 0
    path = Path(file_path).resolve()
    if path.name not in ("question.md", "conclusion.md") or QUESTIONS not in path.parents:
        return 0
    if path.name == "question.md":
        subprocess.run([sys.executable, str(WORKFLOW / "manage_research_tree.py"), "touch", str(path)])
        sync = subprocess.run([sys.executable, str(WORKFLOW / "sync_research_tree_paths.py")],
                              capture_output=True, text=True)
        if sync.returncode != 0:
            print(sync.stderr, file=sys.stderr, end="")
            return 2
    result = subprocess.run([sys.executable, str(WORKFLOW / "validate_research_tree.py")],
                            capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout, file=sys.stderr, end="")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
