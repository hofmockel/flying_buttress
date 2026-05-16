# continue.md

> Pick up here in the next session.

**Repo:** `flying_buttress` — a software factory for AI-native development  
**Branch:** `main` (clean, pushed, up to date)  
**Last commit:** pending — ADR-005 accepted this session

---

## What was done this session

1. **Accepted ADR-004** (factory test strategy) — Three-tier test strategy fully documented. PR smoke checklist in ONBOARDING.md and MANUAL.md. Tiers 2 and 3 in MANUAL.md §10–11. ADR-004 marked Accepted; G4 closed.

2. **Accepted ADR-005** (Makefile underlay) — All six required targets already in place. `plan.md` §5.1 updated to point concretely at the Makefile and state the skill-to-Make constraint (ADR-005). ADR-005 marked Accepted; G5 closed.

---

## ADR status going into next session

| ADR | Gap | Status |
|---|---|---|
| ADR-001 | G1 — v1 MVP scope | **Accepted** |
| ADR-002 | G3 — Day 1 onboarding | **Accepted** |
| ADR-003 | G2 — Team coordination | **Accepted** |
| ADR-004 | G4 — Factory test strategy | **Accepted** |
| ADR-005 | G5 — Makefile underlay | **Accepted** |
| ADR-006 | G6 — Settings governance | Proposed ← **next** |
| ADR-007 | C1/C2/C3 — Doc cleanup | Proposed |

---

## Next step: ADR-006

**File:** `docs/adr/ADR-006-settings-governance.md`

ADR-006 defines who can merge changes to `.claude/settings.json`, what review is required, and how local overrides are handled. Read ADR-006 in full — it will specify a governance model and may require updating MANUAL.md §7 (permissions) and the ownership table in §9.

---

## Active hook to be aware of

After every `git commit` (not `--amend`), `scripts/update_docs_on_commit.py` runs and updates `CHANGELOG.md`. The updated file will be unstaged — amend with `git commit --amend --no-edit` to fold it in, or let it ride into the next commit.

---

## Key files

| File | Why you'd open it |
|---|---|
| `docs/adr/ADR-006-settings-governance.md` | The spec for the next deliverable |
| `.claude/settings.json` | Primary artifact governed by ADR-006 |
| `MANUAL.md` | §7 and §9 may need updating |
| `docs/adr/README.md` | Update status when ADR-006 is accepted |
| `backlog.md` | G6 is the gap ADR-006 closes |
