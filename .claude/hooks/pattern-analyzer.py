#!/usr/bin/env python3
"""Stop hook: analyze Bash command patterns and queue tool promotion suggestions.

Reads bash-log.jsonl, groups by (skeleton, active_skill), and appends entries
to promote_queue.md when a skeleton reaches BASH_PROMOTE_THRESHOLD occurrences.

Ambiguous skeletons (multiple skills, or interpreter-only) get status
'needs-confirmation' so Claude asks the dev before queuing a tool name.
Skeletons already present in the queue with non-dismissed status are skipped.
Dismissed entries are allowed to re-appear if the pattern recurs.

State dir overridable via BUTTRESS_STATE_DIR; queue file via BUTTRESS_QUEUE_FILE.
"""

from __future__ import annotations

import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "tools"))

try:
    from search_config import BASH_PROMOTE_THRESHOLD
except ImportError:
    BASH_PROMOTE_THRESHOLD = 5

_state_env = os.environ.get("BUTTRESS_STATE_DIR")
STATE_DIR = Path(_state_env) if _state_env else REPO / ".claude" / "state"

_queue_env = os.environ.get("BUTTRESS_QUEUE_FILE")
QUEUE_FILE = Path(_queue_env) if _queue_env else REPO / ".claude" / "promote_queue.md"

_INTERPRETERS = frozenset({"python3", "python", "node", "ruby", "perl", "bash", "sh"})

_HEADER = "<!-- promote_queue: do not edit the fenced block manually -->\n"
_FENCE_OPEN = "```jsonlines\n"
_FENCE_CLOSE = "```\n"


def _suggested_tool(skeleton: str) -> str | None:
    tokens = [t.lstrip("-").replace("-", "_") for t in skeleton.split() if t]
    name = "_".join(tokens)[:30]
    return name or None


def _load_existing_skeletons(queue_file: Path) -> set[str]:
    """Return skeletons already queued with non-dismissed status."""
    if not queue_file.exists():
        return set()
    active: set[str] = set()
    in_block = False
    for line in queue_file.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_block = not in_block
            continue
        if in_block and stripped:
            try:
                entry = json.loads(stripped)
                if entry.get("status") != "dismissed":
                    active.add(entry["skeleton"])
            except (json.JSONDecodeError, KeyError):
                continue
    return active


def _append_entry(queue_file: Path, entry: dict) -> None:
    queue_file.parent.mkdir(parents=True, exist_ok=True)
    if not queue_file.exists():
        queue_file.write_text(_HEADER + _FENCE_OPEN + _FENCE_CLOSE, encoding="utf-8")

    text = queue_file.read_text(encoding="utf-8")
    idx = text.rfind(_FENCE_CLOSE)
    if idx == -1:
        text += f"\n{_FENCE_OPEN}{json.dumps(entry)}\n{_FENCE_CLOSE}"
    else:
        text = text[:idx] + json.dumps(entry) + "\n" + text[idx:]
    queue_file.write_text(text, encoding="utf-8")


def main() -> int:
    try:
        json.load(sys.stdin)
    except Exception:
        pass

    log = STATE_DIR / "bash-log.jsonl"
    if not log.exists():
        return 0

    records: list[dict] = []
    for line in log.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    if not records:
        return 0

    counter: Counter = Counter(
        (r.get("skeleton", ""), r.get("active_skill", "")) for r in records
    )

    skeleton_skills: dict[str, set[str]] = {}
    skeleton_counts: dict[str, int] = {}
    for (skeleton, skill), count in counter.items():
        if not skeleton:
            continue
        skeleton_skills.setdefault(skeleton, set()).add(skill)
        skeleton_counts[skeleton] = skeleton_counts.get(skeleton, 0) + count

    existing = _load_existing_skeletons(QUEUE_FILE)
    today = time.strftime("%Y-%m-%d")

    for skeleton, total in skeleton_counts.items():
        if total < BASH_PROMOTE_THRESHOLD:
            continue
        if skeleton in existing:
            continue

        skills = skeleton_skills[skeleton]
        base = skeleton.split()[0]
        is_ambiguous = len(skills) > 1 or (
            len(skeleton.split()) == 1 and base in _INTERPRETERS
        )

        entry = {
            "date": today,
            "skeleton": skeleton,
            "seen": total,
            "active_skill": list(skills)[0] if len(skills) == 1 else "",
            "suggested_tool": None if is_ambiguous else _suggested_tool(skeleton),
            "status": "needs-confirmation" if is_ambiguous else "pending",
        }
        _append_entry(QUEUE_FILE, entry)

    return 0


if __name__ == "__main__":
    sys.exit(main())
