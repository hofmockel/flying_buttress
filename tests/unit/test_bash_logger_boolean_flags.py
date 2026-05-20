"""Regression test: bash-logger drops subcommand after boolean long flags.

Bug: flag-value drop logic fires unconditionally on any non-flag next token;
`git --no-pager log` produces skeleton `git --no-pager`, silently losing
the `log` subcommand. bash-logger.py:69-75
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "tools"))

_spec = importlib.util.spec_from_file_location(
    "bash_logger", REPO / ".claude" / "hooks" / "bash-logger.py"
)
bash_logger = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(bash_logger)  # type: ignore[union-attr]


class TestBooleanLongFlagSubcommand:
    """extract_skeleton must not drop the subcommand after a boolean --no-* flag."""

    def test_no_pager_retains_log_subcommand(self):
        """git --no-pager log must yield skeleton 'git --no-pager log'.

        --no-pager is a boolean flag (takes no value); 'log' is the subcommand
        and must not be silently dropped as if it were --no-pager's value.
        """
        skeleton, _ = bash_logger.extract_skeleton("git --no-pager log")
        assert skeleton == "git --no-pager log", (
            f"Expected 'git --no-pager log', got '{skeleton}' — "
            "subcommand 'log' was dropped as if it were --no-pager's value"
        )

    def test_value_taking_flag_still_drops_value(self):
        """git --format HEAD must still yield skeleton 'git --format'.

        --format takes a value; HEAD must be dropped. This ensures the fix
        does not break legitimate flag-value dropping.
        """
        skeleton, _ = bash_logger.extract_skeleton("git --format HEAD")
        assert skeleton == "git --format", (
            f"Expected 'git --format', got '{skeleton}' — "
            "flag value 'HEAD' should be dropped for value-taking flags"
        )

    def test_no_flag_with_additional_flags(self):
        """git --no-pager log --oneline must retain both --no-pager and log."""
        skeleton, _ = bash_logger.extract_skeleton("git --no-pager log --oneline")
        assert "log" in skeleton, (
            f"'log' subcommand should be in skeleton, got '{skeleton}'"
        )
        assert "--no-pager" in skeleton, (
            f"'--no-pager' flag should be in skeleton, got '{skeleton}'"
        )
