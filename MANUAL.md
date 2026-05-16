# flying_buttress Manual

> *The operating reference. Everything you need to use the factory day to day.*

This manual covers the factory itself — how to scaffold projects, run workflows, write rules, manage permissions, and extend the tooling. It is the practical complement to [`buttress.md`](buttress.md) (the philosophy) and [`plan.md`](plan.md) (the Claude Code internals).

**New here?** Read [`ONBOARDING.md`](ONBOARDING.md) first. Come back when you have your first PR open.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Getting the factory](#2-getting-the-factory)
3. [Scaffolding a project](#3-scaffolding-a-project)
4. [The /spec workflow](#4-the-spec-workflow)
5. [The Makefile reference](#5-the-makefile-reference)
6. [The rules system](#6-the-rules-system)
7. [Permissions and settings](#7-permissions-and-settings)
8. [The ADR system](#8-the-adr-system)
9. [Team coordination](#9-team-coordination)
10. [The lifecycle in practice](#10-the-lifecycle-in-practice)
11. [Extending the factory](#11-extending-the-factory)
12. [Troubleshooting](#12-troubleshooting)
13. [Quick reference](#13-quick-reference)

---

## 1. Prerequisites

| Requirement | Minimum version | Check |
|---|---|---|
| Python | 3.9+ | `python3 --version` |
| Git | 2.30+ | `git --version` |
| Claude Code CLI | latest | `claude --version` |
| GNU Make | any | `make --version` |

**Claude Code CLI install:** `npm install -g @anthropic-ai/claude-code` or see [claude.ai/code](https://claude.ai/code).

No other dependencies are required to run the factory itself. Individual projects scaffolded from it may add their own.

---

## 2. Getting the factory

```bash
git clone https://github.com/hofmockel/flying_buttress.git
cd flying_buttress
make validate-hooks
```

`make validate-hooks` runs the tier-1 smoke checklist. Every line should print `[✓]`. If anything fails, the checklist output tells you what's missing.

**Optional: install `less_tokens`**

`less_tokens` is a token-reduction layer that installs on top of the factory (and any project it produces). It is maintained as a separate repo and is not required.

```bash
git clone https://github.com/hofmockel/less_tokens.git
python3 less_tokens/install.py
```

`less_tokens/` is gitignored. To upgrade, `cd less_tokens && git pull && python3 install.py`.

---

## 3. Scaffolding a project

The scaffold command copies the factory's `templates/` directory into a new sibling repository, substitutes project-specific values, and initializes git.

### Running the scaffolder

```bash
make scaffold TARGET=../my-project
```

Or directly:

```bash
python3 scripts/scaffold.py --target ../my-project
```

The scaffolder will prompt you for:

| Prompt | What it does | Example |
|---|---|---|
| **Project name** | Display name; appears in CLAUDE.md and file headers | `Acme API` |
| **Project slug** | Kebab-case identifier; auto-derived from name | `acme-api` |
| **Install less_tokens?** | Clones less_tokens into the new project | `y` / `N` |

To skip prompts (for scripted use):

```bash
python3 scripts/scaffold.py --target ../my-project --yes
```

### What gets created

After scaffolding, your new project contains:

```
my-project/
├── CLAUDE.md                   ← Claude Code entry point, pre-configured
├── ONBOARDING.md               ← team onboarding doc
├── Makefile                    ← quality gate stubs; fill in your test/lint/fmt commands
├── .gitignore                  ← ignores .env, sandbox/
├── .agents/
│   ├── backend.md              ← backend rules (edit for your stack)
│   ├── frontend.md             ← frontend rules
│   ├── testing.md              ← testing rules
│   └── security.md             ← security rules
├── .claude/
│   ├── settings.json           ← permissions baseline
│   └── skills/spec/SKILL.md   ← /spec skill
└── docs/
    └── specs/                  ← /spec output lands here
```

### Verifying the scaffold

```bash
cd ../my-project
make validate-hooks
```

All checks should be green. Then open Claude Code and confirm it orients correctly:

```bash
claude
```

Ask Claude: *"What is this project and how is it structured?"* — `CLAUDE.md` should route it to the right context.

### What the substitution markers do

The templates use `{{project_name}}`, `{{project_slug}}`, and `{{date}}`. These are replaced at scaffold time. After scaffolding, no markers remain — you own plain files with no template engine dependency.

---

## 4. The /spec workflow

`/spec` is the factory's primary workflow. It generates a PRD (Product Requirements Document) for a new feature using Claude's plan mode as the approval gate.

### When to use /spec

Use `/spec` for any work that:
- Touches more than one file
- Requires a design decision
- Could take more than a few hours to implement

For single-file edits or obvious bug fixes, skip the spec and go straight to implementation.

### Running /spec

Open Claude Code from your project root, then type:

```
/spec add user authentication with email and password
```

Or describe the feature conversationally — Claude's skill description matches a broad range of natural language triggers.

### What happens step by step

**Step 1 — Plan mode engages.** Claude enters read-only plan mode. Nothing is written to disk. You cannot accidentally trigger file changes during this phase.

**Step 2 — Context gathering.** An Explore subagent maps the relevant parts of your codebase: existing auth patterns, interfaces the feature will touch, naming conventions already in use.

**Step 3 — Plan drafting.** A Plan subagent drafts an implementation strategy covering the problem statement, files to change, tests to write, and open questions.

**Step 4 — Your approval.** Claude presents a summary and asks for your confirmation. This is the moment to redirect, push back, or ask follow-up questions. The plan does not proceed until you say yes.

**Step 5 — Plan mode exits.** `ExitPlanMode` is called. This is the gate. File writes begin only after this point.

**Step 6 — Spec is written.** Claude writes `docs/specs/<slug>.md` using a consistent template. The slug is derived from your feature name.

**Step 7 — Confirmation.** Claude runs `make spec SLUG=<slug>` to verify the file landed, then tells you what comes next.

### Reading the spec output

Every spec has the same structure:

```markdown
# Spec: User Authentication

**Slug:** user-auth
**Date:** 2026-05-15
**Status:** Draft

## Problem
...

## Proposed solution
...

## Scope
### In scope
- ...
### Out of scope
- ...

## Implementation plan
...

## Tests
...

## Open questions
...
```

**Status values:** `Draft` → `Approved` → `In progress` → `Done`. Update the status field manually as the feature moves through the lifecycle.

### After the spec

1. Open a PR with the spec file as the only change. This lets the team review the plan before any code is written.
2. Once the spec PR merges, start implementation against it.
3. Remove the "Open questions" section when all questions are resolved.
4. Update status to `Done` when the feature ships.

### Using /spec without Claude Code

```bash
make spec SLUG=user-auth
```

This creates a blank spec template at `docs/specs/user-auth.md` without the guided workflow. Fill it in manually.

---

## 5. The Makefile reference

The Makefile is the factory's durable substrate. Every skill that shells out to a project operation calls a Make target. This means workflows work without Claude Code — useful in CI and for developers who prefer the terminal.

### Targets

#### `make help`

Prints all available targets with descriptions.

#### `make spec [SLUG=<slug>]`

Without `SLUG`: prints a tip to run `/spec` in Claude Code.

With `SLUG=<name>`: creates `docs/specs/<name>.md` from the blank spec template. Useful when you want to write a spec manually.

```bash
make spec SLUG=billing-portal
# → Created: docs/specs/billing-portal.md
```

#### `make test`

Runs the project's test suite. Ships as a stub:

```makefile
test:
    @echo "No test suite configured yet. Add your test command here."
```

**Fill this in** with your actual test command once your stack is chosen:

```makefile
test:
    pytest tests/ -v
```

#### `make lint`

Runs the linter. Ships as a stub. Fill in with your linter:

```makefile
lint:
    ruff check .
```

#### `make fmt`

Runs the formatter. Ships as a stub. Fill in:

```makefile
fmt:
    ruff format .
```

#### `make validate-hooks`

Runs the tier-1 smoke checklist from [ADR-004](docs/adr/ADR-004-factory-test-strategy.md). Checks that all required files and directories exist and that `settings.json` is valid JSON.

```bash
make validate-hooks
# ==> Tier-1 smoke checklist
# [✓] settings.json valid JSON
# [✓] CLAUDE.md exists
# ...
```

Run this before opening any PR. Add it to your CI pipeline once GitHub Actions is configured.

#### `make scaffold TARGET=<path>`

Calls `scripts/scaffold.py` to stamp out a new sibling project. `TARGET` is required.

```bash
make scaffold TARGET=../new-project
```

### Adding targets to your project's Makefile

The Makefile in your scaffolded project is yours to extend. The only constraint (from [ADR-005](docs/adr/ADR-005-makefile-underlay.md)): if you write a Claude Code skill that shells out to a project operation, write the Make target first and have the skill call `make <target>`.

---

## 6. The rules system

The `.agents/` directory is the highest-leverage artifact in the factory. Rules files tell every Claude session what constraints apply in each domain — before any code is touched.

### The four rule files

| File | Domain | Key concerns |
|---|---|---|
| `.agents/backend.md` | Backend code | Boundaries, naming, error handling, structure |
| `.agents/frontend.md` | Frontend code | State, naming, DOM, accessibility |
| `.agents/testing.md` | Tests | What to test, what not to test, CI requirements |
| `.agents/security.md` | Security | Hard rules, PR checklist, dependency policy |

### How rules are applied

Claude Code reads `.agents/` files automatically at the start of each session. Rules apply to all agents — the main session, subagents, and any skill that spawns further agents. You do not need to paste them into prompts.

### Writing effective rules

Good rules are **short, specific, and have a why**:

```markdown
## Hard rule
No SQL string interpolation — always use parameterized queries.
Why: SQL injection is the most common backend vulnerability. Parameterized queries eliminate the entire class.
```

Bad rules are vague:

```markdown
## Best practice
Write secure code.
```

**Three-line limit:** if a rule requires more than three lines to state clearly, it is not a rule yet — it is a discussion. Have the discussion first, then write the rule.

### Updating rules

Rules files are committed to the repo and reviewed like code. To add or change a rule:

1. Edit the relevant `.agents/*.md` file.
2. Open a PR with the change and a one-line explanation.
3. For the factory repo: settings-adjacent rules (`.agents/security.md` changes with security implications) follow the same approval path as `settings.json` — see [ADR-006](docs/adr/ADR-006-settings-governance.md).

### Rules in scaffolded projects

The `.agents/*.md.tmpl` files in `templates/` ship with sensible defaults. Customize them immediately after scaffolding for your project's stack. The stubs include placeholders:

```markdown
---
_Extend these rules with project-specific conventions as the codebase grows._
```

Remove the placeholder line once you have real project-specific rules to add.

---

## 7. Permissions and settings

`settings.json` is the factory's policy-as-code file. It controls what Claude Code is allowed to do in a session without prompting the user.

### File locations and precedence

| File | Scope | Committed? | Who can change |
|---|---|---|---|
| `.claude/settings.json` | Project (all team members) | Yes | Senior approval required (ADR-006) |
| `~/.claude/settings.json` | User (all projects) | No | Anyone (personal preferences) |
| `.claude/settings.local.json` | Local (this machine only) | No — gitignored | Anyone (temporary overrides) |

Project settings override user settings for conflicting keys. Local settings override both.

### The permissions block

```json
{
  "permissions": {
    "allow": [
      "Bash(git status)",
      "Bash(make*)",
      "Read(**)"
    ],
    "deny": [
      "Bash(rm -rf*)",
      "Bash(git push --force*)",
      "Read(.env*)"
    ]
  }
}
```

**Allow rules** permit operations without prompting. Use them for common safe operations (reading files, running Make targets, git status).

**Deny rules** block operations outright — Claude cannot perform them even if asked. Use them for destructive operations (`rm -rf`), credential exposure (`Read(.env*)`), and irreversible git operations.

**Pattern syntax:** `*` matches any suffix. `Bash(make*)` allows all Make invocations. `Read(**)` allows reading any file.

### Using local overrides

`.claude/settings.local.json` is gitignored and never shared. Use it for temporary personal preferences — switching models, enabling a new tool for an experiment:

```json
{
  "env": {
    "CLAUDE_MODEL": "claude-opus-4-7"
  }
}
```

**Rule of thumb:** if you find yourself keeping a local override for more than a week, it belongs either in a PR to `settings.json` or in your personal `~/.claude/settings.json`.

### Changing project settings

Changes to `.claude/settings.json` require senior approval before merge — they affect every developer. See [ADR-006](docs/adr/ADR-006-settings-governance.md) for the full governance model.

When submitting a settings PR, answer these in the description:
- Is this the most targeted change possible?
- Does a new deny rule risk blocking legitimate operations?
- Does a new allow rule introduce a security surface?

---

## 8. The ADR system

Architecture Decision Records (ADRs) are how the factory documents decisions — what was decided, why, and what the consequences are. They live in `docs/adr/`.

### Reading an ADR

Each ADR has:

- **Status** — `Proposed`, `Accepted`, or `Superseded`
- **Context** — what situation prompted this decision
- **Options considered** — what was evaluated
- **Decision** — what was chosen
- **Consequences** — what follows, good and bad

The status is the first thing to check. `Proposed` means it has not been accepted yet — it is a proposal, not a rule. `Accepted` means the team has committed to executing against it.

### The ADR as the work queue

In v1, the ADR sequence is the team's work queue. The lowest-numbered `Proposed` ADR is the next thing to build. This is why [ONBOARDING.md](ONBOARDING.md) sends new contributors to `docs/adr/README.md` first.

### Advancing an ADR

An ADR advances from `Proposed` to `Accepted` at the weekly sync, after the senior has reviewed it. To advance:

1. Change `**Status:** Proposed` to `**Status:** Accepted` in the ADR file.
2. Update the status column in `docs/adr/README.md`.
3. Open a PR with only those two changes.

### Writing a new ADR

When a gap, decision, or architectural question needs a record:

1. Create `docs/adr/ADR-NNN-short-title.md` (next number in sequence).
2. Add a row to `docs/adr/README.md`.
3. Use this structure:

```markdown
# ADR-NNN: Title

**Status:** Proposed
**Date:** YYYY-MM-DD
**Deciders:** [role or name]

## Context
[Why does this need a decision?]

## Options considered
[What were the choices?]

## Decision
[What are we doing?]

## Consequences
[What follows — good and bad?]
```

Keep ADRs short. If the Context section is more than a paragraph, it probably needs to be split.

---

## 9. Team coordination

The coordination model is defined in [ADR-003](docs/adr/ADR-003-team-coordination.md). This section is the practical summary.

### PR process

- **All factory changes go through PRs** — no direct commits to `main`.
- **Self-merge after 48 hours** if there is no blocking comment from the senior.
- **Exception:** changes to `.claude/settings.json` or `.agents/security.md` require explicit senior approval before merge.

### Weekly sync

Every Monday (or nearest working day), 30 minutes:

1. Senior reads all PRs merged since last sync. *(5 min, async before the meeting.)*
2. Team discusses anything flagged. *(10 min.)*
3. Review `docs/adr/README.md` together — advance any ADRs ready to move from Proposed → Accepted. *(10 min.)*
4. Carry-back items: improvements observed in sibling projects this week. *(5 min.)*

### Carry-back loop

When you discover an improvement in a sibling project (a better rule, a more useful Makefile target, a skill bug) that benefits the factory itself:

1. Open a PR against flying_buttress — not the sibling project.
2. PR description must include: what changed, why it's an improvement, and **evidence it works** (transcript excerpt, output artifact, or screenshot).
3. "I tested it and it works" with no artifact is not acceptable.

### Ownership

| Artifact | Who can self-merge |
|---|---|
| `ONBOARDING.md`, `CLAUDE.md`, `backlog.md` | Any developer after 48h |
| Skills under `.claude/skills/` | Junior (assigned per ADR) after 48h |
| `docs/adr/` files | Whoever writes the ADR; senior approval to advance status to Accepted |
| `.agents/*.md` | Senior approval required |
| `.claude/settings.json` | Senior approval required |

### Memory

Memory files live at `~/.claude/projects/<repo>/memory/` — per-machine, not committed. They are not shared across developers. The only shared persistent state is what's in the repo.

Don't put decisions in memory that the team needs to share. Those go in ADRs or `backlog.md`.

---

## 10. The lifecycle in practice

### Sketch phase

**Goal:** produce a spec, not code. Nothing touches disk until plan mode is approved.

1. Open Claude Code: `claude`
2. Describe what you want to build: `/spec <feature description>`
3. Review the plan Claude drafts. Redirect if needed.
4. Approve the plan.
5. Commit `docs/specs/<slug>.md` in a PR.

**What makes a sketch phase complete:** the spec PR is merged and every open question is answered. Do not start implementation while questions remain.

### Prototype phase

**Goal:** running code as fast as possible. Compilable at all times; not production-ready.

- Use Claude Code's fast mode for tight iteration loops (`/fast`).
- PostToolUse hooks (added in v2) will run formatters and type-checkers on every save. Until then, run `make fmt && make lint` manually before committing.
- Every PR gets a preview deploy — even a rough prototype. Stakeholder feedback on a rough version is cheaper than on a finished one.

**What makes a prototype complete:** the feature works end-to-end in a development environment. Known rough edges are documented as issues, not TODO comments.

### Productionize phase

**Goal:** harden the prototype. Quality gates run on every PR. No merge unless all green.

The quality gate sequence (target state — CI wired in v2):

```
commit → lint → type-check → test → security scan → preview deploy → human approve → main
```

- Add your test command to `make test` before this phase begins.
- Add your lint command to `make lint`.
- Run `make validate-hooks` as part of your PR checklist.

**The exception path:** if a quality gate must be bypassed, open an ADR documenting what rule was broken, why, and when the debt will be repaid. No silent bypasses.

### Operate phase

**Goal:** keep it running and keep the knowledge current.

- Write a runbook stub for every feature that can page someone. File it alongside the feature code.
- Update `.agents/*.md` when you discover a new constraint the codebase consistently needs.
- Run `anthropic-skills:consolidate-memory` weekly to keep Claude's memory of the project accurate.
- Session transcripts are searchable (`mcp__ccd_session_mgmt__search_session_transcripts`). ADRs should cite the session in which a decision was made.
- Use `review_plan.md` as the review reference — it defines the ten review kinds and five mechanisms. Run the relevant review kind for each PR type.

---

## 11. Extending the factory

### Adding a skill

Skills are Claude Code slash commands defined in `.claude/skills/<name>/SKILL.md`. To add one:

1. Create `.claude/skills/<name>/SKILL.md`.
2. Write a frontmatter `name` and `description` field — the description controls when the skill triggers.
3. Write the numbered steps the skill follows.
4. If the skill shells out to a project operation, write the Make target first and call `make <target>` from the skill.
5. Test it: open Claude Code, type `/<name>`, and confirm the behavior.
6. Carry it back to flying_buttress if it's general enough to benefit every project.

Minimal SKILL.md structure:

```markdown
---
name: my-skill
description: When to trigger this skill. Be specific — Claude uses this to decide whether to invoke it.
---

# /my-skill workflow

## Steps

### 1. ...
### 2. ...
```

### Adding a Makefile target

```makefile
.PHONY: my-target

my-target:
    @echo "What this does"
    your-command-here
```

Add it to the `help` target output so it shows in `make help`.

### Adding rules

Edit `.agents/<domain>.md`. Rules are short, specific, and have a why. PR required — see [§6](#6-the-rules-system).

### Hooks (v2)

Hooks are shell commands triggered by Claude Code events (PreToolUse, PostToolUse, UserPromptSubmit, Stop). They are the load-bearing safety mechanism for v2 and are not yet configured in v1.

When hooks are added, they will live in `.claude/settings.json` under a `"hooks"` key. See `plan.md` §6.1 for the full model.

### Custom subagents (v2)

Custom subagents are defined in the Agent SDK and extend the built-in Explore/Plan/code-reviewer set. Planned for v2. See `plan.md` §5.3 for the design.

---

## 12. Troubleshooting

### `make validate-hooks` shows a red check

The output names the missing file or directory. Create it or run the scaffold that should have created it.

### Claude doesn't know about my `.agents/` rules

Confirm `CLAUDE.md` exists at the repo root and contains a pointer to `.agents/`. Claude Code reads `CLAUDE.md` at session start — if the pointer is missing, the rules are invisible.

```bash
grep -i ".agents" CLAUDE.md
```

### `/spec` starts writing files immediately without asking

The skill definition may not have `EnterPlanMode` as step 1. Check `.claude/skills/spec/SKILL.md` — the first step must call `EnterPlanMode` before any file operations.

### `make scaffold` fails with `TARGET is required`

You must pass the target path:

```bash
make scaffold TARGET=../my-project   # correct
make scaffold                         # fails
```

### Claude Code can't find a skill

Skills are matched by the `description` field in the SKILL.md frontmatter. If `/myskill` isn't triggering, check that:
1. The file exists at `.claude/skills/myskill/SKILL.md`.
2. The `name` field matches the command name exactly.
3. The `description` field is specific enough to match your trigger phrase.

### `settings.json` changes aren't taking effect

Claude Code reads `settings.json` at session start. Restart the Claude session after changing permissions.

### A permission prompt keeps appearing for a safe operation

Add it to the `allow` list in `.claude/settings.json`. Follow the governance process in [ADR-006](docs/adr/ADR-006-settings-governance.md) — this is a settings change requiring senior approval.

Alternatively, the `fewer-permission-prompts` skill can audit recent session transcripts and suggest allow-list additions automatically.

---

## 13. Quick reference

### Commands

| Command | What it does |
|---|---|
| `make validate-hooks` | Run smoke checklist — do this before every PR |
| `make scaffold TARGET=<path>` | Stamp out a new sibling project |
| `make spec SLUG=<slug>` | Create a blank spec at `docs/specs/<slug>.md` |
| `make test` | Run the test suite (fill in your command) |
| `make lint` | Run the linter (fill in your command) |
| `make fmt` | Run the formatter (fill in your command) |
| `make help` | List all available Make targets |

### Skills

| Skill | Trigger | What it does |
|---|---|---|
| `/spec` | "spec for X", "plan feature X", "I want to build X" | Guided PRD generation with plan mode gate |

### Key files

| File | Purpose |
|---|---|
| `CLAUDE.md` | Claude Code entry point — router to everything else |
| `ONBOARDING.md` | New contributor path |
| `MANUAL.md` | This document |
| `buttress.md` | Philosophy and methodology |
| `plan.md` | Claude Code operating manual |
| `backlog.md` | Open gaps tied to ADRs |
| `review_plan.md` | Ten review kinds and five execution mechanisms |
| `docs/adr/README.md` | ADR index and work queue |
| `.agents/*.md` | Domain rules |
| `.claude/settings.json` | Permissions policy |
| `.claude/skills/spec/SKILL.md` | /spec skill definition |
| `templates/` | Files stamped into new projects |
| `scripts/scaffold.py` | Project scaffolder |
| `Makefile` | Durable workflow substrate |

### Lifecycle cheatsheet

| Phase | Start condition | End condition | Primary tool |
|---|---|---|---|
| **Sketch** | Feature idea | Spec PR merged, no open questions | `/spec` |
| **Prototype** | Spec approved | Feature works end-to-end in dev | Fast mode + Edit |
| **Productionize** | Prototype complete | All quality gates green, PR merged | `/fix`, `/review` |
| **Operate** | Feature in production | Runbook exists, ADR updated | `/runbook`, `/adr` |

### ADR status meanings

| Status | Meaning |
|---|---|
| `Proposed` | Drafted; not yet accepted; may change |
| `Accepted` | Team has committed; execute against it |
| `Superseded` | Replaced by a later ADR; see link |
