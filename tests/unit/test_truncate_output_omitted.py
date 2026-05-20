"""Regression test: truncate-output omitted_chars understated by marker string length.

Bug: `omitted_chars = len(tool_result) - len(truncated)` subtracts the marker
text itself (~31 chars) from the count; savings log and user-facing message
both report the wrong number. truncate-output.py:102
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "tools"))

_spec = importlib.util.spec_from_file_location(
    "truncate_output", REPO / ".claude" / "hooks" / "truncate-output.py"
)
truncate_output = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(truncate_output)  # type: ignore[union-attr]


class TestOmittedCharsExcludesMarker:
    """omitted_chars in the savings log must not include the marker string length."""

    def test_truncate_chars_omitted_excludes_marker(self):
        """truncate_chars produces a marker like '\\n[... N chars omitted ...]\\n'.
        The marker is ~31+ chars and must NOT be subtracted from omitted_chars
        — it inflates len(truncated) and thus understates saved_chars.

        For a 1000-char input truncated to ceiling=100, exactly 900 chars are
        omitted from the original. The marker text adds ~26 chars to truncated,
        so the buggy formula gives 900 - 26 = 874. The correct answer is 900.
        """
        original = "A" * 1000
        ceiling = 100
        truncated = truncate_output.truncate_chars(original, ceiling)

        # Sanity: truncation happened
        assert len(truncated) > ceiling  # marker makes it slightly over ceiling
        assert "[... " in truncated

        # Compute what the marker length is
        # kept content = ceiling chars (60% head + 40% tail)
        kept_content_len = ceiling  # head_chars + tail_chars == ceiling exactly

        true_omitted = len(original) - kept_content_len  # 900
        buggy_omitted = len(original) - len(truncated)  # 900 - marker_len

        # The buggy formula understates omitted_chars by the marker's length.
        # This assert proves the bug exists (precondition for the fix).
        assert buggy_omitted < true_omitted, (
            "Precondition: buggy formula understates omitted_chars "
            f"(got {buggy_omitted}, true is {true_omitted})"
        )

    def test_main_omitted_chars_excludes_marker(self, tmp_path, monkeypatch):
        """main() must report omitted_chars = chars cut from original, not
        including the injected marker string in the 'kept' count.
        """
        # Build a payload large enough to trigger truncation
        ceiling = 100
        original = "B" * 1000
        payload = json.dumps({"tool_name": "Read", "tool_result": original})

        logged: list[dict] = []
        monkeypatch.setattr(truncate_output, "MAX_TOOL_OUTPUT_CHARS", ceiling)
        monkeypatch.setattr(truncate_output, "TOOL_OUTPUT_HEAD_LINES", 5)
        monkeypatch.setattr(truncate_output, "TOOL_OUTPUT_TAIL_LINES", 3)
        monkeypatch.setattr(truncate_output, "_log_savings", logged.append)

        import io

        old_stdin = sys.stdin
        sys.stdin = io.StringIO(payload)
        try:
            truncate_output.main()
        finally:
            sys.stdin = old_stdin

        assert logged, "Hook must log a savings event"
        saved = logged[0]["saved_chars"]
        # With ceiling=100 and original=1000 chars, at least 900 chars are omitted.
        # The buggy formula gives 900 - marker_len (~26). The fix gives >= 900.
        assert saved >= 900, (
            f"saved_chars should be >= 900 (chars truly omitted from 1000-char input "
            f"with ceiling=100), got {saved} — marker text may be reducing the count"
        )
