#!/usr/bin/env python3
"""Run after every git commit. Inserts a CHANGELOG entry under [Unreleased]."""
import json
import subprocess
import sys
from pathlib import Path


def get_commit_info():
    def run(fmt):
        return subprocess.check_output(
            ["git", "log", "-1", f"--format={fmt}"], text=True
        ).strip()

    return run("%h"), run("%s"), run("%as")


def main():
    # Skip amends — prevents re-triggering after we fold CHANGELOG into the commit
    try:
        command = json.loads(sys.stdin.read()).get("tool_input", {}).get("command", "")
        if "--amend" in command:
            sys.exit(0)
    except (json.JSONDecodeError, AttributeError):
        pass

    try:
        hash_, msg, date = get_commit_info()
    except (subprocess.CalledProcessError, IndexError):
        sys.exit(0)

    if not hash_ or not msg:
        sys.exit(0)

    changelog = Path("CHANGELOG.md")
    if not changelog.exists():
        sys.exit(0)

    content = changelog.read_text()
    entry = f"- {msg} (`{hash_}`) — {date}"

    lines = content.split("\n")
    insert_at = None
    for i, line in enumerate(lines):
        if line == "## [Unreleased]":
            # Skip past any immediately following blank lines
            j = i + 1
            while j < len(lines) and lines[j] == "":
                j += 1
            insert_at = j
            break

    if insert_at is None:
        sys.exit(0)

    lines.insert(insert_at, "")
    lines.insert(insert_at, entry)
    new_content = "\n".join(lines)
    if new_content == content:
        sys.exit(0)

    changelog.write_text(new_content)

    print(json.dumps({
        "systemMessage": f"CHANGELOG updated: {entry}",
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": (
                f"CHANGELOG.md was auto-updated with: {entry}\n"
                "The file has uncommitted changes. Amend the current commit "
                "(`git commit --amend --no-edit`) or include it in the next one."
            ),
        },
    }))


if __name__ == "__main__":
    main()
