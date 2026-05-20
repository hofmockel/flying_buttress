"""Regression test: search() must not crash on a corrupt embedding blob.

Bug: np.frombuffer(...).reshape(-1, DIM) at search.py:58-60 is outside any
try/except; a single row with a truncated or wrong-length blob raises an
unhandled ValueError and kills all searches.
"""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "tools"))

from search import search  # noqa: E402
from embeddings import DIM  # noqa: E402


def _make_db_with_corrupt_row(db_path: Path) -> None:
    """Create an index.db with one valid row and one corrupt (truncated) blob."""
    con = sqlite3.connect(db_path)
    con.execute(
        """CREATE TABLE documents (
            id INTEGER PRIMARY KEY,
            source_type TEXT,
            source_path TEXT,
            source_key TEXT,
            text TEXT,
            embedding BLOB
        )"""
    )
    good_vec = np.ones(DIM, dtype=np.float32)
    good_blob = good_vec.tobytes()
    bad_blob = b"\x00\x01\x02"  # truncated — not divisible by DIM*4
    con.execute(
        "INSERT INTO documents VALUES (1, 'doc', 'a.md', 'k1', 'hello', ?)",
        (good_blob,),
    )
    con.execute(
        "INSERT INTO documents VALUES (2, 'doc', 'b.md', 'k2', 'world', ?)",
        (bad_blob,),
    )
    con.commit()
    con.close()


class TestSearchCorruptEmbedding:
    def test_corrupt_blob_does_not_crash(self, tmp_path):
        """search() must return gracefully (not raise) when a blob is corrupt."""
        db_path = tmp_path / "index.db"
        _make_db_with_corrupt_row(db_path)

        # connect_index is bound in search module's namespace directly — patch there.
        import contextlib

        @contextlib.contextmanager
        def fake_connect():
            con = sqlite3.connect(db_path)
            try:
                yield con
            finally:
                con.close()

        qvec = np.ones(DIM, dtype=np.float32)
        with (
            patch("search.connect_index", fake_connect),
            patch("search.embed", return_value=[qvec]),
        ):
            # Must not raise — should return [] or a list of results
            try:
                result = search("hello")
            except ValueError as e:
                pytest.fail(
                    f"search() raised ValueError on corrupt embedding blob: {e}"
                )
            assert isinstance(result, list)
