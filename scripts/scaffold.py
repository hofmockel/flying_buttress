#!/usr/bin/env python3
"""
scaffold.py — stamp a new sibling project from the flying_buttress templates.

Usage:
    python3 scripts/scaffold.py --target ../my-project
    make scaffold TARGET=../my-project

See docs/adr/ADR-001-v1-mvp-scope.md and docs/adr/ADR-005-makefile-underlay.md.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path


TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
SUBSTITUTION_MARKER = re.compile(r"\{\{(\w+)\}\}")


def prompt(question: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    answer = input(f"{question}{suffix}: ").strip()
    return answer if answer else default


def to_slug(name: str) -> str:
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug


def substitute(content: str, vars: dict) -> str:
    def replace(match):
        key = match.group(1)
        return vars.get(key, match.group(0))
    return SUBSTITUTION_MARKER.sub(replace, content)


def copy_templates(src: Path, dst: Path, vars: dict) -> list[Path]:
    written = []
    for src_path in sorted(src.rglob("*")):
        if src_path.is_dir():
            continue

        rel = src_path.relative_to(src)
        # strip .tmpl suffix from destination filename
        dst_name = rel.name[:-5] if rel.name.endswith(".tmpl") else rel.name
        dst_path = dst / rel.parent / dst_name

        dst_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            content = src_path.read_text(encoding="utf-8")
            content = substitute(content, vars)
            dst_path.write_text(content, encoding="utf-8")
        except UnicodeDecodeError:
            # binary file — copy as-is
            shutil.copy2(src_path, dst_path)

        written.append(dst_path)
    return written


def init_git(path: Path) -> bool:
    git_dir = path / ".git"
    if git_dir.exists():
        return False
    result = subprocess.run(
        ["git", "init", str(path)],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scaffold a new flying_buttress project.")
    parser.add_argument("--target", required=True, help="Path to the new project directory")
    parser.add_argument("--name", default=None, help="Project display name (skips interactive prompt)")
    parser.add_argument("--slug", default=None, help="Project slug, kebab-case (skips interactive prompt)")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation prompts")
    return parser


def main(argv=None):
    args = _build_parser().parse_args(argv)

    target = Path(args.target).expanduser().resolve()

    print(f"\nflying_buttress scaffold")
    print(f"{'─' * 40}")

    if target.exists() and any(target.iterdir()):
        print(f"Warning: {target} already exists and is not empty.")
        if not args.yes:
            confirm = input("Continue anyway? [y/N]: ").strip().lower()
            if confirm != "y":
                print("Aborted.")
                sys.exit(0)

    if args.name is not None:
        project_name = args.name
    else:
        project_name = prompt("Project name", default=target.name)

    if args.slug is not None:
        project_slug = args.slug
    elif args.yes:
        project_slug = to_slug(project_name)
    else:
        project_slug = prompt("Project slug (kebab-case)", default=to_slug(project_name))

    install_less_tokens = False
    if not args.yes:
        lt = prompt("Install less_tokens? (y/N)", default="n").lower()
        install_less_tokens = lt == "y"

    vars = {
        "project_name": project_name,
        "project_slug": project_slug,
        "date": date.today().isoformat(),
    }

    print(f"\nScaffolding '{project_name}' → {target}")
    print(f"{'─' * 40}")

    if not TEMPLATES_DIR.exists():
        print(f"Error: templates/ directory not found at {TEMPLATES_DIR}", file=sys.stderr)
        sys.exit(1)

    written = copy_templates(TEMPLATES_DIR, target, vars)
    for path in written:
        print(f"  [+] {path.relative_to(target)}")

    # add .gitignore
    gitignore = target / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("sandbox/\n.env\n.env.*\n")
        print(f"  [+] .gitignore")

    # initialize git
    was_new = init_git(target)
    if was_new:
        print(f"  [+] git init")
    else:
        print(f"  [~] git repo already exists — skipped init")

    # optional: clone less_tokens
    if install_less_tokens:
        lt_dst = target / "less_tokens"
        if lt_dst.exists():
            print(f"  [~] less_tokens already present — skipped")
        else:
            print(f"\nCloning less_tokens...")
            result = subprocess.run(
                ["git", "clone", "https://github.com/hofmockel/less_tokens.git", str(lt_dst)],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print(f"  [+] less_tokens cloned")
                # add to gitignore
                with open(target / ".gitignore", "a") as f:
                    f.write("less_tokens/\n")
                print(f"  [+] less_tokens/ added to .gitignore")
            else:
                print(f"  [!] less_tokens clone failed: {result.stderr.strip()}")

    print(f"\n{'─' * 40}")
    print(f"Done. Next steps:")
    print(f"  cd {target}")
    print(f"  make validate-hooks")
    print(f"  claude   # open Claude Code and run /spec to start your first feature")
    print()


if __name__ == "__main__":
    main()
