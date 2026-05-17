---
name: spec
description: Generate a PRD, task list, and draft implementation plan for a new feature. Use when starting any non-trivial work that touches more than one file or surface. Enters plan mode and requires explicit approval before writing anything to disk. Triggers for "spec for X", "write a spec", "plan feature X", "I want to build X", "spec out Y".
---

# /spec workflow

## Rules
- Never write files until ExitPlanMode is called. Plan mode is the gate.
- Never skip AskUserQuestion. The user must approve the plan before it is written.
- The spec slug must be unique. Check docs/specs/ for existing slugs before writing.
- Call `make spec SLUG=<slug>` after writing the spec to verify the file landed correctly.

## Steps

### 0. Signal active skill
Write `spec` to `.claude/state/active_skill` so the bash-logger hook can key commands to this skill.

### 1. Enter plan mode
Call EnterPlanMode immediately. Do not read files or write anything until you are in plan mode.

### 2. Gather context
Use the Explore subagent to map what already exists that this feature touches or depends on.
Ask: what files are relevant? What interfaces exist? What patterns does this codebase already use?

**If the developer needs to stop here:** write current context to `.claude/spec_queue.md` using the format below, then tell the dev: "Spec queued. Say 'continue spec for <slug>' when you're ready." Do not proceed.

### 2b. Tool identification
Ask the developer: "What external actions does this feature need? (e.g. API calls, subprocess calls, filesystem reads/writes, reads from external state)"

For each action identified:
1. Read `.claude/tool_registry.json` — check if a tool already covers this action. If yes, note it; do not scaffold a duplicate.
2. If no existing tool: record it in the plan as a tool stub to scaffold after ExitPlanMode.

Tool stubs will be created at `.claude/skills/<skill-name>/tools/<tool-name>.py` as typed Python with a real function signature and a `raise NotImplementedError` body.

**If the developer needs to stop here:** write current context (including tool stubs identified) to `.claude/spec_queue.md`, then tell the dev how to resume.

### 3. Draft the plan
Use the Plan subagent to produce an implementation strategy covering:
- What the feature does (one paragraph)
- Files to create or change, with one-line descriptions
- Tests to write
- What the PR will contain
- Open questions that must be answered before implementation starts

### 4. Confirm with the user
Call AskUserQuestion. Present:
- A 3-sentence summary of the proposed feature
- The file change list
- Any open questions
Do not proceed if the user has concerns or unanswered questions.

### 5. Exit plan mode
Call ExitPlanMode. This is the approval gate. Everything after this writes to disk.

### 6. Write the spec
Determine a kebab-case slug for the feature (e.g., `user-auth`, `csv-export`).
Write the spec to `docs/specs/<slug>.md` using this structure:

```
# Spec: <feature name>

**Slug:** <slug>
**Date:** <YYYY-MM-DD>
**Status:** Draft

## Problem
<What problem does this solve? One paragraph.>

## Proposed solution
<What will be built? One paragraph.>

## Scope

### In scope
- <item>

### Out of scope
- <item>

## Implementation plan
<Ordered list: file path — what changes and why>

## Tests
<List of tests to write, one per line>

## Open questions
<Remove this section when all questions are resolved.>
```

### 7. Scaffold tool stubs
For each tool stub identified in step 2b that does not exist yet:
- Run `make scaffold-tool SKILL=<skill-name> NAME=<tool-name>` to create the stub.
- Write a real typed function signature and a one-line docstring. Body: `raise NotImplementedError`.
- The Write hook will fire and instruct you to update `.claude/tool_registry.json` — do so immediately.

### 8. Confirm and report
Run `make spec SLUG=<slug>` to verify the file exists.
Tell the user: where the spec was written, what tool stubs were created (if any), and what the next step is (open a PR for the spec, then start implementation following the spec).

---

## Deferral and resume

### spec_queue.md format
When deferring, write to `.claude/spec_queue.md`:

```markdown
## In progress: <slug>

**Started:** <YYYY-MM-DD>
**Status:** interrupted

### Context gathered so far
<free-text summary of what was learned in step 2>

### Tool stubs identified
- <tool_name>(<args>) -> <return type>  # one line per tool

### Remaining gaps
- [ ] <unanswered question or section not yet drafted>

---
Resume: tell Claude "continue spec for <slug>" to pick up from here.
```

### On resume
Read `.claude/spec_queue.md`. Draft the spec with everything already known — fill in all sections Claude can complete from context. Then walk the developer through remaining gaps one at a time before writing the final spec to disk.
