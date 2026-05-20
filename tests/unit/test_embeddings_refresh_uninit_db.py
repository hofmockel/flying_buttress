"""Regression test for embeddings.refresh() crashing on uninitialised DB.

Bug: connect_index() opens the SQLite file but doesn't create schema.
If db.py init was never run, the SELECT FROM documents at refresh() line 260
raises an unhandled sqlite3.OperationalError, crashing with a raw traceback.

Fix: refresh() should catch sqlite3.OperationalError and print a clear error
message (e.g. "Run db.py init first") then return non-zero, instead of crashing.
"""

from __future__ import annotations

import importlib.util
import sqlite3
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


class TestRefreshHandlesUninitDB:
    """refresh() must not crash when the DB schema hasn't been initialised."""

    def test_refresh_returns_nonzero_on_operational_error(self, tmp_path):
        """When the DB exists but has no schema (tables), refresh() must catch
        sqlite3.OperationalError and return a non-zero exit code rather than
        raising an unhandled exception.
        """
        # Create a blank (schema-less) DB file — simulates running without db.py init
        blank_db = tmp_path / "index.db"
        conn = sqlite3.connect(str(blank_db))
        conn.close()  # file exists but has no tables

        from db import _ClosingConn

        def _fake_connect():
            c = sqlite3.connect(str(blank_db))
            c.row_factory = sqlite3.Row
            return _ClosingConn(c)  # type: ignore[return-value]

        # Stub enumerate_sources so we don't need real files
        fake_sources = [("doc", "README.md", "sec:intro", "Some content")]

        with (
            patch.object(embeddings, "connect_index", _fake_connect),
            patch.object(embeddings, "enumerate_sources", return_value=fake_sources),
            patch.object(embeddings, "_get_model", return_value=None),
        ):
            result = embeddings.refresh()

        assert result != 0, (
            f"refresh() must return non-zero when DB has no schema (uninitialised), "
            f"got {result}. Unhandled sqlite3.OperationalError may have been raised."
        )

    def test_refresh_does_not_raise_on_uninit_db(self, tmp_path, capsys):
        """refresh() must not propagate sqlite3.OperationalError — it must be caught."""
        blank_db = tmp_path / "index.db"
        conn = sqlite3.connect(str(blank_db))
        conn.close()

        from db import _ClosingConn

        def _fake_connect():
            c = sqlite3.connect(str(blank_db))
            c.row_factory = sqlite3.Row
            return _ClosingConn(c)  # type: ignore[return-value]

        fake_sources = [("doc", "README.md", "sec:intro", "Some content")]

        try:
            with (
                patch.object(embeddings, "connect_index", _fake_connect),
                patch.object(
                    embeddings, "enumerate_sources", return_value=fake_sources
                ),
                patch.object(embeddings, "_get_model", return_value=None),
            ):
                embeddings.refresh()
        except sqlite3.OperationalError as e:
            raise AssertionError(
                f"refresh() must not raise sqlite3.OperationalError, but raised: {e}"
            ) from e
