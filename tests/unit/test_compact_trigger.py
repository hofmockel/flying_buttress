"""Regression tests for compact-trigger bugs.

Bug 1: `last` state never resets between sessions — after a large session fires
the nudge (e.g. 2 MB), a subsequent smaller-but-over-threshold session (600 KB)
is silently skipped because size < last + hysteresis. compact-trigger.py:71

Bug 2: os.path.getsize() returns bytes; MAX_SESSION_CHARS is chars; for
transcripts with multi-byte UTF-8 content the nudge fires earlier than intended.
compact-trigger.py:62
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "tools"))

_spec = importlib.util.spec_from_file_location(
    "compact_trigger", REPO / ".claude" / "hooks" / "compact-trigger.py"
)
compact_trigger = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(compact_trigger)  # type: ignore[union-attr]


def _run_main(tmp_path, transcript_content: str, last_size: int, threshold: int):
    """Run main() with a controlled transcript, last-size, and threshold."""
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text(transcript_content, encoding="utf-8")

    state_file = tmp_path / "compact-trigger-last"
    if last_size > 0:
        state_file.write_text(str(last_size))

    payload = json.dumps({"transcript_path": str(transcript)})

    logged: list[dict] = []

    with (
        patch.object(compact_trigger, "STATE_FILE", state_file),
        patch.object(compact_trigger, "MAX_SESSION_CHARS", threshold),
        patch.object(compact_trigger, "_log_savings", logged.append),
    ):
        import io

        old_stdin = sys.stdin
        sys.stdin = io.StringIO(payload)
        try:
            result = compact_trigger.main()
        finally:
            sys.stdin = old_stdin

    return result, logged, state_file


class TestLastStateResetsOnSmallerSession:
    """After a large session, a new smaller-but-over-threshold session must fire."""

    def test_smaller_session_fires_nudge_after_large_session(self, tmp_path):
        """If last=2MB and new session size=600KB (both over threshold=500KB),
        the nudge must fire. The bug causes it to be silently skipped because
        600KB < 2MB + 500KB/4 = 2.125MB.
        """
        threshold = 500  # chars
        large_last_size = 2000  # simulates previous large session (4x threshold)
        # New session transcript: 600 chars (over threshold but < last + hysteresis)
        new_session_content = "x" * 600

        result, logged, _ = _run_main(
            tmp_path, new_session_content, large_last_size, threshold
        )

        assert result == 2, (
            f"Nudge must fire (exit 2) for a new over-threshold session "
            f"even after a previous larger session; got exit {result}"
        )

    def test_state_file_reset_when_transcript_shrinks(self, tmp_path):
        """When the transcript is smaller than last recorded size (new session),
        the state file must be cleared so hysteresis resets correctly.
        """
        threshold = 500
        large_last_size = 2000
        new_session_content = "x" * 600

        _run_main(tmp_path, new_session_content, large_last_size, threshold)

        state_file = tmp_path / "compact-trigger-last"
        if state_file.exists():
            written = int(state_file.read_text().strip())
            # After a reset+fire, the state should reflect the new session size, not old
            assert written != large_last_size, (
                f"State file must not retain old large-session size {large_last_size} "
                f"after a new smaller session"
            )


class TestSizeUsesCharCountNotBytes:
    """Transcript size comparison must use character count, not byte count."""

    def test_multibyte_content_uses_char_count(self, tmp_path):
        """For a transcript with multi-byte UTF-8 chars, the comparison must use
        len(text) (chars), not os.path.getsize() (bytes). With getsize(), a
        600-char file of 2-byte chars has st_size=1200, firing prematurely.
        """
        threshold = 1000  # chars
        # 600 two-byte chars → 600 chars < threshold, but st_size=1200 > threshold
        content = "ä" * 600  # each is 2 bytes in UTF-8
        transcript = tmp_path / "transcript.jsonl"
        transcript.write_text(content, encoding="utf-8")

        byte_size = transcript.stat().st_size  # 1200
        char_count = len(content)  # 600
        assert byte_size > threshold > char_count, (
            "Precondition: byte_size > threshold > char_count for this test to be meaningful"
        )

        payload = json.dumps({"transcript_path": str(transcript)})
        logged: list[dict] = []

        with (
            patch.object(compact_trigger, "STATE_FILE", tmp_path / "state"),
            patch.object(compact_trigger, "MAX_SESSION_CHARS", threshold),
            patch.object(compact_trigger, "_log_savings", logged.append),
        ):
            import io

            old_stdin = sys.stdin
            sys.stdin = io.StringIO(payload)
            try:
                result = compact_trigger.main()
            finally:
                sys.stdin = old_stdin

        assert result == 0, (
            f"Nudge must NOT fire when char count ({char_count}) is below threshold "
            f"({threshold}), even though byte count ({byte_size}) exceeds it. "
            f"Got exit {result} — getsize() may still be used instead of len(read_text())"
        )
