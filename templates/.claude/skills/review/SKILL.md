---
name: review
description: Review changed code against .agents/ rules and produce a verdict. Use when the user asks for a code review, wants to check their changes before a PR, or runs /review. Triggers for "review", "review my changes", "review <file>", "/review", "check my code", or similar requests.
---

# /review workflow

## Rules
- Never modify files. This skill is read-only — it produces a report, nothing else.
- Always check security rules (.agents/security.md) regardless of file type.
- Base the verdict on blocking issues only. Advisory issues never block.
- A verdict of PASS with advisory issues is still a PASS.
- Do not invent rules not present in the .agents/ files.

## Verdicts
- **PASS** — no blocking issues found
- **NEEDS WORK** — one or more advisory issues, no blocking issues
- **BLOCK** — one or more blocking issues; must be resolved before merge

## Steps

### 0. Signal active skill
Write `review` to `.claude/state/active_skill`.

### 1. Determine scope

**If an argument was given** (e.g. `/review src/auth.py` or `/review the login changes`):
- Use the argument to identify the target. If it names a file or directory, read it directly.
- If it's a description, use `git diff` to find the relevant changed files.

**If no argument was given**:
- Run `git diff HEAD` to get all staged and unstaged changes.
- If the diff is empty, run `git diff HEAD~1` to review the last commit.
- Tell the user: "Reviewing: <N files changed>."

### 2. Map files to domains

For each changed file, determine which `.agents/` rule files apply:

| File pattern | Rules to load |
|---|---|
| `*.py`, `*.go`, `*.rb`, `*.java` | `backend.md`, `testing.md`, `security.md` |
| `*.ts`, `*.tsx`, `*.js`, `*.jsx` | `frontend.md`, `testing.md`, `security.md` |
| `test_*.py`, `*.test.ts`, `*.spec.ts` | `testing.md` |
| `*.md`, `*.json`, `*.yaml`, `*.toml` | `security.md` only |
| `.agents/*.md`, `.claude/settings.json` | Skip — meta-files, not subject to domain rules |

Always load `security.md`. Load the others only when the file pattern matches.

### 3. Read the rules
Read each applicable `.agents/` file. These are the only rules the review applies.

### 4. Review each changed file
For each changed file, check every rule in the applicable rule files:
- Is there a violation? Note: **file path**, **line number if identifiable**, **which rule was violated**, **severity** (blocking = rule says "never" / "always" / "required"; advisory = everything else).
- Ignore lines that were not changed (context lines). Only flag changes in the diff.

### 5. Produce the report

Output in this exact format:

```
## Review verdict: [PASS | NEEDS WORK | BLOCK]

### Blocking issues
<!-- If none: write "None." -->
- `<file>:<line>` — [<rule-file>] <description of violation>

### Advisory
<!-- If none: write "None." -->
- `<file>:<line>` — <description>

### Summary
<2–3 sentences: what was reviewed, what was found, what needs to happen before merge (if anything).>
```

### 6. Stop
Do not make changes. Do not open a PR. Do not ask follow-up questions unless the user asks for clarification on a specific issue.
