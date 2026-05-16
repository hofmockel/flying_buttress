# continue.md

> Pick up here in the next session.

**Repo:** `flying_buttress` — a software factory for AI-native development  
**Branch:** `main` (clean, pushed, up to date)  
**Last commit:** pending — ADR-007 accepted this session

---

## What was done this session

1. **Committed hooks and tooling** — `.claude/hooks/`, `tools/`, updated `settings.json` and `.gitignore` were untracked; committed them. `.venv/` and `schema/` added to `.gitignore`.

2. **Accepted ADR-006** (settings governance) — MANUAL.md §7 expanded with the "what requires a settings PR" trigger list and the senior review checklist. ADR-006 marked Accepted; G6 closed.

3. **Accepted ADR-007** (doc cleanup) — Three targeted `plan.md` edits: C1 convention note in §8.4, C2 §11 collapsed to one paragraph, C3 quarterly review cadence in §4.4. ADR-007 marked Accepted; C1/C2/C3 closed.

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
| ADR-007 | C1/C2/C3 — Doc cleanup | **Accepted** |

**All seven ADRs accepted. The backlog is clear.**

---

## Next step: C4 (deny list) or v1 done condition

All critical gaps and smaller concerns are closed. One open item remains in backlog.md:

**C4 — `settings.json` deny list deferred** — The deny list was intentionally omitted from v1. Candidate rules are documented in `backlog.md`. The recommendation was to add them once the allow list has stabilized and the team has a session's worth of data. Review C4 and decide: add the deny list now, or call v1 complete and move to the integration milestone (ADR-004 Tier 2).

The v1 done condition from ADR-001: *five deliverables shipped and stable*. Check `docs/adr/ADR-001-v1-mvp-scope.md` to verify all five are in place before declaring v1 done.

---

## Active hook to be aware of

After every `git commit` (not `--amend`), `scripts/update_docs_on_commit.py` runs and updates `CHANGELOG.md`. The updated file will be unstaged — amend with `git commit --amend --no-edit` to fold it in, or let it ride into the next commit.

---

## Key files

| File | Why you'd open it |
|---|---|
| `docs/adr/ADR-001-v1-mvp-scope.md` | v1 done condition — verify all five deliverables are in |
| `backlog.md` | C4 deny list — the one remaining open item |
| `.claude/settings.json` | Target if adding the deny list |
