"""Regression test: update_docs_on_commit reads/writes CHANGELOG without encoding="utf-8".

Bug: changelog.read_text() and changelog.write_text() at lines 49 and 72 use
platform-default encoding; on non-UTF-8 systems a commit message with non-ASCII
chars (e.g. ✓) raises UnicodeDecodeError or silently corrupts the file.
update_docs_on_commit.py:49,72
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import update_docs_on_commit  # noqa: E402


class TestChangelogEncodingKeyword:
    """read_text() and write_text() calls on CHANGELOG must specify encoding="utf-8"."""

    def _source(self) -> str:
        return inspect.getsource(update_docs_on_commit)

    def test_read_text_has_utf8_encoding(self):
        """changelog.read_text() must pass encoding="utf-8" to avoid
        UnicodeDecodeError on non-UTF-8 platforms when the CHANGELOG
        contains non-ASCII content (e.g. emoji in commit messages).
        """
        src = self._source()
        # The read_text call must include encoding
        assert (
            'read_text(encoding="utf-8")' in src or "read_text(encoding='utf-8')" in src
        ), (
            "changelog.read_text() must specify encoding='utf-8' "
            "— platform default breaks on non-UTF-8 systems"
        )

    def test_write_text_has_utf8_encoding(self):
        """changelog.write_text() must pass encoding="utf-8" to avoid
        UnicodeEncodeError or silent corruption on non-UTF-8 platforms.
        """
        src = self._source()
        assert (
            'write_text(new_content, encoding="utf-8")' in src
            or "write_text(new_content, encoding='utf-8')" in src
        ), (
            "changelog.write_text() must specify encoding='utf-8' "
            "— platform default breaks on non-UTF-8 systems"
        )
