# ADR-007: Documentation Cleanup

**Status:** Proposed  
**Date:** 2026-05-15  
**Deciders:** Senior dev  
**Fixes:** C1, C2, C3 — Minor concerns from architect review  

---

## Context

Three concerns surfaced during the architect review of `plan.md` that do not require a new system or process — only targeted edits to the doc itself.

- **C1:** The "all integrations through MCP" rule (§8.4) is stated as policy but has no enforcement mechanism. It's a convention and should be named as one.
- **C2:** §11 (Agent SDK publishing) is premature for a team that has nothing built yet. It costs reading time and signals ambition that distracts from v1.
- **C3:** The model selection rubric in §4.4 is stated as settled fact but will be wrong within months as models evolve.

---

## Decision

Three targeted edits to `plan.md`. No new files, no structural changes.

---

### C1 — Name the MCP convention as a convention

**In `plan.md` §8.4**, after the paragraph ending "...the audit trail is uniform — connector calls appear in transcripts the same way as native tool calls," add:

> **Note:** This "all integrations through MCP" rule is enforced by convention, not by an automated guardrail. There is no hook today that detects when an agent shells out to an external system without going through MCP. Teams must rely on code review and the carry-back culture (ADR-003) to maintain it. A PreToolUse hook enforcing this is a candidate for v2.

---

### C2 — Collapse §11 to a footnote

**Replace `plan.md` §11 in its entirety** with:

> ## 11. Agent SDK and publishing outward
>
> Skills, subagents, and hooks authored here should eventually be publishable via the Agent SDK — but only once they're stable. v1 does not design for this. When the factory has survived one real sibling project end-to-end, revisit which artifacts are worth publishing and what stable interfaces they require.

---

### C3 — Add a review cadence to the model rubric

**In `plan.md` §4.4**, add a note below the table:

> **Review cadence:** Check this table quarterly against Anthropic's release notes. Model capabilities and pricing change faster than documents do; a stale rubric produces bad cost/quality decisions.

---

## Sequencing

These edits can be done in a single PR. They do not depend on any other ADR. They can be executed in parallel with ADR-001 or at any point before the first developer reads `plan.md` cold.

Assign to whichever junior is most comfortable doing a focused doc edit as a first contribution — it's a low-risk first PR.

---

## Consequences

**Good:**
- C1 correction prevents a new team member from trusting that MCP compliance is automatically enforced. Sets correct expectations.
- C2 reduction cuts the cognitive load of plan.md by roughly one section. Juniors reading it for the first time won't be distracted by publishing infrastructure.
- C3 addition gives the team a concrete signal for when to revisit model choices.

**Risk:** Minimal. These are edits to a doc with no downstream code dependencies.
