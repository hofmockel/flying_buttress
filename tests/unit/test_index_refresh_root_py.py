"""Regression test: index-refresh must trigger re-embed for root-level .py files.

Bug: is_indexed() checked `rel.endswith(".md")` for paths with no "/" (root
files); root *.py files are indexed by embeddings.py (via BASE.glob("*.py"))
but edits to them never triggered a re-embed. index-refresh.py:39-40
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "tools"))

_spec = importlib.util.spec_from_file_location(
    "index_refresh", REPO / ".claude" / "hooks" / "index-refresh.py"
)
index_refresh = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(index_refresh)  # type: ignore[union-attr]


class TestRootLevelPyFiles:
    """is_indexed() must return True for root-level .py files."""

    def test_root_py_is_indexed(self):
        """A root-level .py (e.g. install.py) must trigger re-embed."""
        path = REPO / "install.py"
        assert index_refresh.is_indexed(path), (
            "Root-level install.py should be indexed (embeddings.py indexes "
            "BASE.glob('*.py')) but index-refresh.is_indexed() returned False"
        )

    def test_root_md_still_indexed(self):
        """Root-level .md must still trigger re-embed (existing behaviour)."""
        assert index_refresh.is_indexed(REPO / "README.md")

    def test_root_txt_not_indexed(self):
        """Root-level .txt must not trigger re-embed."""
        assert not index_refresh.is_indexed(REPO / "some_file.txt")

    def test_tools_py_still_indexed(self):
        """Files under tools/ must still trigger re-embed."""
        assert index_refresh.is_indexed(REPO / "tools" / "search.py")
