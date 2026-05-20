#!/usr/bin/env python3
"""PostToolUse hook: detect new tool stubs written into skill subdirectories.

When a Write targets .claude/skills/*/tools/*.py, exits 2 with a message
instructing Claude to add an entry to .claude/tool_registry.json.
Exits 0 for all other writes.
"""

from __future__ import annotations

import fnmatch
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
_TOOLS_GLOB = ".claude/skills/*/tools/*.py"


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    if payload.get("tool_name") not in ("Write", "Edit"):
        return 0

    file_path = payload.get("tool_input", {}).get("file_path", "")
    if not file_path:
        return 0

    try:
        rel = Path(file_path).resolve().relative_to(REPO).as_posix()
    except ValueError:
        return 0

    if not fnmatch.fnmatch(rel, _TOOLS_GLOB):
        return 0

    print(
        f"New tool stub written: {rel}\n"
        f"Update .claude/tool_registry.json — add an entry with fields: "
        f"name, description, skill, file_path, function_signature, date_added.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
