"""Regression test: scaffold.py init_git() returns False for both
"already exists" and git failure, making them indistinguishable.

Bug: `return False` when .git exists and `return result.returncode == 0`
(also False on git failure) are indistinguishable to the caller; a missing
`git` binary or permission error silently prints "git repo already exists".
scaffold.py:97-106,230
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import scaffold  # noqa: E402


class TestInitGitDistinguishesFailure:
    """init_git() must distinguish "already exists" from "git init failed"."""

    def test_init_git_returns_true_on_success(self, tmp_path):
        """init_git() returns True when git init succeeds."""
        result = scaffold.init_git(tmp_path)
        assert result is True

    def test_init_git_returns_false_when_already_exists(self, tmp_path):
        """init_git() returns False when .git already exists (not an error)."""
        (tmp_path / ".git").mkdir()
        result = scaffold.init_git(tmp_path)
        assert result is False

    def test_init_git_raises_on_git_failure(self, tmp_path):
        """init_git() must raise (not return False) when git init fails.

        Before the fix, a git failure silently printed "git repo already
        exists" — indistinguishable from the "already exists" path.
        After the fix, a failed git init raises RuntimeError.
        """
        failed = subprocess.CompletedProcess(
            args=["git", "init"],
            returncode=1,
            stdout="",
            stderr="fatal: not a git repository",
        )
        with patch("subprocess.run", return_value=failed):
            with pytest.raises(RuntimeError, match="git init failed"):
                scaffold.init_git(tmp_path)
