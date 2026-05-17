# Spec: /fix skill

**Slug:** fix-skill
**Date:** 2026-05-17
**Status:** Draft

## Problem

The Tier 2 integration milestone (ADR-004 §Tier 2, Step 3) requires a `/fix` skill to exist before the milestone can run end-to-end. Currently there is no guided, repeatable workflow for bug fixes in the factory. Developers either fix bugs ad-hoc or skip the step entirely, producing no test evidence. Without a skill, the milestone's pass condition — bug reproduced, failing test written, fix committed — cannot be met consistently.

## Proposed solution

A `/fix` skill that drives a strict TDD loop: identify the bug (from an argument or backlog.md), map the affected code with an Explore subagent, write a failing test that pins the regression, apply the minimal fix, run `make test` to go green, and commit test + fix together in one atomic commit. No plan mode gate — the bug is already decided; the red-green cycle is the governance. A `make fix` stub is added to the Makefile and the template so the pattern is discoverable.

## Scope

### In scope
- `.claude/skills/fix/SKILL.md` — skill file for the factory repo
- `templates/.claude/skills/fix/SKILL.md.tmpl` — template stamped into scaffolded projects
- `Makefile` — `fix` target added to `.PHONY` and as an echo stub
- `templates/Makefile.tmpl` — same additions for scaffolded projects
- Acceptance test: Tier 2 milestone Step 3 (plant a bug in fb_test_alpha, run /fix, confirm test + fix committed)

### Out of scope
- Unit tests for the SKILL.md prose itself (not executable)
- Automated detection of bugs (skill requires a human or argument to name the bug)
- Settings/hook changes (no new hooks needed)
- Python tool stubs (all built-in tools are sufficient)

## Implementation plan

1. `docs/specs/fix-skill.md` — this file (written by /spec run)
2. `.claude/skills/fix/SKILL.md` — 8-step skill: signal active_skill, identify bug, explore, write failing test, confirm red, apply fix, confirm green, commit + update backlog
3. `templates/.claude/skills/fix/SKILL.md.tmpl` — same skill with YAML frontmatter (name, description), without factory-specific references
4. `Makefile` — add `fix` to `.PHONY`; add `fix:` target that echoes usage
5. `templates/Makefile.tmpl` — same additions

## Tests

No unit tests — skill is prose instructions. Acceptance test is Tier 2 milestone Step 3:
- Plant a deliberate bug in `../fb_test_alpha`
- Run `/fix <bug description>` inside fb_test_alpha
- Confirm: failing test written before fix, `make test` goes green, single commit contains both test and fix

## Open questions

None — design confirmed before implementation.
