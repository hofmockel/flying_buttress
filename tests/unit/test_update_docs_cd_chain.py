"""Regression test: update_docs_on_commit must use the LAST cd in a chained
command, not the first, when deciding whether a commit is in a sibling repo.

Bug: re.search finds the first cd match; in a multi-cd chain the last
destination (the actual commit location) is ignored, causing the hook to
exit early when the factory root is the true target.
update_docs_on_commit.py:29
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
SCRIPTS = REPO / "scripts"

_spec = importlib.util.spec_from_file_location(
    "update_docs_on_commit", SCRIPTS / "update_docs_on_commit.py"
)
update_docs = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(update_docs)  # type: ignore[union-attr]

FACTORY_ROOT = str(REPO.resolve())
MINIMAL_CHANGELOG = "# Changelog\n\n## [Unreleased]\n\n## [0.1.0] - 2026-01-01\n"


def _run_main(command: str) -> list[str]:
    """Run main() with given command, return list of written content args."""
    payload = json.dumps({"tool_input": {"command": command}})
    written: list[str] = []

    def fake_write(self, content, **kw):
        written.append(content)

    with (
        patch.object(
            update_docs,
            "get_commit_info",
            return_value=("abc1234", "test: x", "2026-05-20"),
        ),
        patch.object(Path, "write_text", fake_write),
        patch.object(
            Path,
            "exists",
            lambda self: self.resolve() == (REPO / "CHANGELOG.md").resolve(),
        ),
        patch.object(Path, "read_text", lambda self, **kw: MINIMAL_CHANGELOG),
        patch("sys.stdin", io.StringIO(payload)),
    ):
        try:
            update_docs.main()
        except SystemExit:
            pass
    return written


class TestCdChain:
    def test_single_cd_to_sibling_skips_changelog(self):
        """cd to a sibling repo → hook should exit without writing."""
        written = _run_main("cd /tmp/other_repo && git commit -m 'test'")
        assert written == [], "Should skip CHANGELOG update for sibling repo cd"

    def test_single_cd_to_factory_root_writes_changelog(self):
        """cd to factory root → hook should write CHANGELOG."""
        written = _run_main(f"cd {FACTORY_ROOT} && git commit -m 'test'")
        assert written, "Should write CHANGELOG when cd target is factory root"

    def test_multi_cd_last_is_factory_root_writes_changelog(self):
        """cd sibling then cd factory_root → last cd wins, CHANGELOG written.

        Bug: re.search finds the first cd (/tmp/other), exits 0 thinking it's
        a sibling repo and skips the CHANGELOG update. After fix, the last cd
        (factory_root) is used and CHANGELOG is written.
        """
        command = f"cd /tmp/other_repo && cd {FACTORY_ROOT} && git commit -m 'test'"
        written = _run_main(command)
        assert written, (
            "Multi-cd chain ending at factory root should write CHANGELOG, "
            "but hook exited early (took first cd, not last)"
        )

    def test_multi_cd_last_is_sibling_skips_changelog(self):
        """cd factory_root then cd sibling → last cd wins, CHANGELOG skipped."""
        command = f"cd {FACTORY_ROOT} && cd /tmp/other_repo && git commit -m 'test'"
        written = _run_main(command)
        assert written == [], (
            "Multi-cd chain ending at sibling should skip CHANGELOG update"
        )

    def test_no_cd_writes_changelog(self):
        """No cd in command → CHANGELOG is always written."""
        written = _run_main("git commit -m 'test'")
        assert written, "Should write CHANGELOG when no cd in command"
