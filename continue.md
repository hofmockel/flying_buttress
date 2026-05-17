# continue.md

> Pick up here in the next session.

**Repo:** `flying_buttress` — a software factory for AI-native development  
**Branch:** `main` (clean, committed through `8cc1253`)  
**State:** v1 complete. All seven ADRs accepted. Backlog clear.

---

## What v1 contains (all verified present)

| Deliverable | Location |
|---|---|
| Root `CLAUDE.md` | `CLAUDE.md` |
| `.agents/` rules | `.agents/{backend,frontend,testing,security}.md` |
| `settings.json` baseline + deny list | `.claude/settings.json` |
| `/spec` skill | `.claude/skills/spec/SKILL.md` |
| `ONBOARDING.md` | `ONBOARDING.md` |
| `Makefile` (6 targets) | `Makefile` |
| `templates/` | `templates/` |
| `scripts/scaffold.py` | `scripts/scaffold.py` |

---

## What comes next: the Tier 2 integration milestone

Before any v2 features start, the factory must pass this milestone (ADR-004 §Tier 2). It proves the factory works end-to-end on a real project, not just in theory.

**Who runs it:** senior, with at least one junior observing.

### Step 1 — Scaffold a test project

```bash
make scaffold TARGET=../fb_test_alpha
cd ../fb_test_alpha
make validate-hooks   # all checks should be green
```

Confirm Claude Code opens correctly inside `fb_test_alpha`:

```bash
claude
# ask: "What is this project and how is it structured?"
# CLAUDE.md should orient correctly
```

### Step 2 — Run /spec on a real problem

Inside `fb_test_alpha`, open Claude Code and run:

```
/spec <a real, non-toy feature for the test project>
```

Pass condition: a readable PRD is written to `docs/specs/<slug>.md`. The plan mode gate must engage (Claude asks for approval before writing).

### Step 3 — Plant and fix a bug

Plant a deliberate bug in `fb_test_alpha` (a function that returns the wrong value, a missing guard, etc.). Then either:

- **If `/fix` exists by then:** run `/fix` — it should reproduce the bug, write a failing test, and apply the fix.
- **If `/fix` does not exist yet:** fix it manually using Claude Code, document the gap, and note it as a carry-back candidate.

Pass condition: the bug is reproduced, a test exists that catches it, and the fix is committed.

### Step 4 — Carry back at least one improvement

Anything observed during the milestone that would improve the factory (a better rule, a Makefile gap, a CLAUDE.md wording issue, a skill edge case) should be carried back to `flying_buttress` per ADR-003:

1. Open a PR against `flying_buttress` — not `fb_test_alpha`.
2. Include evidence it works (transcript excerpt, output artifact, or screenshot).
3. "I tested it and it works" with no artifact is not acceptable (Tier 3 gate, ADR-004).

### Milestone pass condition

All four steps complete with no open blockers. If any step fails, open an issue in `flying_buttress`, fix it, and re-run from Step 1.

---

## /fix is built (2026-05-17)

The blocker is resolved. `/fix` is a fully implemented skill:

| Artifact | Location |
|---|---|
| Factory skill | `.claude/skills/fix/SKILL.md` |
| Template (stamped to new projects) | `templates/.claude/skills/fix/SKILL.md` |
| Makefile target | `make fix` |

**Workflow:** signal active_skill → identify bug (arg or backlog) → Explore → write failing test → confirm red → minimal fix → confirm green → one atomic commit → update backlog.

---

## Active learning hooks: wired (2026-05-17)

Three hooks are now registered in `.claude/settings.json`:

| Hook | Event | File |
|---|---|---|
| bash-logger | PostToolUse/Bash | `.claude/hooks/bash-logger.py` |
| tool-registry | PostToolUse/Write | `.claude/hooks/tool-registry.py` |
| pattern-analyzer | Stop | `.claude/hooks/pattern-analyzer.py` |

`make test` is now live (28 tests, all passing). `make validate-hooks` is fully green.

---

## v2 candidate deliverables (not yet scoped)

From `plan.md` §13 "load-bearing soon" list — not committed, just the queue to draw from:

- `/fix` skill — atomic bug fix with TDD loop
- `/review` skill — code review against `.agents/` rules  
- PostToolUse hooks — format, type-check, test on save
- PreToolUse hook — MCP compliance guardrail (C1 v2 candidate)
- `/scaffold` skill — wraps `make scaffold` with guided prompts

---

## Active hook to be aware of

After every `git commit` (not `--amend`), `scripts/update_docs_on_commit.py` runs and inserts a bullet under `## [Unreleased]` in `CHANGELOG.md`. The file will be unstaged after every commit — fold it in with `git commit --amend --no-edit` or let it ride into the next commit.

---

## Key files

| File | Why you'd open it |
|---|---|
| `docs/adr/ADR-004-factory-test-strategy.md` | Full Tier 2 milestone spec |
| `docs/adr/ADR-003-team-coordination.md` | Carry-back rules for Step 4 |
| `scripts/scaffold.py` | What `make scaffold` calls |
| `templates/` | What gets stamped into `fb_test_alpha` |
| `.claude/skills/spec/SKILL.md` | Reference when building `/fix` |
| `MANUAL.md` §10 | Integration milestone also documented here |
