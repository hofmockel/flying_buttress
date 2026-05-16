# continue.md

> Pick up here in the next session.

**Repo:** `flying_buttress` — a software factory for AI-native development  
**Branch:** `main` (clean, pushed, up to date)  
**Last commit:** pending — v1 complete

---

## What was done this session

1. **Committed hooks and tooling** — `.claude/hooks/`, `tools/`, updated `settings.json` and `.gitignore` were untracked; committed them. `.venv/` and `schema/` added to `.gitignore`.

2. **Accepted ADR-006** (settings governance) — MANUAL.md §7 expanded with trigger list and review checklist. ADR-006 marked Accepted; G6 closed.

3. **Accepted ADR-007** (doc cleanup) — Three targeted `plan.md` edits: C1 convention note in §8.4, C2 §11 collapsed, C3 quarterly review cadence in §4.4. ADR-007 marked Accepted; C1/C2/C3 closed.

4. **C4 deny list added** — deny rules added to `.claude/settings.json` and `templates/.claude/settings.json.tmpl`. All eight v1 deliverables verified present. **v1 declared complete.**

---

## ADR status

| ADR | Gap | Status |
|---|---|---|
| ADR-001 | G1 — v1 MVP scope | **Accepted** |
| ADR-002 | G3 — Day 1 onboarding | **Accepted** |
| ADR-003 | G2 — Team coordination | **Accepted** |
| ADR-004 | G4 — Factory test strategy | **Accepted** |
| ADR-005 | G5 — Makefile underlay | **Accepted** |
| ADR-006 | G6 — Settings governance | **Accepted** |
| ADR-007 | C1/C2/C3 — Doc cleanup | **Accepted** |

**All seven ADRs accepted. Backlog clear. v1 complete.**

---

## Next step: Tier 2 integration milestone (ADR-004)

v1 is done. The next gate before v2 work starts is the **Tier 2 integration milestone** from ADR-004:

1. Run `make scaffold TARGET=../fb_test_alpha` to stamp out a sibling test project.
2. Run `/spec` inside `fb_test_alpha` on a real problem — a readable PRD must be produced.
3. Run `/fix` on a planted bug inside `fb_test_alpha` — reproduce the bug, write a failing test, apply the fix.
4. Carry back at least one improvement to flying_buttress following the carry-back rules (ADR-003).

**Who runs it:** senior, with at least one junior observing. **Blocker:** `/fix` skill does not exist yet. Either build `/fix` first (v2 item) or run the milestone with a manual fix loop and note the gap.

---

## Active hook to be aware of

After every `git commit` (not `--amend`), `scripts/update_docs_on_commit.py` runs and updates `CHANGELOG.md`. The updated file will be unstaged — amend with `git commit --amend --no-edit` to fold it in, or let it ride into the next commit.

---

## Key files

| File | Why you'd open it |
|---|---|
| `docs/adr/ADR-004-factory-test-strategy.md` | Tier 2 milestone definition |
| `scripts/scaffold.py` | Run the scaffold to create fb_test_alpha |
| `CHANGELOG.md` | Track v1 → v2 transition |
