#!/usr/bin/env python3
"""PreToolUse hook: warn when a Bash command should go through MCP instead.

Reads the Bash tool payload from stdin, checks for patterns that indicate
direct external-system access (HTTP clients, database CLIs, queue tools, etc.)
that the factory requires to go through MCP connectors per plan.md §8.4.

Always exits 0 — this is an advisory warning, not a blocker. The goal is to
surface the convention at the moment of violation so the developer can choose
to install the appropriate MCP connector instead.

See plan.md §8.4 and docs/adr/ADR-007-documentation-cleanup.md.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent

# Patterns: (regex_on_base_command, suggested_mcp_connector, human_label)
_PATTERNS: list[tuple[re.Pattern, str, str]] = [
    (
        re.compile(r"^curls?$|^wget$|^http$|^httpie$"),
        "mcp__fetch or mcp__brave_search",
        "HTTP request",
    ),
    (
        re.compile(r"^psql$|^pg_dump$|^pg_restore$"),
        "a Postgres MCP connector (e.g. mcp__postgres)",
        "PostgreSQL",
    ),
    (
        re.compile(r"^mysql$|^mysqldump$"),
        "a MySQL MCP connector",
        "MySQL",
    ),
    (
        re.compile(r"^sqlite3$"),
        "a SQLite MCP connector (e.g. mcp__sqlite)",
        "SQLite",
    ),
    (
        re.compile(r"^redis-cli$|^redis-server$"),
        "a Redis MCP connector",
        "Redis",
    ),
    (
        re.compile(r"^mongosh$|^mongo$|^mongodump$"),
        "a MongoDB MCP connector",
        "MongoDB",
    ),
    (
        re.compile(r"^kafka-console-[a-z-]+$|^kafka-topics$|^kafka-consumer-groups$"),
        "a Kafka MCP connector",
        "Kafka",
    ),
    (
        re.compile(r"^aws$"),
        "the AWS MCP connector (e.g. mcp__aws_kb_retrieval)",
        "AWS CLI",
    ),
    (
        re.compile(r"^gcloud$|^gsutil$|^bq$"),
        "a GCP MCP connector",
        "Google Cloud CLI",
    ),
    (
        re.compile(r"^gh$"),
        "mcp__github (GitHub MCP connector)",
        "GitHub CLI",
    ),
    (
        re.compile(r"^docker$|^docker-compose$|^podman$"),
        "a container MCP connector",
        "container runtime",
    ),
    (
        re.compile(r"^terraform$|^tofu$"),
        "an IaC MCP connector",
        "infrastructure CLI",
    ),
]


def _base_command(command: str) -> str:
    """Extract the first real token, skipping env-var assignments."""
    try:
        import shlex

        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()

    for tok in tokens:
        if not tok:
            continue
        # Skip KEY=VALUE env assignments
        if re.match(r"^[A-Z_][A-Z0-9_]*=", tok):
            continue
        # Strip path prefix
        return Path(tok).name
    return ""


def check(command: str) -> str | None:
    """Return a warning message if the command matches an MCP pattern, else None."""
    base = _base_command(command)
    if not base:
        return None
    for pattern, connector, label in _PATTERNS:
        if pattern.match(base):
            return (
                f"⚡ MCP-first reminder (plan.md §8.4): '{base}' shells out to {label} "
                f"directly.\n"
                f"   Consider using {connector} instead so agents access this system "
                f"through the MCP substrate.\n"
                f"   Continuing anyway — this is advisory."
            )
    return None


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

    warning = check(command)
    if warning:
        print(warning, file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
