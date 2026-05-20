# backlog.md

> Open gaps, concerns, and carry-back items for the factory. All closed items are recorded in CHANGELOG.md.

---

## Bugs

| Bug | Description | Status |
|-----|-------------|--------|
| **update_docs_on_commit opens CHANGELOG.md relative to CWD** | `Path("CHANGELOG.md")` resolves against the process CWD, not the repo root; hook silently no-ops when invoked from any directory other than the repo root. `update_docs_on_commit.py:45`. | open |
| **update_docs_on_commit only checks the first `cd` in a chained command** | `re.search` finds the first `cd` match; in a multi-`cd` chain the last destination (the actual commit location) is ignored, causing the hook to exit early when the factory root is the true target. `update_docs_on_commit.py:29`. | open |
| **pattern-analyzer _append_entry inserts into the last fence, not the jsonlines fence** | `text.rfind(_FENCE_CLOSE)` finds the last ` ``` ` in the file; any markdown block after the jsonlines block causes new entries to land in the wrong fence, corrupting both blocks. `pattern-analyzer.py:78`. | open |
| **pattern-analyzer _load_existing_skeletons toggles on any fence marker** | `if stripped.startswith("```"): in_block = not in_block` triggers on every fence opener/closer regardless of language; JSON objects in other fenced blocks are falsely counted as already-queued skeletons. `pattern-analyzer.py:59`. | open |
| **compact-trigger `last` state never resets between sessions** | After a large session fires the nudge (e.g. 2 MB), a subsequent smaller-but-over-threshold session (e.g. 600 KB) is silently skipped because `size < last + hysteresis`. State file is never cleared on new/smaller sessions. `compact-trigger.py:71`. | open |
| **embeddings.py stores `f.name` instead of relative path for root-glob files** | `out.append((st, f.name, k, t))` uses just the filename; `README.md` and `docs/adr/README.md` both get `source_path="README.md"`, so the second upsert silently overwrites the first in the DB. `embeddings.py:191`. | open |
| **embeddings.py refresh() crashes with unhandled OperationalError on uninitialised DB** | `connect_index()` opens the file but doesn't create schema; `SELECT FROM documents` raises an unhandled `sqlite3.OperationalError` if `db.py init` was never run. `embeddings.py:253-261`. | open |
| **`make spec SLUG=…` uses `sed -i ''` (BSD/macOS only) — fails on Linux** | GNU `sed` treats the empty-string argument as a filename; spec file placeholders are left unreplaced or the file is corrupted. `Makefile:31`. | open |
| **truncate-output `omitted_chars` understated by marker string length** | `omitted_chars = len(tool_result) - len(truncated)` subtracts the marker text itself (~31 chars) from the count; savings log and user-facing message both report the wrong number. `truncate-output.py:102`. | open |
| **`embeddings.py savings` subcommand crashes with unrecognized argument** | `stats.main()` calls `ap.parse_args()` with no args, so it reads `sys.argv` and sees `'savings'` as an unrecognized positional — argparse errors and exits. `embeddings.py:441` + `stats.py:143`. | open |
| **bash-logger drops subcommand after boolean long flags** | Flag-value drop logic fires unconditionally on any non-flag next token; `git --no-pager log` produces skeleton `git --no-pager`, silently losing the `log` subcommand. `bash-logger.py:69-75`. | open |
| **tool-registry only watches `Write`, ignores `Edit`** | `payload.get("tool_name") != "Write"` gates the hook; edits to existing skill tool stubs via `Edit` never trigger the registry-update reminder. `tool-registry.py:26`. | open |
| **update_docs_on_commit accumulates blank lines between CHANGELOG entries** | `lines.insert(insert_at, "")` unconditionally inserts a blank before every existing entry on each commit; after N commits there are N−1 blank lines between bullets. `update_docs_on_commit.py:66-67`. | open |
| **index-refresh `is_indexed()` returns False for root-level `.py` files** | Root files with no `/` in their relative path only pass if they end in `.md`; root `*.py` files are indexed by `embeddings.py` but edits to them never trigger a re-embed. `index-refresh.py:39-40`. | open |
| **`mcp_check.py` regex `^curls?$` matches non-existent command `curls`** | `r"^curls?$"` is present in both factory and template hooks; the `s?` makes `curls` a valid match and fires a spurious MCP advisory for a command that doesn't exist. `mcp_check.py:27`. | open |
| **`update_docs_on_commit` cd-regex misses `\n` as command separator** | `re.search(r"(?:^|&&|;)\s*cd\s+...")` has no `\n` in the separator alternation; a `cd /other\ngit commit` chain bypasses the sibling-repo guard and writes CHANGELOG from the wrong repo. `update_docs_on_commit.py:29`. | open |
| **`embeddings.py expected_source_paths()` uses `f.name` for root-glob files** | `out.add(f.name)` at line 328 stores only the filename, so `health()` falsely reports no gaps even when the data-loss collision from `enumerate_sources()` has overwritten `docs/adr/README.md` content. `embeddings.py:328`. | open |
| **`compact-trigger` compares transcript size in bytes against `MAX_SESSION_CHARS` (chars)** | `os.path.getsize()` returns bytes; `MAX_SESSION_CHARS` is documented and named as a character count; for transcripts with multi-byte UTF-8 content the nudge fires earlier than intended. `compact-trigger.py:62`. | open |
| **`search.py` savings log mixes `st_size` (bytes) with `len(text)` (chars)** | `full_file_chars += Path(fp).stat().st_size` counts bytes; `chunk_chars` counts characters; the subtraction overstates `saved_chars` for any file with non-ASCII content. `search.py:99-100`. | open |
| **`search-first.py` docstring claims `WINDOW_SECONDS` is configurable in `search_config.py` — it isn't** | `WINDOW_SECONDS = 300` is hardcoded at line 18; the constant doesn't exist in `search_config.py`; docstring on line 5 says "configure in search_config.py" which is false. `search-first.py:5,18`. | open |
| **`search-first.py` logs `st_size` (bytes) as `saved_chars` in savings log** | `file_chars = p.stat().st_size` returns bytes, not chars; logged as `saved_chars` under the `search-blocked` strategy — same class as Bug #22. `search-first.py:104,108`. | open |
| **`scaffold.py` `init_git()` returns `False` for both "already exists" and git failure** | `return False` when `.git` exists and `return result.returncode == 0` (also False on failure) are indistinguishable to the caller; a missing `git` binary or permission error silently prints "git repo already exists — skipped init". `scaffold.py:97-106,230`. | open |
| **`update_docs_on_commit` reads/writes CHANGELOG without `encoding="utf-8"`** | `changelog.read_text()` and `changelog.write_text()` use platform-default encoding; on Windows with non-ASCII commit messages (e.g. `✓`) this raises `UnicodeDecodeError` or silently corrupts the file. `update_docs_on_commit.py:49,72`. | open |
| **`bash-logger` log write lacks `encoding="utf-8"`** | `log.open("a")` uses platform-default encoding; on non-UTF-8 systems a non-ASCII command or active_skill value raises `UnicodeEncodeError` and the event is dropped. `bash-logger.py:115`. | open |
| **`bash-logger` active_skill read lacks `encoding="utf-8"`** | `active_skill_file.read_text()` uses platform-default encoding; a non-UTF-8 active_skill file raises `UnicodeDecodeError` and kills the log write for that event. `bash-logger.py:102`. | open |
| **`pattern-analyzer` queue file read/write lacks `encoding="utf-8"`** | `queue_file.read_text()` and `queue_file.write_text()` at lines 57, 75, 77, 83 use platform-default encoding; non-ASCII skeleton names or tool values corrupt the queue or raise on non-UTF-8 systems. `pattern-analyzer.py:57,75,77,83`. | open |
| **`pattern-analyzer` bash-log read lacks `encoding="utf-8"`** | `log.read_text().splitlines()` at line 97 uses platform-default encoding; a single non-ASCII entry in bash-log.jsonl raises `UnicodeDecodeError` and halts the entire analysis pass. `pattern-analyzer.py:97`. | open |

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
