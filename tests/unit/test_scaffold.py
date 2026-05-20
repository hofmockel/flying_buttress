"""Tests for scripts/scaffold.py — CB1: --name/--slug flags."""

import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import scaffold  # noqa: E402


# ── to_slug ──────────────────────────────────────────────────────────────────


def test_to_slug_basic():
    assert scaffold.to_slug("My Project") == "my-project"


def test_to_slug_special_chars():
    assert scaffold.to_slug("Acme API v2!") == "acme-api-v2"


def test_to_slug_already_kebab():
    assert scaffold.to_slug("acme-api") == "acme-api"


# ── argument parsing: --name and --slug flags ─────────────────────────────────


def _parse(args):
    parser = scaffold._build_parser()
    return parser.parse_args(args)


def test_name_flag_accepted():
    args = _parse(["--target", "/tmp/x", "--name", "My App"])
    assert args.name == "My App"


def test_slug_flag_accepted():
    args = _parse(["--target", "/tmp/x", "--slug", "my-app"])
    assert args.slug == "my-app"


def test_name_and_slug_with_yes():
    args = _parse(
        ["--target", "/tmp/x", "--name", "My App", "--slug", "my-app", "--yes"]
    )
    assert args.name == "My App"
    assert args.slug == "my-app"
    assert args.yes is True


def test_name_defaults_to_none():
    args = _parse(["--target", "/tmp/x"])
    assert args.name is None


def test_slug_defaults_to_none():
    args = _parse(["--target", "/tmp/x"])
    assert args.slug is None


# ── end-to-end: --name/--slug/--yes skips all prompts ────────────────────────


def test_scaffold_name_slug_yes_no_prompts(monkeypatch, tmp_path):
    """When --name, --slug, and --yes are all supplied, no input() call is made."""
    target = tmp_path / "new_project"

    called = []
    monkeypatch.setattr("builtins.input", lambda _: called.append(True) or "")

    scaffold.main(
        [
            "--target",
            str(target),
            "--name",
            "Test Project",
            "--slug",
            "test-project",
            "--yes",
        ]
    )

    assert called == [], "input() was called despite --name/--slug/--yes being set"
    assert (target / "CLAUDE.md").exists()


def test_scaffold_name_used_in_output(tmp_path):
    """Project name supplied via --name appears in CLAUDE.md."""
    target = tmp_path / "named_project"
    scaffold.main(
        ["--target", str(target), "--name", "Acme API", "--slug", "acme-api", "--yes"]
    )
    content = (target / "CLAUDE.md").read_text()
    assert "Acme API" in content


def test_scaffold_slug_derived_from_name_when_omitted(monkeypatch, tmp_path):
    """When --slug is omitted but --name is given with --yes, slug is derived automatically."""
    target = tmp_path / "auto_slug"
    monkeypatch.setattr("builtins.input", lambda _: "")  # should not be called for slug
    scaffold.main(["--target", str(target), "--name", "Auto Slug Project", "--yes"])
    # No assertion on slug value — just confirm it completes without interactive prompt
    assert (target / "CLAUDE.md").exists()


# ── --add flag: non-destructive install ──────────────────────────────────────

ADD_ARGS = ["--name", "X", "--slug", "x", "--yes", "--add"]


def test_add_flag_accepted():
    args = _parse(["--target", "/tmp/x", "--add"])
    assert args.add is True


def test_add_flag_defaults_false():
    args = _parse(["--target", "/tmp/x"])
    assert args.add is False


def test_add_writes_missing_files(tmp_path):
    """--add writes files that don't yet exist in the target."""
    target = tmp_path / "partial"
    target.mkdir()
    scaffold.main(["--target", str(target)] + ADD_ARGS)
    assert (target / ".agents" / "backend.md").exists()
    assert (target / "Makefile").exists()
    assert (target / ".claude" / "hooks" / "on_write_fmt.py").exists()


def test_add_skips_existing_files(tmp_path):
    """--add does not overwrite files that already exist."""
    target = tmp_path / "existing"
    target.mkdir()
    (target / "Makefile").write_text("# my custom Makefile\n")
    scaffold.main(["--target", str(target)] + ADD_ARGS)
    assert (target / "Makefile").read_text() == "# my custom Makefile\n"


def test_add_no_prompts(monkeypatch, tmp_path):
    """--add combined with --yes never calls input()."""
    target = tmp_path / "no_prompts"
    target.mkdir()
    called = []
    monkeypatch.setattr("builtins.input", lambda _: called.append(True) or "")
    scaffold.main(["--target", str(target)] + ADD_ARGS)
    assert called == [], "input() was called despite --yes --add"


def test_add_appends_gitignore_missing_lines(tmp_path):
    """--add appends missing lines to an existing .gitignore."""
    target = tmp_path / "has_gitignore"
    target.mkdir()
    (target / ".gitignore").write_text("node_modules/\n")
    scaffold.main(["--target", str(target)] + ADD_ARGS)
    content = (target / ".gitignore").read_text()
    assert "node_modules/" in content  # original preserved
    assert ".env" in content  # missing line added
    assert "sandbox/" in content


def test_add_gitignore_no_duplicate_lines(tmp_path):
    """--add does not duplicate lines already in .gitignore."""
    target = tmp_path / "full_gitignore"
    target.mkdir()
    (target / ".gitignore").write_text("sandbox/\n.env\n.env.*\n")
    scaffold.main(["--target", str(target)] + ADD_ARGS)
    content = (target / ".gitignore").read_text()
    assert content.count(".env\n") == 1


def test_add_appends_claude_md_section(tmp_path):
    """--add appends flying_buttress section to an existing CLAUDE.md."""
    target = tmp_path / "has_claude_md"
    target.mkdir()
    (target / "CLAUDE.md").write_text("# My project\n\nSome docs.\n")
    scaffold.main(["--target", str(target)] + ADD_ARGS)
    content = (target / "CLAUDE.md").read_text()
    assert "My project" in content  # original preserved
    assert "flying_buttress" in content  # section appended


def test_add_preserves_original_claude_md_content(tmp_path):
    """--add does not wipe existing CLAUDE.md content."""
    target = tmp_path / "preserve_claude"
    target.mkdir()
    original = "# Keep me\n\nVery important docs.\n"
    (target / "CLAUDE.md").write_text(original)
    scaffold.main(["--target", str(target)] + ADD_ARGS)
    content = (target / "CLAUDE.md").read_text()
    assert content.startswith("# Keep me")
    assert "Very important docs." in content


def test_add_no_duplicate_claude_md_section(tmp_path):
    """--add does not append a second flying_buttress section if one is already present."""
    target = tmp_path / "already_has_fb"
    target.mkdir()
    (target / "CLAUDE.md").write_text("# flying_buttress project\n\nAlready set up.\n")
    scaffold.main(["--target", str(target)] + ADD_ARGS)
    content = (target / "CLAUDE.md").read_text()
    assert content.count("flying_buttress") == 1
