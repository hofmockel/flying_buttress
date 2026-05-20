"""Regression test: bash-logger reads active_skill and writes log without encoding="utf-8".

Bug 1: active_skill_file.read_text() at line 102 uses platform-default encoding;
  a non-UTF-8 active_skill file raises UnicodeDecodeError.
Bug 2: log.open("a") at line 115 uses platform-default encoding;
  a non-ASCII command or active_skill raises UnicodeEncodeError on non-UTF-8 systems.
bash-logger.py:102,115
"""

from __future__ import annotations

import importlib.util
import inspect
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "tools"))

_bash_logger_path = REPO / ".claude" / "hooks" / "bash-logger.py"

_spec = importlib.util.spec_from_file_location("bash_logger", _bash_logger_path)
bash_logger = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(bash_logger)  # type: ignore[union-attr]


class TestBashLoggerEncoding:
    """bash-logger must use encoding="utf-8" for both file operations."""

    def _source(self) -> str:
        return inspect.getsource(bash_logger)

    def test_active_skill_read_text_has_utf8_encoding(self):
        """active_skill_file.read_text() must specify encoding="utf-8" to avoid
        UnicodeDecodeError when the active_skill file contains non-ASCII content
        on a non-UTF-8 platform.
        """
        src = self._source()
        assert (
            'read_text(encoding="utf-8")' in src or "read_text(encoding='utf-8')" in src
        ), (
            "active_skill_file.read_text() must specify encoding='utf-8' "
            "— platform default breaks on non-UTF-8 systems"
        )

    def test_log_open_has_utf8_encoding(self):
        """log.open('a') must specify encoding='utf-8' to avoid UnicodeEncodeError
        when a command or active_skill contains non-ASCII chars on non-UTF-8 systems.
        """
        src = self._source()
        assert (
            'log.open("a", encoding="utf-8")' in src
            or "log.open('a', encoding='utf-8')" in src
        ), (
            "log.open('a') must specify encoding='utf-8' "
            "— platform default breaks on non-UTF-8 systems"
        )
