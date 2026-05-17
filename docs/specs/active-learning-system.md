# Spec: Active Learning System

**Slug:** active-learning-system
**Date:** 2026-05-16
**Status:** Draft

## Problem

Developers using flying_buttress repeatedly reach for the same Bash patterns, leave spec work half-done when interrupted, and build tool stubs inside skills without any way to discover what already exists elsewhere. The factory watches none of this. Every session starts cold, recurring work never gets codified, and the same tools get re-invented across skills. The gap is that the factory has no feedback loop from developer behavior back into its own structure.

## Proposed solution

Three interlocking mechanisms close the loop. A bash-logger hook captures every command Claude runs, keyed to the active skill; a stop hook analyzes those patterns after each turn and queues promotion suggestions to `.claude/promote_queue.md` when a command skeleton recurs enough times. The `/spec` skill gains a tool-identification phase that asks what external actions a feature needs before writing prose, defers in-progress work to `.claude/spec_queue.md` when the developer needs to context-switch, and resumes by drafting what it knows then walking gaps section by section. A tool-registry hook detects when a new tool stub is written inside a skill subdirectory and instructs Claude to index it in a global `.claude/tool_registry.json` that Claude consults on demand to avoid re-implementation.

## Scope

### In scope
- `bash-logger.py` hook (PostToolUse on Bash): logs command, skeleton, timestamp, active skill to `.claude/state/bash-log.jsonl`
- `pattern-analyzer.py` hook (Stop event): detects repeated skeletons, appends entries to `.claude/promote_queue.md`; marks ambiguous patterns `needs-confirmation`; threshold configurable via `tools/search_config.py`
- `tool-registry.py` hook (PostToolUse on Write): detects writes to `.claude/skills/*/tools/*.py`, exits 2 with registry update instruction
- `.claude/state/active_skill` — written by each skill at start; read by bash-logger
- `.claude/promote_queue.md` — persists until dismissed or accepted; Claude handles status updates
- `.claude/spec_queue.md` — written by Claude on deferral; structured with context, tool stubs identified, remaining gaps
- `.claude/tool_registry.json` — global registry; Claude maintains; schema: `{name, description, skill, file_path, function_signature, date_added}`
- `/spec` SKILL.md update: Step 1 writes active_skill; new Step 2b identifies external actions and checks registry; deferral/resume flow
- Makefile targets: `promote-queue`, `tool-registry`, `scaffold-tool`, `install-hooks`; extend `validate-hooks`
- Tests in `less_tokens/tests/unit/test_active_learning_hooks.py`
- Settings PR (separate, senior-gated per ADR-006): three hook registrations in `.claude/settings.json`

### Out of scope
- Tools outside skill subdirectories (global tools are a separate concern)
- Automatic tool implementation (promotion suggests; dev or Claude implements)
- Cross-repo registry federation
- bash-log rotation policy (noted as future concern in hook docstring)

## Implementation plan

1. `tools/search_config.py` — add `BASH_PROMOTE_THRESHOLD: int = 5`
2. `.claude/hooks/bash-logger.py` + `less_tokens/hooks/bash-logger.py` — PostToolUse on Bash; `shlex.split` skeleton extraction (keep base command + flag tokens, strip positional args and quoted values); interpreter-only skeletons flagged `needs-confirmation`; reads `.claude/state/active_skill`; appends to `.claude/state/bash-log.jsonl`; exits 0 always
3. `.claude/hooks/pattern-analyzer.py` + `less_tokens/hooks/pattern-analyzer.py` — Stop hook; reads bash-log; groups by `(skeleton, active_skill)`; imports `BASH_PROMOTE_THRESHOLD` with fallback 5; appends to `.claude/promote_queue.md` (JSONL in fenced block); skips existing non-dismissed entries; exits 0 always
4. `.claude/hooks/tool-registry.py` + `less_tokens/hooks/tool-registry.py` — PostToolUse on Write; glob match `.claude/skills/*/tools/*.py`; exits 2 with registry instruction; exits 0 otherwise
5. `.claude/tool_registry.json` — initialize as `[]`
6. `.claude/skills/spec/SKILL.md` — Step 1: write `spec` to `.claude/state/active_skill`; Step 2b: tool identification (ask for external actions, check registry, record stubs needed); deferral: write `.claude/spec_queue.md` and instruct dev to say "continue spec for \<slug\>"; resume: draft known content, walk remaining gaps
7. `Makefile` — add `promote-queue` (display queue with pending count), `tool-registry` (display registry), `scaffold-tool SKILL= NAME=` (stamp typed Python stub into `.claude/skills/<skill>/tools/<name>.py`), `install-hooks` (copy from `less_tokens/hooks/` to `.claude/hooks/`); extend `validate-hooks` with registry JSON validity, bash-log JSONL validity, promote_queue existence checks
8. `less_tokens/tests/unit/test_active_learning_hooks.py` — three test classes (see Tests section)
9. **Settings PR** (separate, senior-gated): `.claude/settings.json` — PostToolUse on `Bash` → bash-logger; PostToolUse on `Write` → tool-registry; Stop → pattern-analyzer

## Tests

**`TestBashLogger`**
- Logs command and skeleton correctly to bash-log.jsonl
- Skeleton strips path arguments: `grep -r "foo" src/bar.py` → `grep -r`
- Skeleton strips quoted strings: `git commit -m "fix thing"` → `git commit -m`
- Skeleton strips positional args: `make spec SLUG=foo` → `make spec`
- Reads active_skill from state file correctly
- Missing active_skill file defaults to empty string, exits 0
- Malformed JSON stdin exits 0
- Empty command string exits 0

**`TestPatternAnalyzer`**
- Below threshold (4 records) produces no queue entry
- Threshold hit (5), unambiguous single skill → `pending` entry appended
- Threshold hit, multiple skills claim skeleton → `needs-confirmation` entry
- Interpreter-only skeleton (`python3` with no flags) → `needs-confirmation` regardless of count
- Existing `pending` entry not duplicated
- Existing `accepted` entry not duplicated
- `dismissed` entry allows new `pending` to be appended
- Corrupt JSONL line skipped gracefully; valid lines still processed
- Always exits 0

**`TestToolRegistry`**
- Write to `.claude/skills/spec/tools/fetch_api.py` → exits 2 with registry instruction in stderr
- Write to `.claude/skills/my-skill/tools/call_db.py` → exits 2
- Write to `.claude/hooks/foo.py` → exits 0
- Write tool_name is `Edit` → exits 0
- Missing `file_path` in payload → exits 0
- Malformed JSON stdin → exits 0

## Open questions

**Stop hook payload schema** — verify that `transcript_path` is present and `tool_name` is absent in Stop event payloads before finalizing `pattern-analyzer.py`. Test with a minimal stub first. Do not depend on `tool_name` in the Stop handler.
