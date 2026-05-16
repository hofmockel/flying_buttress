# ADR-004: Factory Test Strategy

**Status:** Proposed  
**Date:** 2026-05-15  
**Deciders:** Senior dev  
**Fixes:** G4 — No factory test strategy  

---

## Context

`plan.md` §10.4 names the factory's test suite: "Can we build something real with it?" That's the right end goal but it's not a test strategy — it's a ship condition. Without intermediate checks, a change to a hook or skill can silently break the factory and the team won't know until something goes wrong mid-build.

The factory is all docs today. The test strategy must work as artifacts are added, not just at the end.

The agreed done condition: **the factory has been used to build one real sibling project end-to-end.**

---

## Decision

Three-tier strategy, each tier activated as the factory matures.

---

### Tier 1 — PR smoke checklist (active from day one)

Every PR that touches a skill, hook, or `settings.json` must include a checked smoke checklist in the PR description. The author runs these manually and checks them before opening the PR.

The checklist grows as the factory is built. Starting checklist:

```
- [ ] Opened Claude Code from the repo root with no errors
- [ ] CLAUDE.md loads and routes correctly (confirm by asking Claude "what is this repo?")
- [ ] If skill changed: ran the skill on a toy input and got expected output shape
- [ ] If settings.json changed: confirmed Claude Code started without permission errors
- [ ] ONBOARDING.md is still accurate (no steps are broken by this change)
```

Add items to this checklist whenever a regression is found. Never remove items.

**Owner of the checklist:** the author of each PR. The senior verifies at the weekly sync that it was actually run (spot-check).

---

### Tier 2 — Integration milestone (before any v2 features start)

Before any "load-bearing soon" item from `plan.md` §13 is started, the factory must pass the integration milestone:

1. Run `/scaffold` to stamp out a sibling test project at `../fb_test_alpha`.
2. Run `/spec` inside `fb_test_alpha` on a real (non-toy) problem. A readable PRD must be produced.
3. Run `/fix` on a planted bug inside `fb_test_alpha`. The bug must be reproduced, a failing test written, and the fix applied.
4. Carry back at least one improvement from `fb_test_alpha` to flying_buttress following the carry-back rules in ADR-003.

If any step fails, it is a blocker. Open an issue, fix it, and re-run from step 1.

**Who runs it:** senior, with at least one junior observing.  
**When:** after all five v1 deliverables from ADR-001 are merged and in a stable state.

---

### Tier 3 — Carry-back evidence gate (active from first carry-back)

Any improvement carried back from a sibling project must include evidence in the PR that it works. Acceptable evidence:

- A transcript excerpt showing the skill or hook producing the expected output.
- An output artifact (e.g., the PRD that `/spec` produced, the test that `/fix` wrote).
- A screenshot of the factory running correctly in the new context.

"I tested it and it works" with no artifact is not acceptable. The senior enforces this at weekly sync review.

---

## What this does NOT include

- Automated tests (no test runner, no CI). The factory is too early for this and the overhead would exceed the benefit in v1.
- Snapshot testing of skill outputs. Skill outputs are intentionally variable (they're LLM-generated); testing their shape is more useful than their content. Deferred to v2 if needed.

---

## Consequences

**Good:**
- Tier 1 catches regressions before they land. Cheap to run, cheap to maintain.
- Tier 2 gives the team a shared moment of "yes, the factory works" before adding complexity.
- Tier 3 creates a light evidence culture without bureaucracy.

**Risks:**
- Tier 1 checklist will be skipped under time pressure. The senior spot-checks at the weekly sync, but cannot enforce it. Name this risk explicitly: if the checklist is skipped, regressions will ship.
- Tier 2 depends on `/scaffold` existing, which is out of v1 scope. Implication: the integration milestone cannot run until `/scaffold` is built in v2. That's acceptable — tier 1 carries the load until then.
