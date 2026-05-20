"""Regression test: search.py savings log mixes st_size (bytes) with len(text) (chars).

Bug: `full_file_chars += Path(fp).stat().st_size` counts bytes; `chunk_chars`
counts characters; the subtraction overstates `saved_chars` for any file with
non-ASCII content. search.py:99-100
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "tools"))

import search  # noqa: E402


class TestFullFileCharsUsesCharCount:
    """full_file_chars accumulation must use character count, not byte count."""

    def test_st_size_not_used_for_full_file_chars(self):
        """The savings-log code must not use stat().st_size to count file size.

        st_size returns bytes; for files with multi-byte UTF-8 content the
        subtraction (full_file_chars - chunk_chars) overstates saved_chars.
        The fix is to read the file and count characters with len(text).
        """
        src = inspect.getsource(search)
        # The buggy pattern is accumulating st_size into full_file_chars
        assert (
            "full_file_chars += " not in src
            or "st_size" not in src.split("full_file_chars +=")[1].split("\n")[0]
        ), (
            "full_file_chars must not be accumulated via st_size (bytes); "
            "use len(read_text(...)) to count characters"
        )

    def test_savings_log_uses_read_text_for_char_count(self):
        """The savings computation must use read_text() to count file chars."""
        src = inspect.getsource(search)
        # After the fix, full_file_chars should accumulate via len(read_text(...))
        assert "read_text" in src, (
            "search.py main() must use read_text() to count file characters "
            "for the savings log — st_size measures bytes, not chars"
        )
