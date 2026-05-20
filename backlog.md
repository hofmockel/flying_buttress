# backlog.md

> Open gaps, concerns, and carry-back items for the factory. All closed items are recorded in CHANGELOG.md.

---

## Bugs

| Bug | Description | Status |
|-----|-------------|--------|
| **pattern-analyzer _append_entry inserts into the last fence, not the jsonlines fence** | `text.rfind(_FENCE_CLOSE)` finds the last ` ``` ` in the file; any markdown block after the jsonlines block causes new entries to land in the wrong fence, corrupting both blocks. `pattern-analyzer.py:78`. | open |
| **pattern-analyzer _load_existing_skeletons toggles on any fence marker** | `if stripped.startswith("```"): in_block = not in_block` triggers on every fence opener/closer regardless of language; JSON objects in other fenced blocks are falsely counted as already-queued skeletons. `pattern-analyzer.py:59`. | open |
| **compact-trigger `last` state never resets between sessions** | After a large session fires the nudge (e.g. 2 MB), a subsequent smaller-but-over-threshold session (e.g. 600 KB) is silently skipped because `size < last + hysteresis`. State file is never cleared on new/smaller sessions. `compact-trigger.py:71`. | open |
| **embeddings.py stores `f.name` instead of relative path for root-glob files** | `out.append((st, f.name, k, t))` uses just the filename; `README.md` and `docs/adr/README.md` both get `source_path="README.md"`, so the second upsert silently overwrites the first in the DB. `embeddings.py:191`. | open |
| **embeddings.py refresh() crashes with unhandled OperationalError on uninitialised DB** | `connect_index()` opens the file but doesn't create schema; `SELECT FROM documents` raises an unhandled `sqlite3.OperationalError` if `db.py init` was never run. `embeddings.py:253-261`. | open |
| **`make spec SLUG=…` uses `sed -i ''` (BSD/macOS only) — fails on Linux** | GNU `sed` treats the empty-string argument as a filename; spec file placeholders are left unreplaced or the file is corrupted. `Makefile:31`. | open |
| **`embeddings.py savings` subcommand crashes with unrecognized argument** | `stats.main()` calls `ap.parse_args()` with no args, so it reads `sys.argv` and sees `'savings'` as an unrecognized positional — argparse errors and exits. `embeddings.py:441` + `stats.py:143`. | open |
| **`embeddings.py expected_source_paths()` uses `f.name` for root-glob files** | `out.add(f.name)` at line 328 stores only the filename, so `health()` falsely reports no gaps even when the data-loss collision from `enumerate_sources()` has overwritten `docs/adr/README.md` content. `embeddings.py:328`. | open |
| **`compact-trigger` compares transcript size in bytes against `MAX_SESSION_CHARS` (chars)** | `os.path.getsize()` returns bytes; `MAX_SESSION_CHARS` is documented and named as a character count; for transcripts with multi-byte UTF-8 content the nudge fires earlier than intended. `compact-trigger.py:62`. | open |

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
