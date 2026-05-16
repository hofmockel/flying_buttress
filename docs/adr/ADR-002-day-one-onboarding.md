# ADR-002: Day 1 Onboarding Path

**Status:** Accepted  
**Date:** 2026-05-15  
**Deciders:** Senior dev  
**Fixes:** G3 — No Day 1 onboarding path  
**Priority:** Execute this before any other ADR. Juniors are blocked right now.

---

## Context

The team is 1 senior + 1–2 junior developers. The juniors' stated blocker: *they don't know where to start in the repo at all.* Nothing is built yet — it's all docs. A new developer cloning this repo has no obvious entry point, no setup steps, and no way to know what they're supposed to contribute.

The factory has no `ONBOARDING.md`. The closest substitute is `plan.md` §1.3, which gives a reading order — not a setup path.

---

## Decision

**Write `ONBOARDING.md` at the repo root.** It must answer: "I just cloned this. What do I do?"

The file must work in the current state (docs-only) and remain accurate as the factory is built. It is a living document; updating it is part of every carry-back.

### Required content — in this order

**Step 1 — Understand the factory (30 min, one-time)**  
Read `buttress.md` in full. Then read `plan.md` §1–§3 and §9. Skip the rest of `plan.md` for now.  
Goal: know what the factory is, what the four pillars are, and how the lifecycle maps to Claude Code.

**Step 2 — Understand the current work queue (10 min)**  
Read `backlog.md`. Then read `docs/adr/README.md` and skim each open ADR.  
Goal: know what's being built and what's already decided.

**Step 3 — Pick up a task (5 min)**  
Find the lowest-numbered ADR with status `Proposed`. That is the next thing to build. If someone else is already on it, take the next one.  
If all ADRs are `Accepted` and you're not sure what's left, ask the senior.

**Step 4 — Set up your environment**  
*(This section grows as the factory is built. Today it is minimal.)*  
- Clone the repo.  
- Install Claude Code CLI if not already installed.  
- Run `claude` from the repo root and confirm it loads.  
- There is nothing else to install yet.

**Step 5 — Open your first PR**  
Implement the deliverable from the ADR you picked. Open a PR with:  
- A one-line title naming the ADR (e.g., `ADR-002: add ONBOARDING.md`).  
- A one-paragraph description: what changed and why.  
- If you carried back an improvement from a test project, include the evidence (transcript excerpt or output artifact).  
Self-merge after 48 hours if there is no blocking comment. The senior reviews at the weekly sync.

---

## Maintenance rule

`ONBOARDING.md` must be updated whenever:
- Step 4 (environment setup) gains new required tools.
- The ADR sequence changes.
- The v1 scope is redefined.

Add "update ONBOARDING.md if needed" to the PR checklist in ADR-003.

---

## Consequences

**Good:**
- Juniors have a concrete first action within minutes of cloning.
- The ADR sequence becomes the natural work queue — no separate task tracker needed for v1.
- Senior spends less time orienting new contributors.

**Risk:**
- `ONBOARDING.md` will go stale if it's not part of the carry-back habit. Mitigated by the maintenance rule above.
