# ADR-001: v1 MVP Scope

**Status:** Accepted  
**Date:** 2026-05-15  
**Deciders:** Senior dev  
**Fixes:** G1 — No sequencing; §14 is a menu, not a plan  

---

## Context

`plan.md` §14 is explicitly "a possibility survey — not a commitment plan." It lists ~30 things that could be scaffolded. A three-person team with nothing built cannot parallelize 30 open choices. Without a committed scope, juniors will start on different parts of the menu and produce an inconsistent factory.

The stated first bar for the factory: *a developer can run `/spec` and get a usable PRD out.*

---

## Options considered

**Option A — Minimal: CLAUDE.md hierarchy + `/spec` skill only.**  
Build the minimum that demonstrates the factory works. Ship everything else in v2.

**Option B — Safety-first: hooks and `settings.json` before any skills.**  
Establish the rails before anyone builds on top of them. Nothing lands without safety gates.

**Option C — Full §13 load-bearing list.**  
Implement everything marked "load-bearing now" before calling v1 done. ~12 items.

---

## Decision

**Option A, with a defined stop condition.**

v1 is exactly these eight deliverables, in order:

1. **Root `CLAUDE.md`** — router only; one paragraph overview, pointers to `buttress.md`, `plan.md`, `.agents/`, and `docs/adr/`. No inline rules.
2. **`.agents/` rules files** — four files: `backend.md`, `frontend.md`, `testing.md`, `security.md`. Stubs are acceptable; they must exist and be non-empty.
3. **`settings.json` baseline** — permissions block only (common allow/deny list). No hooks yet.
4. **`/spec` skill** — end-to-end: enters plan mode, uses Explore + Plan subagents, prompts for approval via `AskUserQuestion`, writes output to `docs/specs/<slug>.md`. This is the v1 acceptance test.
5. **`ONBOARDING.md`** — see ADR-002; must exist before juniors start on items 1–4.
6. **`Makefile`** — root-level durable substrate (ADR-005 pulled forward to v1); targets: `spec`, `test`, `lint`, `fmt`, `validate-hooks`, `scaffold`. Skills call Make; stubs are acceptable for targets with no tooling yet.
7. **`templates/`** — the files that `/scaffold` stamps into every new sibling project. This is the factory backbone: CLAUDE.md, `.agents/`, `settings.json`, `/spec` skill, and `Makefile` as templated copies with `{{project_name}}` / `{{project_slug}}` / `{{date}}` substitution markers.
8. **`scripts/scaffold.py`** — thin Python script that copies `templates/` into a target directory, performs substitutions, and initializes a git repo. Called by `make scaffold TARGET=<path>`.

v1 is complete when a developer (not the person who wrote the skill) runs `/spec` on a toy problem and produces a readable PRD without assistance.

**What is explicitly out of v1:** hooks (all four types), `/fix`, `/refactor`, memory system, MCP connectors beyond what ships by default, custom subagents.

**Note on ADR-005:** The Makefile underlay was originally deferred to v1.5. It is pulled into v1 here because `templates/` and `scripts/scaffold.py` both depend on it — the scaffold script calls `make scaffold`, and every template includes a starter Makefile.

---

## Consequences

**Good:**
- Scope is small enough for a junior to own one item each.
- `/spec` running end-to-end proves the factory's core loop without needing hooks, memory, or MCP.
- The stop condition is observable by someone other than the author.

**Risks:**
- Without hooks, bad operations are not blocked during factory development itself. Mitigated by: senior awareness and the settings.json deny list.
- The `.agents/` stubs will be weak at first. That's acceptable — they're the foundation, not the finished product.

**Next:** Once v1 is accepted by the team, open one issue per deliverable and assign ownership. ADR-003 defines the coordination model for that work.
