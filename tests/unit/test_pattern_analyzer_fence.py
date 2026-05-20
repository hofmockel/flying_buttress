"""Regression tests for pattern-analyzer fence-related bugs.

Bug 1 (_append_entry): text.rfind(_FENCE_CLOSE) finds the last ```  in the file;
any markdown block after the jsonlines block causes new entries to land in the
wrong fence, corrupting both blocks. pattern-analyzer.py:78

Bug 2 (_load_existing_skeletons): in_block toggles on every fence opener/closer
regardless of language; JSON objects in non-jsonlines fenced blocks are falsely
counted as already-queued skeletons. pattern-analyzer.py:59
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "tools"))

_spec = importlib.util.spec_from_file_location(
    "pattern_analyzer", REPO / ".claude" / "hooks" / "pattern-analyzer.py"
)
pattern_analyzer = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(pattern_analyzer)  # type: ignore[union-attr]


class TestAppendEntryTargetsJsonlinesFence:
    """_append_entry must insert into the jsonlines fence, not the last fence."""

    def test_entry_inserted_before_jsonlines_close_not_last_close(self, tmp_path):
        """When a markdown code block follows the jsonlines block, the new entry
        must still be inserted inside the jsonlines fence, not inside the trailing block.
        """
        queue_file = tmp_path / "promote_queue.md"
        # File with jsonlines block followed by a markdown python block
        queue_file.write_text(
            "<!-- promote_queue -->\n"
            "```jsonlines\n"
            '{"skeleton":"git log","seen":5,"status":"pending"}\n'
            "```\n"
            "\n"
            "## Notes\n"
            "```python\n"
            "# some python example\n"
            "```\n",
            encoding="utf-8",
        )

        entry = {"skeleton": "git diff", "seen": 6, "status": "pending"}
        pattern_analyzer._append_entry(queue_file, entry)

        result = queue_file.read_text(encoding="utf-8")

        # The new entry must appear inside the jsonlines block
        jsonlines_block_end = result.index("```\n", result.index("```jsonlines\n") + 1)
        jsonlines_content = result[result.index("```jsonlines\n") : jsonlines_block_end]
        assert "git diff" in jsonlines_content, (
            f"New entry 'git diff' must be inside the jsonlines fence, "
            f"but it wasn't found there. Block content:\n{jsonlines_content}"
        )

        # The python block must remain intact
        assert "```python\n" in result, "python code block must be preserved"
        assert "# some python example" in result, (
            "python block content must be preserved"
        )

        # The new entry must NOT appear after the python block's close fence
        python_close = result.rindex("```\n")
        assert "git diff" not in result[python_close:], (
            "New entry 'git diff' must not appear after the python block's close fence"
        )


class TestLoadExistingSkeletonsIgnoresNonJsonlinesFences:
    """_load_existing_skeletons must only read JSON from the jsonlines fence."""

    def test_json_in_other_fence_not_counted_as_queued(self, tmp_path):
        """A JSON object inside a non-jsonlines fenced block (e.g. ```json) must not
        be counted as an already-queued skeleton, even if it has a 'skeleton' key.
        """
        queue_file = tmp_path / "promote_queue.md"
        # jsonlines block has one entry; a json block has a look-alike entry
        queue_file.write_text(
            "```jsonlines\n"
            '{"skeleton":"git log","status":"pending"}\n'
            "```\n"
            "\n"
            "```json\n"
            '{"skeleton":"git diff","status":"pending"}\n'
            "```\n",
            encoding="utf-8",
        )

        skeletons = pattern_analyzer._load_existing_skeletons(queue_file)

        assert "git log" in skeletons, (
            "'git log' from the jsonlines block must be in existing skeletons"
        )
        assert "git diff" not in skeletons, (
            "'git diff' from the json block must NOT be counted as queued — "
            "it is in a non-jsonlines fence and is not a real queue entry"
        )
