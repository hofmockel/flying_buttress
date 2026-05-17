#!/usr/bin/env python3
"""PostToolUse(Write|Edit) hook: run make fmt on source file changes.

Runs silently on success. Writes make output to stderr only on failure.
Always exits 0 — format hooks never block tool completion.

Triggered by Write or Edit on source files (.py, .ts, .tsx, .js, .jsx).
Skips documentation, config, and template files.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent

SOURCE_EXTS = frozenset({".py", ".ts", ".tsx", ".js", ".jsx"})


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
    if not file_path or Path(file_path).suffix not in SOURCE_EXTS:
        return 0

    result = subprocess.run(
        ["make", "fmt"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    if result.returncode != 0:
        print(result.stdout + result.stderr, file=sys.stderr, end="")

    return 0


if __name__ == "__main__":
    sys.exit(main())
