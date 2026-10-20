#!/usr/bin/env python3
"""Claude Code SessionStart / UserPromptSubmit hook: catch tree inconsistencies made outside Claude.

Wired in .claude/settings.json. Runs validate_research_tree.py; silent when the tree is
valid. On violations it warns the user and hands the violations to Claude as context.
Never blocks the prompt.
"""
import json
import subprocess
import sys
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parent


def main():
    try:
        event = json.load(sys.stdin).get("hook_event_name", "UserPromptSubmit")
    except (json.JSONDecodeError, AttributeError):
        event = "UserPromptSubmit"
    result = subprocess.run([sys.executable, str(WORKFLOW / "validate_research_tree.py")],
                            capture_output=True, text=True)
    if result.returncode == 0:
        return 0
    lines = result.stdout.strip().splitlines()
    print(json.dumps({
        "systemMessage": f"research tree: {lines[-1]}",
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": "validate_research_tree.py reports violations (likely an edit made "
                                 "outside Claude):\n" + "\n".join(lines),
        },
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
