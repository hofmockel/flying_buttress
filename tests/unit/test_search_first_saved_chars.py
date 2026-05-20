"""Regression test: search-first logs st_size (bytes) as saved_chars instead of char count.

Bug: `file_chars = p.stat().st_size` returns bytes; for files with multi-byte
UTF-8 content the logged `saved_chars` value is overstated.
search-first.py:104,108
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "tools"))

_spec = importlib.util.spec_from_file_location(
    "search_first", REPO / ".claude" / "hooks" / "search-first.py"
)
search_first = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(search_first)  # type: ignore[union-attr]


class TestSavedCharsIsCharCount:
    """saved_chars in savings log must be character count, not byte count."""

    def test_saved_chars_uses_char_count_not_byte_count(self, tmp_path):
        """For a file with multi-byte UTF-8 characters, saved_chars must equal
        the character count (len of decoded string), not the byte count.

        A file with 3 two-byte UTF-8 chars has st_size=6 but len(text)=3.
        The bug logs 6; the fix logs 3.
        """
        # Write a file with multi-byte UTF-8 content: 3 chars × 2 bytes each
        content = "äöü"  # each is 2 bytes in UTF-8
        f = tmp_path / "test_file.py"
        f.write_text(content, encoding="utf-8")

        byte_size = f.stat().st_size  # 6
        char_count = len(content)  # 3
        assert byte_size != char_count, (
            "Precondition: bytes != chars for multi-byte content"
        )

        logged_events: list[dict] = []

        import json

        fake_payload = json.dumps(
            {
                "tool_name": "Read",
                "tool_input": {"file_path": str(f)},
            }
        )

        # _load_config() runs inside main() and would overwrite _config with
        # real values from search_config/savings_log; patch it to a no-op that
        # just returns True so our controlled _config dict is used instead.
        fake_config = {
            "venv_py": "python3",
            "log": logged_events.append,
        }
        search_first._config.clear()
        search_first._config.update(fake_config)

        with (
            patch.object(search_first, "REPO", tmp_path),
            patch.object(search_first, "_load_config", return_value=True),
            patch.object(search_first, "is_indexed", return_value=True),
            patch.object(search_first, "search_was_recent", return_value=False),
        ):
            import io

            old_stdin = sys.stdin
            sys.stdin = io.StringIO(fake_payload)
            try:
                result = search_first.main()
            finally:
                sys.stdin = old_stdin

        assert result == 2, "Hook must exit 2 (block) for un-searched indexed file"
        assert logged_events, "Hook must log a savings event"
        saved = logged_events[0]["saved_chars"]
        assert saved == char_count, (
            f"saved_chars should be character count ({char_count}) "
            f"not byte count ({byte_size}), got {saved}"
        )
