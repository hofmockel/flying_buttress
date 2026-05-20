"""Regression test: index-refresh must trigger re-embedding for docs/**/*.md
and .agents/*.md files (root_globs), not just files under INDEXED_SOURCE_DIRS.

Bug: is_indexed() in index-refresh.py didn't import INDEXED_ROOT_GLOBS and
never checked them; edits to docs/ and .agents/ files left the index stale.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "tools"))

# index-refresh.py has a hyphen — load via importlib
_spec = importlib.util.spec_from_file_location(
    "index_refresh", REPO / ".claude" / "hooks" / "index-refresh.py"
)
index_refresh = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(index_refresh)  # type: ignore[union-attr]


class TestIsIndexedRootGlobs:
    """is_indexed() in index-refresh must return True for INDEXED_ROOT_GLOBS paths."""

    def test_docs_nested_md_is_indexed(self):
        """docs/adr/README.md matches docs/**/*.md — should trigger re-embed."""
        path = REPO / "docs" / "adr" / "README.md"
        assert index_refresh.is_indexed(path), (
            "docs/adr/README.md should be indexed (matches docs/**/*.md) "
            "but index-refresh.is_indexed() returned False"
        )

    def test_agents_md_is_indexed(self):
        """.agents/backend.md matches .agents/*.md — should trigger re-embed."""
        path = REPO / ".agents" / "backend.md"
        assert index_refresh.is_indexed(path), (
            ".agents/backend.md should be indexed (matches .agents/*.md) "
            "but index-refresh.is_indexed() returned False"
        )

    def test_root_md_still_indexed(self):
        """Root-level .md must still trigger re-embed (existing behaviour)."""
        path = REPO / "README.md"
        assert index_refresh.is_indexed(path)

    def test_tools_py_still_indexed(self):
        """Files under tools/ must still trigger re-embed (existing behaviour)."""
        path = REPO / "tools" / "search.py"
        assert index_refresh.is_indexed(path)

    def test_unindexed_file_not_triggered(self):
        """A random .txt file must not trigger re-embed."""
        path = REPO / "some_random_file.txt"
        assert not index_refresh.is_indexed(path)
