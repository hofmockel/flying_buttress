"""Regression test: search-first.py docstring falsely claims WINDOW_SECONDS
is configurable in search_config.py.

Bug: WINDOW_SECONDS = 300 is hardcoded at line 18; the constant does not
exist in search_config.py; but the module docstring says "configure in
search_config.py", which is false. search-first.py:5,18
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "tools"))

_spec = importlib.util.spec_from_file_location(
    "search_first", REPO / ".claude" / "hooks" / "search-first.py"
)
search_first = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(search_first)  # type: ignore[union-attr]

import search_config  # noqa: E402


class TestWindowSecondsDocstring:
    def test_window_seconds_not_in_search_config(self):
        """WINDOW_SECONDS must not be claimed as configurable in search_config.py
        unless it actually exists there.

        The docstring says 'configure in search_config.py' but the constant
        is absent from search_config — the docstring is false.
        """
        assert not hasattr(search_config, "WINDOW_SECONDS"), (
            "WINDOW_SECONDS now exists in search_config — update the docstring "
            "to say it IS configurable there (or remove it from the docstring)"
        )

    def test_docstring_does_not_claim_search_config_configurability(self):
        """The module docstring must not falsely claim WINDOW_SECONDS is
        configurable in search_config.py when it isn't.
        """
        doc = search_first.__doc__ or ""
        assert "configure in search_config.py" not in doc, (
            "Docstring still claims 'configure in search_config.py' but "
            "WINDOW_SECONDS is hardcoded — remove or correct the claim"
        )
