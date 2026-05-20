"""Regression test for 'embeddings.py savings' subcommand argparse crash.

Bug: embeddings.main() dispatches to stats.main() for the 'savings' subcommand.
stats.main() calls ap.parse_args() with no arguments, so it reads sys.argv.
When run as `python3 tools/embeddings.py savings`, sys.argv[1] == 'savings',
which argparse in stats.main() sees as an unrecognized positional and errors out.

Fix: stats.main() should accept an optional argv list; embeddings.main() passes []
so stats sees no extra arguments from sys.argv.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "tools"))

_spec = importlib.util.spec_from_file_location(
    "embeddings", REPO / "tools" / "embeddings.py"
)
embeddings = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(embeddings)  # type: ignore[union-attr]

import stats as _stats_mod  # noqa: E402


class TestSavingsSubcommandDoesNotCrash:
    """embeddings savings subcommand must not crash with unrecognized argument."""

    def test_savings_does_not_raise_systemexit(self):
        """Calling embeddings.main() with sys.argv=['embeddings.py', 'savings']
        must not raise SystemExit due to argparse seeing 'savings' as an
        unrecognized arg inside stats.main().

        We mock stats.main to return 0 to avoid interactive prompts; the bug
        being tested is in the argparse dispatch in embeddings.main(), not in
        stats.main() itself.
        """
        fake_argv = ["embeddings.py", "savings"]

        with (
            patch.object(sys, "argv", fake_argv),
            patch.object(_stats_mod, "main", return_value=0) as mock_stats,
        ):
            try:
                result = embeddings.main()
            except SystemExit as e:
                raise AssertionError(
                    f"embeddings.main() raised SystemExit({e.code}) when called with "
                    f"argv={fake_argv}. stats.main() likely called ap.parse_args() "
                    f"without passing [] to ignore sys.argv."
                ) from e

        # Should return an int (0 or non-zero), not crash
        assert isinstance(result, int), (
            f"embeddings.main() must return an int, got {type(result)}"
        )
        # stats.main must have been called with [] so it doesn't read sys.argv
        mock_stats.assert_called_once_with([])

    def test_stats_main_accepts_empty_argv(self):
        """stats.main() must accept an explicit argv=[] argument so callers
        can suppress sys.argv consumption.
        """
        import inspect

        sig = inspect.signature(_stats_mod.main)
        params = list(sig.parameters.keys())
        assert len(params) >= 1, (
            "stats.main() must accept at least one parameter (argv or args) "
            "so embeddings.main() can pass [] to avoid sys.argv pollution."
        )
