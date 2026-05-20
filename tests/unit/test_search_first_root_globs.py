"""Regression test: search-first gate must enforce the search-before-Read rule
for docs/**/*.md and .agents/*.md files (root_globs), not just for files under
INDEXED_SOURCE_DIRS.

Bug: is_indexed() loaded root_globs into _config but never consulted them;
docs/ and .agents/ paths fell through to `return False`, bypassing the gate.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "tools"))

# search-first.py has a hyphen — load via importlib
_spec = importlib.util.spec_from_file_location(
    "search_first", REPO / ".claude" / "hooks" / "search-first.py"
)
search_first = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(search_first)  # type: ignore[union-attr]


@pytest.fixture(autouse=True)
def _load_real_config():
    """Load real search_config so _config is populated before each test."""
    search_first._config.clear()
    search_first._load_config()
    yield
    search_first._config.clear()


class TestIsIndexedRootGlobs:
    """is_indexed() must return True for paths matching INDEXED_ROOT_GLOBS."""

    def test_docs_nested_md_is_indexed(self):
        """docs/adr/README.md matches docs/**/*.md — should be gated."""
        path = REPO / "docs" / "adr" / "README.md"
        assert search_first.is_indexed(path), (
            "docs/adr/README.md should be indexed (matches docs/**/*.md) "
            "but is_indexed() returned False"
        )

    def test_agents_md_is_indexed(self):
        """.agents/backend.md matches .agents/*.md — should be gated."""
        path = REPO / ".agents" / "backend.md"
        assert search_first.is_indexed(path), (
            ".agents/backend.md should be indexed (matches .agents/*.md) "
            "but is_indexed() returned False"
        )

    def test_root_md_still_indexed(self):
        """Root-level .md (e.g. README.md) must still be gated (existing behaviour)."""
        path = REPO / "README.md"
        assert search_first.is_indexed(path)

    def test_tools_py_still_indexed(self):
        """files under tools/ must still be gated (existing behaviour)."""
        path = REPO / "tools" / "search.py"
        assert search_first.is_indexed(path)

    def test_unindexed_file_not_gated(self):
        """A random .txt file must not be gated."""
        path = REPO / "some_random_file.txt"
        assert not search_first.is_indexed(path)
