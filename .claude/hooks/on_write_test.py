#!/usr/bin/env python3
"""PostToolUse(Write|Edit) hook: run make test when a test file changes.

Triggered only when a test file is modified — not on every source edit.
Writes test output to stderr on failure. Always exits 0.

Test file patterns: test_*.py, *_test.py, *.test.ts, *.spec.ts,
                    *.test.js, *.spec.js
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent

_TEST_PATTERNS = re.compile(
    r"(^test_.+\.py$|.+_test\.py$|.+\.test\.(ts|tsx|js|jsx)$|.+\.spec\.(ts|tsx|js|jsx)$)"
)


def is_test_file(path: str) -> bool:
    return bool(_TEST_PATTERNS.match(Path(path).name))


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    if payload.get("tool_name") not in ("Write", "Edit"):
        return 0

    file_path = payload.get("tool_input", {}).get("file_path") or payload.get(
        "tool_input", {}
    ).get("path", "")
    if not file_path or not is_test_file(file_path):
        return 0

    result = subprocess.run(
        ["make", "test"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    # Always surface test output so the developer sees pass/fail immediately
    output = result.stdout + result.stderr
    if output.strip():
        print(output, file=sys.stderr, end="")

    return 0


if __name__ == "__main__":
    sys.exit(main())
