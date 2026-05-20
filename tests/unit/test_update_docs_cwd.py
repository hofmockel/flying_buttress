"""Regression test: update_docs_on_commit must write CHANGELOG.md relative to
the repo root, not relative to the process CWD.

Bug: `changelog = Path("CHANGELOG.md")` resolves against the process CWD;
when the hook is invoked from any directory other than the repo root the file
is not found and the hook silently no-ops.
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO / "scripts"

_spec = importlib.util.spec_from_file_location(
    "update_docs_on_commit", SCRIPTS / "update_docs_on_commit.py"
)
update_docs = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(update_docs)  # type: ignore[union-attr]


MINIMAL_CHANGELOG = "# Changelog\n\n## [Unreleased]\n\n## [0.1.0] - 2026-01-01\n"


class TestChangelogPath:
    def test_path_resolves_to_repo_root_not_cwd(self, tmp_path, monkeypatch):
        """changelog path must resolve to the repo root even when CWD differs.

        With the bug: Path("CHANGELOG.md") from a temp CWD → file not found
        → hook silently no-ops and write_text is never called.
        After fix: path is repo-root-anchored → write_text called on
        REPO/CHANGELOG.md regardless of CWD.
        """
        # Change CWD away from repo root
        monkeypatch.chdir(tmp_path)

        payload = json.dumps({"tool_input": {"command": "git commit -m 'test'"}})
        monkeypatch.setattr("sys.stdin", io.StringIO(payload))

        written_paths: list[Path] = []

        # Intercept Path.write_text to record what path was written
        original_write_text = Path.write_text

        def spy_write_text(self, *args, **kwargs):
            # Record path but do NOT actually write — avoids corrupting real files
            written_paths.append(self.resolve())

        with (
            patch.object(
                update_docs,
                "get_commit_info",
                return_value=("abc1234", "test: thing", "2026-05-20"),
            ),
            # Prevent actual writes — just record the path and fake success
            patch.object(Path, "write_text", spy_write_text),
            # Make Path.exists() return True only for the repo-root CHANGELOG
            patch.object(
                Path,
                "exists",
                lambda self: self.resolve() == (REPO / "CHANGELOG.md").resolve(),
            ),
            # Fake read_text so we don't actually touch the real file
            patch.object(Path, "read_text", lambda self, **kw: MINIMAL_CHANGELOG),
        ):
            try:
                update_docs.main()
            except SystemExit:
                pass

        assert written_paths, (
            "write_text was never called — hook no-oped, likely because "
            "Path('CHANGELOG.md') resolved against CWD instead of repo root"
        )
        expected = (REPO / "CHANGELOG.md").resolve()
        assert written_paths[0] == expected, (
            f"write_text called on {written_paths[0]}, expected {expected}; "
            "hook is not anchoring the path to the repo root"
        )
