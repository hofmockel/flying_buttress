"""Tests for on-write-fmt.py, on-write-lint.py, on-write-test.py hooks."""

import json
import subprocess
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

HOOKS_DIR = Path(__file__).parent.parent.parent / ".claude" / "hooks"
sys.path.insert(0, str(HOOKS_DIR))

import on_write_fmt as fmt_hook  # noqa: E402
import on_write_lint as lint_hook  # noqa: E402
import on_write_test as test_hook  # noqa: E402


# ── helpers ──────────────────────────────────────────────────────────────────


def _payload(tool: str, file_path: str) -> str:
    return json.dumps({"tool_name": tool, "tool_input": {"file_path": file_path}})


def _run(module, stdin_text: str) -> tuple[int, str]:
    """Run a hook module's main() with given stdin, return (exit_code, stderr)."""
    captured = StringIO()
    with patch("sys.stdin", StringIO(stdin_text)), patch("sys.stderr", captured):
        code = module.main()
    return code, captured.getvalue()


# ── fmt hook ─────────────────────────────────────────────────────────────────


class TestOnWriteFmt:
    def test_ignores_non_write_edit(self):
        code, _ = _run(fmt_hook, _payload("Bash", "foo.py"))
        assert code == 0

    def test_ignores_non_source_extension(self):
        with patch("subprocess.run") as mock_run:
            code, _ = _run(fmt_hook, _payload("Write", "README.md"))
        assert code == 0
        mock_run.assert_not_called()

    def test_runs_make_fmt_on_py_file(self):
        mock_result = MagicMock(returncode=0, stdout="", stderr="")
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            code, _ = _run(fmt_hook, _payload("Write", "src/foo.py"))
        assert code == 0
        mock_run.assert_called_once()
        assert mock_run.call_args[0][0] == ["make", "fmt"]

    def test_runs_on_edit_too(self):
        mock_result = MagicMock(returncode=0, stdout="", stderr="")
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            code, _ = _run(fmt_hook, _payload("Edit", "src/foo.ts"))
        assert code == 0
        mock_run.assert_called_once()

    def test_surfaces_stderr_on_failure(self):
        mock_result = MagicMock(returncode=1, stdout="error output\n", stderr="")
        with patch("subprocess.run", return_value=mock_result):
            code, stderr = _run(fmt_hook, _payload("Write", "src/foo.py"))
        assert code == 0  # never blocks
        assert "error output" in stderr

    def test_malformed_json_exits_zero(self):
        code, _ = _run(fmt_hook, "not json")
        assert code == 0

    @pytest.mark.parametrize("ext", [".py", ".ts", ".tsx", ".js", ".jsx"])
    def test_source_extensions_trigger(self, ext):
        mock_result = MagicMock(returncode=0, stdout="", stderr="")
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            _run(fmt_hook, _payload("Write", f"src/foo{ext}"))
        mock_run.assert_called_once()

    @pytest.mark.parametrize("ext", [".md", ".json", ".yaml", ".toml", ".tmpl"])
    def test_non_source_extensions_skipped(self, ext):
        with patch("subprocess.run") as mock_run:
            _run(fmt_hook, _payload("Write", f"docs/foo{ext}"))
        mock_run.assert_not_called()


# ── lint hook ─────────────────────────────────────────────────────────────────


class TestOnWriteLint:
    def test_ignores_non_source_file(self):
        with patch("subprocess.run") as mock_run:
            code, _ = _run(lint_hook, _payload("Write", "README.md"))
        assert code == 0
        mock_run.assert_not_called()

    def test_runs_make_lint_on_source(self):
        mock_result = MagicMock(returncode=0, stdout="", stderr="")
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            code, _ = _run(lint_hook, _payload("Write", "src/foo.py"))
        assert code == 0
        assert mock_run.call_args[0][0] == ["make", "lint"]

    def test_surfaces_lint_issues_on_failure(self):
        mock_result = MagicMock(returncode=1, stdout="lint issue found\n", stderr="")
        with patch("subprocess.run", return_value=mock_result):
            code, stderr = _run(lint_hook, _payload("Write", "src/foo.py"))
        assert code == 0
        assert "lint issue found" in stderr

    def test_clean_lint_produces_no_output(self):
        mock_result = MagicMock(returncode=0, stdout="", stderr="")
        with patch("subprocess.run", return_value=mock_result):
            code, stderr = _run(lint_hook, _payload("Write", "src/foo.py"))
        assert code == 0
        assert stderr == ""


# ── test hook ────────────────────────────────────────────────────────────────


class TestOnWriteTest:
    def test_ignores_non_test_file(self):
        with patch("subprocess.run") as mock_run:
            code, _ = _run(test_hook, _payload("Write", "src/foo.py"))
        assert code == 0
        mock_run.assert_not_called()

    def test_triggers_on_test_py(self):
        mock_result = MagicMock(returncode=0, stdout="1 passed\n", stderr="")
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            code, _ = _run(test_hook, _payload("Write", "tests/test_foo.py"))
        assert code == 0
        mock_run.assert_called_once()
        assert mock_run.call_args[0][0] == ["make", "test"]

    @pytest.mark.parametrize(
        "name",
        [
            "test_foo.py",
            "foo_test.py",
            "foo.test.ts",
            "foo.spec.ts",
            "foo.test.js",
            "foo.spec.js",
        ],
    )
    def test_recognizes_test_file_patterns(self, name):
        assert test_hook.is_test_file(name)

    @pytest.mark.parametrize(
        "name",
        [
            "foo.py",
            "foo.ts",
            "foo.tsx",
            "foo.js",
            "testing_utils.py",
            "test.md",
        ],
    )
    def test_rejects_non_test_patterns(self, name):
        assert not test_hook.is_test_file(name)

    def test_surfaces_test_output_on_failure(self):
        mock_result = MagicMock(returncode=1, stdout="FAILED test_foo\n", stderr="")
        with patch("subprocess.run", return_value=mock_result):
            code, stderr = _run(test_hook, _payload("Write", "tests/test_foo.py"))
        assert code == 0
        assert "FAILED test_foo" in stderr

    def test_surfaces_test_output_on_pass(self):
        mock_result = MagicMock(returncode=0, stdout="3 passed\n", stderr="")
        with patch("subprocess.run", return_value=mock_result):
            code, stderr = _run(test_hook, _payload("Write", "tests/test_foo.py"))
        assert code == 0
        assert "3 passed" in stderr
