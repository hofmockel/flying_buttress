# Architecture Decision Records

One ADR per gap from `backlog.md`. Execute in sequence — later ADRs depend on decisions made in earlier ones.

| Order | ADR | Gap | Status |
|---|---|---|---|
| 1 | [ADR-001](ADR-001-v1-mvp-scope.md) | G1 — No v1 scope | Accepted |
| 2 | [ADR-002](ADR-002-day-one-onboarding.md) | G3 — No Day 1 onboarding | Accepted |
| 3 | [ADR-003](ADR-003-team-coordination.md) | G2 — No team coordination model | Accepted |
| 4 | [ADR-004](ADR-004-factory-test-strategy.md) | G4 — No factory test strategy | Proposed |
| 5 | [ADR-005](ADR-005-makefile-underlay.md) | G5 — Vendor lock-in / no durable substrate | Proposed |
| 6 | [ADR-006](ADR-006-settings-governance.md) | G6 — Settings governance absent | Proposed |
| 7 | [ADR-007](ADR-007-documentation-cleanup.md) | C1, C2, C3 — Minor doc concerns | Proposed |

**Why this order:** ADR-001 defines the scope everyone works within. ADR-002 unblocks junior developers immediately. ADR-003 defines how changes flow. ADR-004 defines what "done" means before carry-backs start. ADR-005 and ADR-006 are strategic — important but not day-one blockers. ADR-007 is doc cleanup that can happen anytime.

**ADR status definitions:**
- **Proposed** — drafted; not yet accepted by the team
- **Accepted** — senior has reviewed; team is executing against it
- **Superseded** — replaced by a later ADR; link to successor

**Done condition for the factory:** the factory has been used to build one real sibling project end-to-end (scaffolded, spec'd, fixed a bug, reviewed). That is the acceptance test for v1.
