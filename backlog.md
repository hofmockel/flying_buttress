# backlog.md

> Open gaps, concerns, and carry-back items for the factory. All closed items are recorded in CHANGELOG.md.

---

## Bugs

| Bug | Description | Status |
|-----|-------------|--------|

---

## Bug-Hunt Protocol

### Current state (post-round-6)

- **Round 6** (10 surfaced; 4 real, 6 duplicate, 0 dismissed): 4 `ux`. Overlap 60% (6/10). Files hit: bash-logger.py (2nd and 3rd bugs), pattern-analyzer.py (3rd and 4th bugs) — all revisited files, new encoding angles.
- **Severity slide**: ✓ — median `ux`; dropped from `silent` (round 5).
- **Overlap rate**: ✓ — 60% (at threshold; first round to meet it).
- **File coverage**: ✓ — 100% cumulative.

**STOP TRIGGER FIRED. All 3 signals met. Surface is saturated — overlap crossed 60%, severity slid to ux, all files covered.**

### Previous state (post-round-5)

- **Round 5** (6 surfaced; 4 real, 2 duplicate, 0 dismissed): 2 `silent`, 1 `ux`, 1 `cosmetic`. Overlap 33% (2/6). Files hit: search-first.py (2nd bug), scaffold.py (new), update_docs_on_commit.py (5th bug), truncate-output.py (revisit/dup) — mix of new angles and revisits.
- **Severity slide**: ✗ — median `silent`; rose from `cosmetic` (round 4). Duplicate cluster skews harder.
- **Overlap rate**: ✗ — 33% (rising from 0% but below 60% threshold).
- **File coverage**: ✓ — 100% cumulative.

**Verdict: Run one more round. 2 of 3 signals met; overlap rising (0%→33%) — one more round to confirm it crosses 60%.**

### Previous state (post-round-4)

- **Round 4** (8 surfaced; 5 real, 3 dismissed, 0 duplicate): 2 `silent`, 3 `cosmetic`. Overlap 0%. Files hit: caveman-reminder.py, mcp_check.py, update_docs_on_commit.py (4th bug), embeddings.py (3rd bug), compact-trigger.py (2nd bug), search.py (2nd bug).
- **Severity slide**: ✓ — median `cosmetic`; dropped from `silent` (round 3).
- **Overlap rate**: ✗ — 0%.
- **File coverage**: ✓ — ~100% cumulative.

**Verdict: Run one more round. 2 of 3 signals met.**

### Previous state (post-round-3)

- **Round 3** (5 surfaced; 5 real, 0 dismissed, 0 duplicate): 3 `silent`, 1 `ux`, 1 `cosmetic`. Overlap 0%. Files hit: bash-logger.py, tool-registry.py, stats.py, update_docs_on_commit.py (3rd bug), index-refresh.py (2nd bug).
- **Severity slide**: ✓ — median `silent`; dropped from `ux` (round 2).
- **Overlap rate**: ✗ — 0%.
- **File coverage**: ✓ — ~87% cumulative.

**Verdict: Keep hunting. 2 of 3 signals met.**

### Previous state (post-round-2)

- **Round 2** (5 surfaced; 5 real, 0 dismissed, 0 duplicate): 1 `data-loss`, 2 `ux`, 1 `silent`, 1 `cosmetic`. Overlap 0%. Files hit: compact-trigger.py, embeddings.py, Makefile, truncate-output.py — all first sweep.
- **Severity slide**: ✗ — median `ux`; Round 1 median was `silent`. Severity rose (data-loss bug found).
- **Overlap rate**: ✗ — 0% (no rediscoveries; surface still fresh).
- **File coverage**: ✓ — ~9/15 key files hit cumulatively (~60%).

**Verdict: Keep hunting. 1 of 3 signals met.**

### Previous state (post-round-1)

- **Round 1** (7 surfaced; 7 real, 0 dismissed, 0 duplicate): 6 `silent`, 1 `ux`. Overlap 0%. Files hit: search-first.py, index-refresh.py, search.py, update_docs_on_commit.py, pattern-analyzer.py — all first sweep.
- **Severity slide**: n/a — Round 1, no prior baseline.
- **Overlap rate**: ✗ — 0% (Round 1; expected).
- **File coverage**: ✗ — 5/15 key files hit (~33% of hooks + scripts surface).

**Verdict: Keep hunting. Round 1 baseline — overlap and file coverage both below threshold, severity slide not applicable.**
