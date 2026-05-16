# continue.md

> Pick up here in the next session.

**Repo:** `flying_buttress` — a software factory for AI-native development  
**Branch:** `main` (clean, pushed, up to date)  
**Last commit:** pending — ADR-004 accepted this session

---

## What was done this session

1. **Accepted ADR-004** (factory test strategy) — Three-tier test strategy fully documented:
   - Tier 1 PR smoke checklist added to `ONBOARDING.md` Step 5 and `MANUAL.md` §9.
   - Tier 2 integration milestone (scaffold → `/spec` → `/fix` → carry-back) added to `MANUAL.md` §10, gates v2 start.
   - Tier 3 carry-back evidence gate labeled and expanded in `MANUAL.md` §11.
   - ADR-004 marked Accepted; `docs/adr/README.md` updated; `backlog.md` G4 closed.

---

## ADR status going into next session

| ADR | Gap | Status |
|---|---|---|
| ADR-001 | G1 — v1 MVP scope | **Accepted** |
| ADR-002 | G3 — Day 1 onboarding | **Accepted** |
| ADR-003 | G2 — Team coordination | **Accepted** |
| ADR-004 | G4 — Factory test strategy | **Accepted** |
| ADR-005 | G5 — Makefile underlay | Proposed ← **next** |
| ADR-006 | G6 — Settings governance | Proposed |
| ADR-007 | C1/C2/C3 — Doc cleanup | Proposed |

---

## Next step: ADR-005

**File:** `docs/adr/ADR-005-makefile-underlay.md`

ADR-005 specifies the Makefile as the durable substrate beneath all Claude Code skills. Every factory workflow expressible as a Make target should be. Claude Code skills call Make; Make is the underlay that survives any tool change.

Read ADR-005 in full before starting — it defines required targets and the constraint that skills must call `make <target>` rather than shelling out directly.

---

## Active hook to be aware of

After every `git commit` (not `--amend`), `scripts/update_docs_on_commit.py` runs and updates `CHANGELOG.md`. The updated file will be unstaged — amend with `git commit --amend --no-edit` to fold it in, or let it ride into the next commit.

---

## Key files

| File | Why you'd open it |
|---|---|
| `docs/adr/ADR-005-makefile-underlay.md` | The spec for the next deliverable |
| `Makefile` | Primary artifact for ADR-005 |
| `docs/adr/README.md` | Update status when ADR-005 is accepted |
| `backlog.md` | G5 is the gap ADR-005 closes |
