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

### 1. Enter plan mode
Call EnterPlanMode immediately. Do not read files or write anything until you are in plan mode.

### 2. Gather context
Use the Explore subagent to map what already exists that this feature touches or depends on.
Ask: what files are relevant? What interfaces exist? What patterns does this codebase already use?

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

### 7. Confirm and report
Run `make spec SLUG=<slug>` to verify the file exists.
Tell the user: where the spec was written, what the next step is (open a PR for the spec, then start implementation following the spec).
