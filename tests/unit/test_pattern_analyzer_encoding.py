"""Regression test: pattern-analyzer reads/writes queue and bash-log without encoding="utf-8".

Bug 1: queue_file.read_text() and queue_file.write_text() at lines 57, 75, 77, 83
  use platform-default encoding; non-ASCII skeleton names or tool values corrupt
  the queue or raise on non-UTF-8 systems.
Bug 2: log.read_text() at line 97 uses platform-default encoding; a single non-ASCII
  entry in bash-log.jsonl raises UnicodeDecodeError and halts the entire analysis pass.
pattern-analyzer.py:57,75,77,83,97
"""

from __future__ import annotations

import importlib.util
import inspect
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "tools"))

_spec = importlib.util.spec_from_file_location(
    "pattern_analyzer", REPO / ".claude" / "hooks" / "pattern-analyzer.py"
)
pattern_analyzer = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(pattern_analyzer)  # type: ignore[union-attr]


def _src() -> str:
    return inspect.getsource(pattern_analyzer)


class TestQueueFileEncoding:
    """queue_file read/write calls must specify encoding="utf-8"."""

    def test_all_read_text_calls_have_utf8_encoding(self):
        """Every queue_file.read_text() must specify encoding='utf-8' to avoid
        UnicodeDecodeError on non-UTF-8 systems with non-ASCII skeleton names.
        """
        src = _src()
        # Count bare read_text() calls (no encoding arg) — there should be none
        bare_reads = src.count("read_text()")
        assert bare_reads == 0, (
            f"Found {bare_reads} bare read_text() call(s) without encoding= "
            "— all must specify encoding='utf-8'"
        )

    def test_all_write_text_calls_have_utf8_encoding(self):
        """Every queue_file.write_text(...) must specify encoding='utf-8' to avoid
        UnicodeEncodeError or silent corruption on non-UTF-8 systems.
        """
        src = _src()
        import re

        # Find write_text calls; check none are missing the encoding kwarg
        write_calls = re.findall(r"write_text\([^)]+\)", src)
        bad = [c for c in write_calls if "encoding=" not in c]
        assert not bad, (
            f"write_text() calls missing encoding=: {bad} "
            "— all must specify encoding='utf-8'"
        )
