# ADR-005: Makefile Underlay

**Status:** Proposed  
**Date:** 2026-05-15  
**Deciders:** Senior dev  
**Fixes:** G5 — Vendor lock-in deeper than acknowledged; no durable substrate  

---

## Context

`plan.md` §5.1 mentions "the Makefile substrate referenced in `buttress.md` §6 is the durable underlay" but never specifies what that Makefile contains or which skills delegate to it. Every factory workflow is currently expressed only as Claude Code-specific primitives (skills, hooks, subagents). If Claude Code changes pricing, retires a feature, or the team needs to use a different tool for any period, no workflow survives.

This is a strategic risk, not a day-one blocker. It goes in v1.5 — after the five v1 deliverables are shipped but before v2 starts.

---

## Decision

**Add a `Makefile` at the repo root. Every skill that shells out to a project operation must delegate to a Make target. Skills call Make; Make is the durable substrate.**

The constraint: if Claude Code is unavailable, `make <target>` must be the fallback that a developer can run manually to accomplish the same operation.

### Required targets for v1.5

| Target | What it does | Called by |
|---|---|---|
| `make spec` | Prompts for a feature slug, then opens the spec template at `docs/specs/<slug>.md` | `/spec` skill |
| `make test` | Runs the project's test suite (or `echo "no tests yet"` until one exists) | PostToolUse hook (v2) |
| `make lint` | Runs the linter (or `echo "no linter yet"`) | PostToolUse hook (v2) |
| `make fmt` | Runs the formatter | PostToolUse hook (v2) |
| `make validate-hooks` | Runs the tier-1 smoke checklist from ADR-004 non-interactively | CI (v2) |
| `make scaffold TARGET=<path>` | Stamps out a sibling project at `TARGET` | `/scaffold` skill (v2) |

### Constraint on skill authors

When writing a skill that invokes a shell command for a project operation, the author must:
1. Write the Make target first.
2. Have the skill call `make <target>` rather than the raw command.
3. Document the target in the table above.

Skills that do research, conversation, or Claude Code-internal operations (Explore, Plan, AskUserQuestion) are exempt — they have no shell equivalent.

### What this does NOT do

- Does not replace skills. Skills carry context, compose subagents, and respect the permission system. Make cannot do those things.
- Does not define the project-under-construction's Makefile. This is the factory's Makefile; sibling projects scaffold their own.

---

## Consequences

**Good:**
- A developer can run `make spec` without Claude Code running. The factory's core operations are not hostage to a single tool.
- Hooks become more testable: `make validate-hooks` can run in a non-interactive context.
- New team members with Make familiarity have a fallback if they're not yet comfortable with Claude Code.

**Risks:**
- Make targets and skill logic will drift over time if not maintained together. Mitigated by: the skill author is responsible for the corresponding Make target (enforced by ADR-003 code review).
- Some operations (plan mode, subagent spawning) genuinely have no Make equivalent. Those are documented as Claude Code-only in the skill's SKILL.md.
