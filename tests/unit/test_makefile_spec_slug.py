"""Regression test for 'make spec SLUG=…' sed -i '' portability bug.

Bug: Makefile:31 uses `sed -i ''` (BSD/macOS-only form). GNU sed (Linux) treats
the empty-string argument as a filename, leaving {{slug}} and {{date}} unreplaced
or corrupting the output file.

Fix: replace the sed invocation with a cross-platform Python one-liner that does
the same substitution using str.replace(), with no platform-specific flags.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent


def _make_available() -> bool:
    return shutil.which("make") is not None


class TestMakeSpecSlugPortable:
    """make spec SLUG=x must replace {{slug}} and {{date}} on all platforms."""

    def test_placeholders_replaced_in_output_file(self, tmp_path):
        """Running 'make spec SLUG=test-widget' must produce a file with
        no unresolved {{slug}} or {{date}} placeholders.
        """
        if not _make_available():
            import pytest

            pytest.skip("make not available in this environment")

        # Set up minimal directory structure in tmp_path
        makefile_src = REPO / "Makefile"
        tmpl_src = REPO / "templates" / "docs" / "specs" / "spec.md.tmpl"

        if not tmpl_src.exists():
            import pytest

            pytest.skip(f"Template not found: {tmpl_src}")

        shutil.copy(makefile_src, tmp_path / "Makefile")
        tmpl_dest = tmp_path / "templates" / "docs" / "specs"
        tmpl_dest.mkdir(parents=True)
        shutil.copy(tmpl_src, tmpl_dest / "spec.md.tmpl")

        result = subprocess.run(
            ["make", "spec", "SLUG=test-widget"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )

        out_file = tmp_path / "docs" / "specs" / "test-widget.md"
        assert out_file.exists(), (
            f"make spec SLUG=test-widget must create docs/specs/test-widget.md. "
            f"stdout: {result.stdout!r}\nstderr: {result.stderr!r}"
        )

        content = out_file.read_text(encoding="utf-8")

        assert "{{slug}}" not in content, (
            f"{{{{slug}}}} placeholder must be replaced in output file; "
            f"sed -i '' may have failed silently on this platform. "
            f"Content:\n{content[:500]}"
        )
        assert "{{date}}" not in content, (
            f"{{{{date}}}} placeholder must be replaced in output file. "
            f"Content:\n{content[:500]}"
        )
        assert "test-widget" in content, (
            f"'test-widget' must appear in output (slug substitution). "
            f"Content:\n{content[:500]}"
        )

    def test_makefile_does_not_use_bsd_sed_flag(self):
        """The Makefile must not contain 'sed -i ''' (BSD-only form).

        A cross-platform implementation must not require the empty-string
        backup-extension argument that BSD sed requires but GNU sed rejects.
        """
        makefile_text = (REPO / "Makefile").read_text(encoding="utf-8")
        assert "sed -i ''" not in makefile_text, (
            "Makefile contains 'sed -i \"\"' which is BSD/macOS-only. "
            "Use a cross-platform alternative (e.g. python3 -c '...str.replace()...')."
        )
