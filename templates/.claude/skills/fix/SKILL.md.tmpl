---
name: fix
description: Fix a bug atomically using a TDD loop. Reproduces the bug, writes a failing test, applies the minimal fix, runs make test, and commits. Use when the user asks to fix a specific bug, work through the backlog, or run /fix. Triggers for "fix this bug", "fix <description>", "/fix", "next bug in backlog", or similar requests.
---

# /fix workflow

## Rules
- Never write the fix before writing a failing test. Red before green — always.
- Never change the test to make it pass. If the fix is hard, keep working on the fix.
- Never refactor or clean up beyond what is needed to fix the bug. Scope is the bug, nothing else.
- Never commit test and fix separately. One atomic commit contains both.

## Steps

### 0. Signal active skill
Write `fix` to `.claude/state/active_skill` so the bash-logger hook can key commands to this skill.

### 1. Identify the bug

**If an argument was given** (e.g. `/fix the login function returns None when username is empty`):
- Use the argument as the bug description. Proceed to Step 2.

**If no argument was given**:
- Read `backlog.md`. Find the lowest-numbered entry that is still open (no "Closed" or "Fixed" status).
- Confirm with the user: "Working on: [bug title]. Proceed?" Stop if they redirect.

### 2. Explore
Use the Explore subagent to map the code relevant to the bug:
- Which files and functions are involved?
- What is the expected vs. actual behavior?
- Where is the best place to add a test?

Report findings in one short paragraph before writing anything.

### 3. Write a failing test
Write a test that:
- Describes the bug in its name (e.g. `test_login_returns_none_when_username_empty`)
- Asserts the correct behavior (what *should* happen, not what currently happens)
- Is as small and focused as possible

Run `make test`. **Confirm the new test fails.** If it passes without any fix, the test is wrong — stop and diagnose.

### 4. Apply the minimal fix
Change only what is needed to make the failing test pass. Do not:
- Refactor surrounding code
- Fix adjacent issues
- Add features or guards beyond what the test requires

### 5. Run `make test` — confirm green
Run `make test`. All tests must pass, including the new one. If any test fails:
- If the new test fails: the fix is incomplete. Iterate on the fix only.
- If an existing test fails: the fix introduced a regression. Revise the fix.

Do not proceed to commit until `make test` is fully green.

### 6. Commit
Create a single commit containing the test and the fix. The commit message must:
- Describe the bug that was fixed (not the code change)
- Be written in past tense: "Fix login returning None when username is empty"

```bash
git add <test file> <fixed file(s)>
git commit -m "<fix description>"
```

### 7. Update backlog (if applicable)
If the bug came from `backlog.md`, mark its status as closed with today's date:

```
**Status:** Closed — fixed <YYYY-MM-DD>. Test: `<test_function_name>`.
```
