"""Regression test for expected_source_paths() using f.name instead of relative path.

Bug: out.add(f.name) at embeddings.py:328 stores only the filename.
When docs/adr/README.md exists alongside README.md in the root, health()
reports no gaps even though enumerate_sources() has already overwritten
the docs/adr/README.md content (due to the same f.name bug there).

Fix: use f.relative_to(BASE).as_posix() to get the full relative path,
mirroring the fix applied to enumerate_sources().
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


class TestExpectedSourcePathsUsesRelativePath:
    """expected_source_paths() must return full relative paths, not bare filenames."""

    def test_two_readme_files_get_distinct_expected_paths(self, tmp_path):
        """When root glob matches both README.md and docs/adr/README.md,
        expected_source_paths() must return both as distinct relative paths,
        not two entries both named 'README.md'.
        """
        # Create the files so glob() finds them
        root_readme = tmp_path / "README.md"
        root_readme.write_text("# Root", encoding="utf-8")

        nested_dir = tmp_path / "docs" / "adr"
        nested_dir.mkdir(parents=True)
        nested_readme = nested_dir / "README.md"
        nested_readme.write_text("# ADR", encoding="utf-8")

        with (
            patch.object(embeddings, "BASE", tmp_path),
            patch.object(embeddings, "INDEXED_ROOT_GLOBS", ["**/*.md"]),
            patch.object(embeddings, "INDEXED_SOURCE_DIRS", []),
        ):
            paths = embeddings.expected_source_paths()

        # The nested README must appear as a relative path, not just "README.md"
        assert "docs/adr/README.md" in paths, (
            f"'docs/adr/README.md' must be in expected_source_paths(), "
            f"got: {sorted(paths)}. f.name is being used instead of relative_to(BASE)."
        )

        # The root README should appear as "README.md"
        assert "README.md" in paths, (
            f"'README.md' must be in expected_source_paths(), got: {sorted(paths)}"
        )

        # There must be exactly two distinct entries (not one "README.md" that counts twice)
        assert len(paths) == 2, (
            f"expected_source_paths() must return 2 distinct paths for 2 distinct files, "
            f"got {len(paths)}: {sorted(paths)}"
        )
