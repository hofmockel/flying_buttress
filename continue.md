# continue.md

> Pick up here in the next session.

**Repo:** `flying_buttress` — a software factory for AI-native development  
**Branch:** `main` (clean, pushed, up to date)  
**Last commit:** pending — ADR-006 accepted this session

---

## What was done this session

1. **Committed hooks and tooling** — `.claude/hooks/`, `tools/`, updated `settings.json` and `.gitignore` were untracked; committed them. `.venv/` and `schema/` added to `.gitignore`.

2. **Accepted ADR-006** (settings governance) — MANUAL.md §7 expanded with the "what requires a settings PR" trigger list and the senior review checklist. `_comment` key in `settings.json` already names the owner and links ADR-006. ADR-006 marked Accepted; G6 closed.

---

## ADR status going into next session

| ADR | Gap | Status |
|---|---|---|
| ADR-001 | G1 — v1 MVP scope | **Accepted** |
| ADR-002 | G3 — Day 1 onboarding | **Accepted** |
| ADR-003 | G2 — Team coordination | **Accepted** |
| ADR-004 | G4 — Factory test strategy | **Accepted** |
| ADR-005 | G5 — Makefile underlay | **Accepted** |
| ADR-006 | G6 — Settings governance | **Accepted** |
| ADR-007 | C1/C2/C3 — Doc cleanup | Proposed ← **next** |

---

## Next step: ADR-007

**File:** `docs/adr/ADR-007-documentation-cleanup.md`

ADR-007 closes the three smaller doc concerns (C1, C2, C3) from the backlog:
- **C1** — "All integrations through MCP" is a convention, not a guardrail; name it explicitly.
- **C2** — §11 (Agent SDK publishing) is premature noise; move or collapse it.
- **C3** — Model selection rubric in §4.4 will drift; add a quarterly review cadence note.

All three are `plan.md` edits. Read ADR-007 in full before starting.

---

## Active hook to be aware of

After every `git commit` (not `--amend`), `scripts/update_docs_on_commit.py` runs and updates `CHANGELOG.md`. The updated file will be unstaged — amend with `git commit --amend --no-edit` to fold it in, or let it ride into the next commit.

---

## Key files

| File | Why you'd open it |
|---|---|
| `docs/adr/ADR-007-documentation-cleanup.md` | The spec for the next deliverable |
| `plan.md` | Primary target for all three C1/C2/C3 edits |
| `docs/adr/README.md` | Update status when ADR-007 is accepted |
| `backlog.md` | C1, C2, C3 are the gaps ADR-007 closes |
