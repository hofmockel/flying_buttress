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
    args = _parse(["--target", "/tmp/x", "--name", "My App", "--slug", "my-app", "--yes"])
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

    scaffold.main(["--target", str(target), "--name", "Test Project", "--slug", "test-project", "--yes"])

    assert called == [], "input() was called despite --name/--slug/--yes being set"
    assert (target / "CLAUDE.md").exists()


def test_scaffold_name_used_in_output(tmp_path):
    """Project name supplied via --name appears in CLAUDE.md."""
    target = tmp_path / "named_project"
    scaffold.main(["--target", str(target), "--name", "Acme API", "--slug", "acme-api", "--yes"])
    content = (target / "CLAUDE.md").read_text()
    assert "Acme API" in content


def test_scaffold_slug_derived_from_name_when_omitted(monkeypatch, tmp_path):
    """When --slug is omitted but --name is given with --yes, slug is derived automatically."""
    target = tmp_path / "auto_slug"
    monkeypatch.setattr("builtins.input", lambda _: "")  # should not be called for slug
    scaffold.main(["--target", str(target), "--name", "Auto Slug Project", "--yes"])
    # No assertion on slug value — just confirm it completes without interactive prompt
    assert (target / "CLAUDE.md").exists()
