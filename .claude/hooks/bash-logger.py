#!/usr/bin/env python3
"""PostToolUse hook: log Bash commands and skeletons for pattern analysis.

Reads the Bash tool payload from stdin, extracts a command skeleton (base
command + subcommand + flags, no positional args or quoted values), and
appends a JSONL record to the state bash-log file.

Skeleton algorithm:
  - Token 0 (base command): always kept.
  - Token 1: kept as subcommand if it has no leading dash, no '=', no path
    separators, and the base command is not an interpreter.
  - Remaining tokens: flag tokens (leading dash) are kept; their immediate
    non-flag value is dropped. Positional args and KEY=VALUE tokens dropped.
  - Interpreter-only skeletons (e.g. 'python3' with no flags) are ambiguous.

State dir is overridable via BUTTRESS_STATE_DIR env var (used by tests).
"""

from __future__ import annotations

import json
import os
import shlex
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent

_state_env = os.environ.get("BUTTRESS_STATE_DIR")
STATE_DIR = Path(_state_env) if _state_env else REPO / ".claude" / "state"

_INTERPRETERS = frozenset({"python3", "python", "node", "ruby", "perl", "bash", "sh"})


def extract_skeleton(command: str) -> tuple[str, bool]:
    """Return (skeleton, is_ambiguous)."""
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()

    if not tokens:
        return "", True

    base = tokens[0]
    kept = [base]

    # Subcommand: keep token 1 if it looks like a word, not a path or interpreter arg
    if (
        len(tokens) > 1
        and not tokens[1].startswith("-")
        and "=" not in tokens[1]
        and "/" not in tokens[1]
        and "." not in tokens[1]
        and base not in _INTERPRETERS
    ):
        kept.append(tokens[1])
        start = 2
    else:
        start = 1

    i = start
    while i < len(tokens):
        tok = tokens[i]
        if tok.startswith("-"):
            kept.append(tok)
            # Drop the flag's value if the next token is not itself a flag
            if (
                i + 1 < len(tokens)
                and not tokens[i + 1].startswith("-")
                and "=" not in tokens[i + 1]
            ):
                i += 2
                continue
        i += 1

    skeleton = " ".join(kept)
    is_ambiguous = len(kept) == 1 and base in _INTERPRETERS
    return skeleton, is_ambiguous


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    if payload.get("tool_name") != "Bash":
        return 0

    command = payload.get("tool_input", {}).get("command", "")
    if not command:
        return 0

    skeleton, _ = extract_skeleton(command)
    if not skeleton:
        return 0

    active_skill_file = STATE_DIR / "active_skill"
    try:
        active_skill = active_skill_file.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        active_skill = ""

    record = {
        "ts": time.time(),
        "command": command,
        "skeleton": skeleton,
        "active_skill": active_skill,
    }

    log = STATE_DIR / "bash-log.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
