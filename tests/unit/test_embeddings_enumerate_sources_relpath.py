"""Regression test for enumerate_sources() using f.name instead of relative path.

Bug: out.append((st, f.name, k, t)) at embeddings.py:191 stores just the filename,
so README.md at repo root and docs/adr/README.md both get source_path="README.md".
The second upsert silently overwrites the first in the DB, losing data.

Fix: use f.relative_to(BASE).as_posix() to get the full relative path.
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


class TestEnumerateSourcesUsesRelativePath:
    """enumerate_sources() must return distinct relative paths, not bare filenames."""

    def test_two_readme_files_get_distinct_source_paths(self, tmp_path):
        """When root glob matches README.md and docs/adr/README.md both exist,
        each must appear with its unique relative path as source_path, not
        just 'README.md' for both (which causes silent DB overwrites).
        """
        # Create two markdown files with the same basename in different dirs
        root_readme = tmp_path / "README.md"
        root_readme.write_text("# Root README\nSome content here.\n", encoding="utf-8")

        nested_dir = tmp_path / "docs" / "adr"
        nested_dir.mkdir(parents=True)
        nested_readme = nested_dir / "README.md"
        nested_readme.write_text("# ADR README\nDecisions here.\n", encoding="utf-8")

        with (
            patch.object(embeddings, "BASE", tmp_path),
            patch.object(embeddings, "INDEXED_ROOT_GLOBS", ["**/*.md"]),
            patch.object(embeddings, "INDEXED_SOURCE_DIRS", []),
        ):
            sources = embeddings.enumerate_sources()

        # Collect all source_paths from the result
        source_paths = [src[1] for src in sources]

        # Both files must be present
        assert any("README.md" in p and "adr" in p for p in source_paths), (
            f"docs/adr/README.md must appear in source_paths, got: {source_paths}"
        )

        # No two entries should have the same bare filename "README.md"
        bare_readmes = [p for p in source_paths if p == "README.md"]
        assert len(bare_readmes) <= 1, (
            f"At most one entry should have source_path='README.md'; "
            f"found {len(bare_readmes)} — f.name is being used instead of relative_to(BASE)"
        )

        # The nested README must have its relative path, not just "README.md"
        nested_path = "docs/adr/README.md"
        assert any(p == nested_path for p in source_paths), (
            f"Expected source_path '{nested_path}' in results, got: {source_paths}"
        )
