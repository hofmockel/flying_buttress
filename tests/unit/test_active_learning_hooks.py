"""Tests for active learning hooks: bash-logger, pattern-analyzer, tool-registry.

Hooks run as subprocesses (matching real Claude Code behaviour).
PYTHONPATH is set to include tools/ so search_config imports work.
BUTTRESS_STATE_DIR and BUTTRESS_QUEUE_FILE env vars redirect state writes
to tmp_path for test isolation.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent.parent
HOOKS = REPO / ".claude" / "hooks"

_ENV = {**os.environ, "PYTHONPATH": str(REPO / "tools")}


def run_hook(
    hook_name: str,
    payload: dict,
    extra_env: dict | None = None,
) -> tuple[int, str, str]:
    env = {**_ENV, **(extra_env or {})}
    result = subprocess.run(
        [sys.executable, str(HOOKS / hook_name)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
    )
    return result.returncode, result.stdout, result.stderr


def run_hook_raw(
    hook_name: str, stdin: str, extra_env: dict | None = None
) -> tuple[int, str, str]:
    env = {**_ENV, **(extra_env or {})}
    result = subprocess.run(
        [sys.executable, str(HOOKS / hook_name)],
        input=stdin,
        capture_output=True,
        text=True,
        env=env,
    )
    return result.returncode, result.stdout, result.stderr


# ---------------------------------------------------------------------------
# bash-logger.py
# ---------------------------------------------------------------------------


class TestBashLogger:
    def test_logs_command_and_skeleton(self, tmp_path):
        code, _, _ = run_hook(
            "bash-logger.py",
            {"tool_name": "Bash", "tool_input": {"command": "git status --short"}},
            {"BUTTRESS_STATE_DIR": str(tmp_path)},
        )
        assert code == 0
        log = tmp_path / "bash-log.jsonl"
        assert log.exists()
        record = json.loads(log.read_text().strip())
        assert record["command"] == "git status --short"
        assert record["skeleton"] == "git status --short"

    def test_skeleton_strips_positional_args(self, tmp_path):
        code, _, _ = run_hook(
            "bash-logger.py",
            {"tool_name": "Bash", "tool_input": {"command": 'grep -r "pattern" src/'}},
            {"BUTTRESS_STATE_DIR": str(tmp_path)},
        )
        assert code == 0
        record = json.loads((tmp_path / "bash-log.jsonl").read_text().strip())
        assert record["skeleton"] == "grep -r"

    def test_skeleton_strips_quoted_flag_values(self, tmp_path):
        code, _, _ = run_hook(
            "bash-logger.py",
            {
                "tool_name": "Bash",
                "tool_input": {"command": 'git commit -m "fix thing"'},
            },
            {"BUTTRESS_STATE_DIR": str(tmp_path)},
        )
        assert code == 0
        record = json.loads((tmp_path / "bash-log.jsonl").read_text().strip())
        assert record["skeleton"] == "git commit -m"

    def test_skeleton_strips_key_value_args(self, tmp_path):
        code, _, _ = run_hook(
            "bash-logger.py",
            {"tool_name": "Bash", "tool_input": {"command": "make spec SLUG=foo"}},
            {"BUTTRESS_STATE_DIR": str(tmp_path)},
        )
        assert code == 0
        record = json.loads((tmp_path / "bash-log.jsonl").read_text().strip())
        assert record["skeleton"] == "make spec"

    def test_reads_active_skill(self, tmp_path):
        (tmp_path / "active_skill").write_text("bugfix\n")
        run_hook(
            "bash-logger.py",
            {"tool_name": "Bash", "tool_input": {"command": "git diff"}},
            {"BUTTRESS_STATE_DIR": str(tmp_path)},
        )
        record = json.loads((tmp_path / "bash-log.jsonl").read_text().strip())
        assert record["active_skill"] == "bugfix"

    def test_missing_active_skill_defaults_empty(self, tmp_path):
        run_hook(
            "bash-logger.py",
            {"tool_name": "Bash", "tool_input": {"command": "ls"}},
            {"BUTTRESS_STATE_DIR": str(tmp_path)},
        )
        record = json.loads((tmp_path / "bash-log.jsonl").read_text().strip())
        assert record["active_skill"] == ""

    def test_non_bash_tool_exits_zero_no_write(self, tmp_path):
        code, _, _ = run_hook(
            "bash-logger.py",
            {"tool_name": "Read", "tool_input": {"file_path": "/tmp/foo.py"}},
            {"BUTTRESS_STATE_DIR": str(tmp_path)},
        )
        assert code == 0
        assert not (tmp_path / "bash-log.jsonl").exists()

    def test_malformed_json_exits_zero(self, tmp_path):
        code, _, _ = run_hook_raw(
            "bash-logger.py",
            "not-json!!!",
            {"BUTTRESS_STATE_DIR": str(tmp_path)},
        )
        assert code == 0

    def test_empty_command_exits_zero_no_write(self, tmp_path):
        code, _, _ = run_hook(
            "bash-logger.py",
            {"tool_name": "Bash", "tool_input": {"command": ""}},
            {"BUTTRESS_STATE_DIR": str(tmp_path)},
        )
        assert code == 0
        assert not (tmp_path / "bash-log.jsonl").exists()

    def test_multiple_commands_appended(self, tmp_path):
        for cmd in ["git status", "git diff", "git log"]:
            run_hook(
                "bash-logger.py",
                {"tool_name": "Bash", "tool_input": {"command": cmd}},
                {"BUTTRESS_STATE_DIR": str(tmp_path)},
            )
        lines = (tmp_path / "bash-log.jsonl").read_text().strip().splitlines()
        assert len(lines) == 3


# ---------------------------------------------------------------------------
# pattern-analyzer.py
# ---------------------------------------------------------------------------


def _write_log(state_dir: Path, entries: list[dict]) -> None:
    log = state_dir / "bash-log.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("w") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")


def _make_records(skeleton: str, skill: str, count: int) -> list[dict]:
    return [
        {"ts": 1.0, "command": skeleton, "skeleton": skeleton, "active_skill": skill}
        for _ in range(count)
    ]


class TestPatternAnalyzer:
    def test_no_log_file_exits_zero(self, tmp_path):
        queue = tmp_path / "queue.md"
        code, _, _ = run_hook(
            "pattern-analyzer.py",
            {},
            {"BUTTRESS_STATE_DIR": str(tmp_path), "BUTTRESS_QUEUE_FILE": str(queue)},
        )
        assert code == 0
        assert not queue.exists()

    def test_below_threshold_no_queue_entry(self, tmp_path):
        queue = tmp_path / "queue.md"
        _write_log(tmp_path, _make_records("git status", "spec", 4))
        run_hook(
            "pattern-analyzer.py",
            {},
            {"BUTTRESS_STATE_DIR": str(tmp_path), "BUTTRESS_QUEUE_FILE": str(queue)},
        )
        assert not queue.exists()

    def test_threshold_hit_unambiguous_appends_pending(self, tmp_path):
        queue = tmp_path / "queue.md"
        _write_log(tmp_path, _make_records("git status", "spec", 5))
        run_hook(
            "pattern-analyzer.py",
            {},
            {"BUTTRESS_STATE_DIR": str(tmp_path), "BUTTRESS_QUEUE_FILE": str(queue)},
        )
        assert queue.exists()
        text = queue.read_text()
        assert '"status": "pending"' in text
        assert '"skeleton": "git status"' in text

    def test_threshold_hit_ambiguous_multi_skill_needs_confirmation(self, tmp_path):
        queue = tmp_path / "queue.md"
        records = _make_records("grep -r", "spec", 3) + _make_records(
            "grep -r", "bugfix", 3
        )
        _write_log(tmp_path, records)
        run_hook(
            "pattern-analyzer.py",
            {},
            {"BUTTRESS_STATE_DIR": str(tmp_path), "BUTTRESS_QUEUE_FILE": str(queue)},
        )
        assert queue.exists()
        assert '"status": "needs-confirmation"' in queue.read_text()

    def test_interpreter_only_skeleton_needs_confirmation(self, tmp_path):
        queue = tmp_path / "queue.md"
        _write_log(tmp_path, _make_records("python3", "spec", 6))
        run_hook(
            "pattern-analyzer.py",
            {},
            {"BUTTRESS_STATE_DIR": str(tmp_path), "BUTTRESS_QUEUE_FILE": str(queue)},
        )
        assert queue.exists()
        assert '"status": "needs-confirmation"' in queue.read_text()

    def test_skips_existing_pending_entry(self, tmp_path):
        queue = tmp_path / "queue.md"
        existing = json.dumps(
            {
                "date": "2026-05-16",
                "skeleton": "git status",
                "seen": 5,
                "active_skill": "spec",
                "suggested_tool": "git_status",
                "status": "pending",
            }
        )
        queue.write_text(
            "<!-- promote_queue: do not edit the fenced block manually -->\n"
            "```jsonlines\n"
            f"{existing}\n"
            "```\n"
        )
        _write_log(tmp_path, _make_records("git status", "spec", 7))
        run_hook(
            "pattern-analyzer.py",
            {},
            {"BUTTRESS_STATE_DIR": str(tmp_path), "BUTTRESS_QUEUE_FILE": str(queue)},
        )
        assert queue.read_text().count('"skeleton": "git status"') == 1

    def test_skips_existing_accepted_entry(self, tmp_path):
        queue = tmp_path / "queue.md"
        existing = json.dumps(
            {
                "date": "2026-05-16",
                "skeleton": "git diff",
                "seen": 5,
                "active_skill": "spec",
                "suggested_tool": "git_diff",
                "status": "accepted",
            }
        )
        queue.write_text(
            "<!-- promote_queue: do not edit the fenced block manually -->\n"
            "```jsonlines\n"
            f"{existing}\n"
            "```\n"
        )
        _write_log(tmp_path, _make_records("git diff", "spec", 7))
        run_hook(
            "pattern-analyzer.py",
            {},
            {"BUTTRESS_STATE_DIR": str(tmp_path), "BUTTRESS_QUEUE_FILE": str(queue)},
        )
        assert queue.read_text().count('"skeleton": "git diff"') == 1

    def test_dismissed_entry_allows_new_pending(self, tmp_path):
        queue = tmp_path / "queue.md"
        existing = json.dumps(
            {
                "date": "2026-05-01",
                "skeleton": "make lint",
                "seen": 5,
                "active_skill": "spec",
                "suggested_tool": "make_lint",
                "status": "dismissed",
            }
        )
        queue.write_text(
            "<!-- promote_queue: do not edit the fenced block manually -->\n"
            "```jsonlines\n"
            f"{existing}\n"
            "```\n"
        )
        _write_log(tmp_path, _make_records("make lint", "spec", 6))
        run_hook(
            "pattern-analyzer.py",
            {},
            {"BUTTRESS_STATE_DIR": str(tmp_path), "BUTTRESS_QUEUE_FILE": str(queue)},
        )
        assert queue.read_text().count('"skeleton": "make lint"') == 2

    def test_corrupt_jsonl_line_skipped_gracefully(self, tmp_path):
        queue = tmp_path / "queue.md"
        log = tmp_path / "bash-log.jsonl"
        log.parent.mkdir(parents=True, exist_ok=True)
        good = json.dumps(
            {
                "ts": 1.0,
                "command": "git log",
                "skeleton": "git log",
                "active_skill": "spec",
            }
        )
        with log.open("w") as f:
            f.write("{{corrupt\n")
            for _ in range(5):
                f.write(good + "\n")
        code, _, _ = run_hook(
            "pattern-analyzer.py",
            {},
            {"BUTTRESS_STATE_DIR": str(tmp_path), "BUTTRESS_QUEUE_FILE": str(queue)},
        )
        assert code == 0
        assert queue.exists()
        assert '"skeleton": "git log"' in queue.read_text()

    def test_always_exits_zero(self, tmp_path):
        queue = tmp_path / "queue.md"
        _write_log(tmp_path, _make_records("git status", "spec", 10))
        code, _, _ = run_hook(
            "pattern-analyzer.py",
            {},
            {"BUTTRESS_STATE_DIR": str(tmp_path), "BUTTRESS_QUEUE_FILE": str(queue)},
        )
        assert code == 0

    def test_malformed_json_stdin_exits_zero(self, tmp_path):
        queue = tmp_path / "queue.md"
        code, _, _ = run_hook_raw(
            "pattern-analyzer.py",
            "not-json",
            {"BUTTRESS_STATE_DIR": str(tmp_path), "BUTTRESS_QUEUE_FILE": str(queue)},
        )
        assert code == 0


# ---------------------------------------------------------------------------
# tool-registry.py
# ---------------------------------------------------------------------------


class TestToolRegistry:
    def test_write_to_tools_path_exits_two_with_message(self):
        file_path = str(REPO / ".claude" / "skills" / "spec" / "tools" / "fetch_api.py")
        code, _, stderr = run_hook(
            "tool-registry.py",
            {"tool_name": "Write", "tool_input": {"file_path": file_path}},
        )
        assert code == 2
        assert "tool_registry.json" in stderr

    def test_nested_skill_tools_path_matched(self):
        file_path = str(
            REPO / ".claude" / "skills" / "my-skill" / "tools" / "call_db.py"
        )
        code, _, stderr = run_hook(
            "tool-registry.py",
            {"tool_name": "Write", "tool_input": {"file_path": file_path}},
        )
        assert code == 2
        assert "tool_registry.json" in stderr

    def test_write_outside_tools_path_exits_zero(self):
        code, _, _ = run_hook(
            "tool-registry.py",
            {"tool_name": "Write", "tool_input": {"file_path": "/tmp/unrelated.py"}},
        )
        assert code == 0

    def test_write_to_hooks_path_exits_zero(self):
        file_path = str(REPO / ".claude" / "hooks" / "foo.py")
        code, _, _ = run_hook(
            "tool-registry.py",
            {"tool_name": "Write", "tool_input": {"file_path": file_path}},
        )
        assert code == 0

    def test_non_write_tool_exits_zero(self):
        code, _, _ = run_hook(
            "tool-registry.py",
            {"tool_name": "Edit", "tool_input": {"file_path": "/tmp/foo.py"}},
        )
        assert code == 0

    def test_edit_to_tools_path_exits_two_with_message(self):
        """Regression: Edit on a skill tools/*.py must trigger registry reminder.

        Bug: hook checked tool_name != 'Write', so Edit calls on existing tool
        stubs never fired the registry-update reminder.
        """
        file_path = str(REPO / ".claude" / "skills" / "spec" / "tools" / "fetch_api.py")
        code, _, stderr = run_hook(
            "tool-registry.py",
            {"tool_name": "Edit", "tool_input": {"file_path": file_path}},
        )
        assert code == 2, (
            f"Edit on a skill tool stub should exit 2 but got {code}; "
            "hook is ignoring Edit tool calls"
        )
        assert "tool_registry.json" in stderr

    def test_missing_file_path_exits_zero(self):
        code, _, _ = run_hook(
            "tool-registry.py",
            {"tool_name": "Write", "tool_input": {}},
        )
        assert code == 0

    def test_malformed_json_exits_zero(self):
        code, _, _ = run_hook_raw("tool-registry.py", "not-json")
        assert code == 0
