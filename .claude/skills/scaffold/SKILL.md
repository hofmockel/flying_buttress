---
name: scaffold
description: Stamp out a new sibling project from the flying_buttress factory templates. Use when the user wants to create a new project, scaffold a repo, start a new app from the factory, or run /scaffold. Triggers for "scaffold a new project", "create a new repo", "stamp out a project", "new project from factory", "/scaffold", or similar requests.
---

# /scaffold workflow

## Rules
- Never write any files into flying_buttress as a side effect — the target is always a sibling directory outside this repo.
- The target path must be outside the flying_buttress directory. If the user gives a relative path, resolve it relative to the parent of flying_buttress (i.e., `../my-project`), not inside it.
- Always confirm the target path and project details with the user before running `make scaffold`.
- If the target directory already exists and is non-empty, warn the user before proceeding.
- Use `make scaffold` (not `python3 scripts/scaffold.py` directly) — the Makefile is the durable interface.

## Steps

### 0. Signal active skill
Write `scaffold` to `.claude/state/active_skill`.

### 1. Collect project details
Ask the user for:
1. **Target path** — where to create the project. Suggest `../my-project-name` (a sibling of flying_buttress).
2. **Project name** — display name (e.g. "My App"). Default: the target directory name.
3. **Project slug** — kebab-case identifier (e.g. `my-app`). Default: auto-derived from the name.
4. **Install less_tokens?** — optional; clones the less_tokens helper library into the new project.

Use AskUserQuestion for items 1–3 together (one question block). Ask about less_tokens separately if the user seems unfamiliar with it — offer a one-sentence explanation: "less_tokens is a helper that reduces Claude's context window usage."

### 2. Confirm before running
Show the user a summary:
```
Target:   <resolved absolute path>
Name:     <project name>
Slug:     <project slug>
less_tokens: yes / no
```
Ask: "Ready to scaffold?" If they say no or want changes, loop back to step 1.

### 3. Run make scaffold
Build the make command from the collected details:

```
make scaffold TARGET=<target> NAME="<name>" SLUG="<slug>" YES=1
```

- Always pass `YES=1` (the user already confirmed in step 2; no need for a second interactive prompt inside scaffold.py).
- Add `LESS_TOKENS=1` only if the user opted in — but note: the current Makefile does not expose a `LESS_TOKENS` flag. If the user wants less_tokens, run the command without it and follow up with a separate `git clone https://github.com/hofmockel/less_tokens.git <target>/less_tokens`.
- Run via Bash. Stream output to the user.

### 4. Verify and report
After the command completes:
1. Check that `<target>/.claude/settings.json` exists — if not, report the error and stop.
2. Check that `<target>/.git/` exists — if not, note that git init may have been skipped.
3. Confirm all three hook files are present: `.claude/hooks/on_write_fmt.py`, `on_write_lint.py`, `on_write_test.py`.

Report to the user:
- ✓ Files stamped (list the key ones: CLAUDE.md, settings.json, Makefile, hooks)
- ✓ Git repo initialized (or "already existed — skipped")
- Next steps:
  ```
  cd <target>
  make validate-hooks       # verify hooks are wired correctly
  claude                    # open Claude Code in the new project
  /spec                     # start your first feature
  ```

### 5. Offer carry-back reminder
If the user adds custom modifications to the scaffolded project that look like factory improvements (better hooks, new skills, improved templates), remind them of the carry-back workflow:
> "If this improvement belongs in the factory, open a PR back to flying_buttress so future projects inherit it (ADR-003)."

---

## Error handling

| Situation | Action |
|---|---|
| Target path is inside flying_buttress | Refuse. Tell the user to use a sibling path (e.g. `../my-project`). |
| Target already exists and non-empty | Warn. Ask for explicit confirmation before passing `YES=1`. |
| `make scaffold` exits non-zero | Show the full output. Do not proceed to verification. |
| Hook files missing after scaffold | Report which files are absent. Suggest `cd <target> && make validate-hooks`. |
