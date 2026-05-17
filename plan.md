# plan.md

> *The operating manual for the factory floor.*

This document maps every part of the **flying_buttress** factory onto Claude Code's native features. Where `buttress.md` is the manifesto — opinionated on roles, agnostic on tools — this is the green-field operating manual that assumes Claude Code is the substrate and asks: *what does each part of the factory look like in Claude Code terms?*

For the review process specifically — review kinds, mechanisms, GitHub Actions, lifecycle alignment — see `review_plan.md`.

---

## 1. What this document is

### 1.1 Relationship to `buttress.md`

`buttress.md` is the **manifesto**: the public-facing definition of what flying_buttress is, the nine pillars, the six architectural roles, the four lifecycle phases. It is tool-agnostic at every layer.

`plan.md` is the **operating manual**: how the factory actually runs. It is opinionated about Claude Code, and only about Claude Code.

The two are companions. `buttress.md` says *what we are*. `plan.md` says *how we work*.

### 1.2 The paradox: agnostic AND all-in

"Tool-agnostic" applies to **what is built** — the Foundation, the Application surfaces, the Agent layer, the deploy target. Those choices are deferred to fork time.

"All-in on Claude Code" applies to **how we build it** — the editor, the workflow engine, the rule system, the audit trail. The factory floor itself is not pluggable. Claude Code is the substrate.

If a workflow can be expressed in a Claude Code skill, it should be. If a safety check can be expressed as a hook, it should be. If a rule can be written to a context file, it should be. The bar: *the factory ships with its rails.*

### 1.3 Audience and reading order

**New to this repo?** Start with [ONBOARDING.md](ONBOARDING.md) — five ordered steps from "I just cloned this" to "I have a PR open." Come back to this document after Step 1.

Three audiences for this document specifically:

- **Solo builder running the factory** — read in order; §4–§7 are load-bearing; §14 tracks delivery status (done / v2 / speculative).
- **Collaborator inheriting it** — start with §3 (pillars overview) and §9 (lifecycle table), then §14 (what's shipped, what's queued).
- **Template-cloner forking it** — start with §1–§3, then jump to §14 to understand what comes with the box and what's still queued.

---

## 2. In scope / out of scope

**In scope.** Claude Code as four things: the build environment, the workflow engine, the guardrails system, the governance layer. Plus MCP as the integration substrate. Plus the lifecycle mapping.

**Out of scope.** Foundation / Application / Agent-layer tool picks (deferred to fork time; see `buttress.md` §3). How built applications run in production (see `buttress.md` §5.4). Specific framework opinions for the apps under `/apps/`.

**Deferred.** Authoring custom MCP servers. Publishing skills and subagents to the wider community via the Agent SDK. Multi-repo orchestration. Memory consolidation tooling beyond what ships with Claude Code today.

---

## 3. The four pillars (overview)

The factory rests on four Claude-Code-native pillars. Each gets a deep dive in §4–§7.

- **Build environment** (§4) — the surfaces and primitives Claude Code provides. CLI, Desktop, Web, IDE; the irreducible tool verbs (Read, Edit, Bash, etc.); the execution modes (plan, fast, background, worktree); the model rubric; the discipline of context.
- **Workflow** (§5) — the named procedures we encode atop the primitives. Skills are the center of gravity. Subagents are division of labor. Loops and schedules are recurrence. Chapters and TodoWrite keep sessions legible.
- **Guardrails** (§6) — the automated rails that turn intent into safety. Hooks are the primary mechanism. Permissions cascade. Plan mode gates approval. Worktrees and subagent isolation protect blast radius.
- **Governance** (§7) — the rules and learning layer that compounds across sessions. Context files cascade. Memory persists. Skills encode procedure. Transcripts are the audit trail. `settings.json` is policy-as-code.

MCP (§8) is the nervous system that connects the factory to the outside world. The lifecycle (§9) is how all of this sequences from sketch to operate. §10 describes how the factory is developed and tested without contaminating its own repo.

---

## 4. Pillar I — Build environment

### 4.1 Surfaces

Four surfaces, ranked by role:

- **CLI** — the substrate. Every workflow must run here. Skills, hooks, and subagents are CLI-native. No factory feature depends on a graphical surface.
- **Desktop app** — the daily driver. Better ergonomics for long sessions, richer transcript view, easier chapter navigation. Preferred for sketch and operate phases.
- **Web (claude.ai/code)** — portable. The fallback when away from your machine; works without local install. Suitable for review, not for primary build.
- **IDE extensions** (VS Code, JetBrains) — opportunistic. Useful when the work is heavily inside a single file. Not the primary surface.

The factory is configured so that **all features work from the CLI**, with the others as conveniences.

### 4.2 Tool primitives

The irreducible verbs the factory composes:

- **Read / Write / Edit / NotebookEdit** — atomic file ops. The verbs of all coding workflows.
- **Bash** — universal executor. The spine of test running, git ops, deploys, anything shell-shaped.
- **WebFetch / WebSearch** — research during `/spec`; dependency CVE lookup during `/security-review`; documentation reads when context is missing.
- **Multimodal inputs** (images, PDFs, screenshots, Jupyter notebooks) — sketch-phase artifacts (mocks, whiteboards), bug-report attachments, design specs.

These verbs do not appear directly in workflows; they appear inside skills, subagents, and hooks. The factory wraps them.

### 4.3 Execution modes

Four modes, each with a clear "when to choose":

- **Plan mode** — read-only design phase with explicit `ExitPlanMode` approval gate. Default for `/spec` and `/refactor`; mandatory for any change touching more than ~3 files.
- **Fast mode** (`/fast`) — Opus 4.6 with faster output. Default during prototype-phase iteration, where wall-clock latency dominates.
- **Background execution** (`run_in_background`) — long-running tests, dev servers, watch processes. The factory's default for anything that runs longer than the conversation.
- **Worktree isolation** — agents working in isolated git copies. Default for risky refactors, security review on real diffs, parallel experiments that should not contaminate `main`.

### 4.4 Model selection rubric

| Model | Use for |
|---|---|
| Opus 4.7 (`claude-opus-4-7`) | Architecture, novel design, plan mode on hard problems, long-context refactors |
| Sonnet 4.6 (`claude-sonnet-4-6`) | Default for implementation, code review, most session work |
| Haiku 4.5 (`claude-haiku-4-5-20251001`) | Simple edits, formatting passes, repeated tooling tasks, low-stakes loops |

Default in `settings.json` is the most cost-effective model that meets the bar for the phase. Override per session if the work demands more.

**Review cadence:** Check this table quarterly against Anthropic's release notes. Model capabilities and pricing change faster than documents do; a stale rubric produces bad cost/quality decisions.

### 4.5 Context discipline

Long-context windows are not free. The factory enforces three habits:

- **Cache-warm windows.** Avoid sleeps and pauses past the 5-minute cache TTL. When polling, stay under 270s or commit to 20+ minutes.
- **Subagents protect main context.** Large tool results (codebase searches, security scans, transcript dumps) go to subagents whose summaries return to the main session.
- **Chapters mark phase shifts.** Long sessions get explicit chapter markers so transcripts stay navigable.

---

## 5. Pillar II — Workflow

### 5.1 Skills as the workflow primitive

The factory's workflows live as **Claude Code skills** under `.claude/skills/<name>/SKILL.md`. Skills are user-invokable slash commands with structured prompts and well-named triggers. They are the agentic surface; the `Makefile` at the repo root is the durable underlay (see [ADR-005](docs/adr/ADR-005-makefile-underlay.md) and `make help`).

**The constraint (ADR-005):** if a skill invokes a shell operation for a project workflow, it must delegate to a Make target — not the raw command. Run `make <target>` from the skill. This way, if Claude Code is unavailable, a developer can reach the same operation through Make directly. Skills that do purely agentic work (Explore, Plan, AskUserQuestion) are exempt — they have no shell equivalent.

Why skills, not Make targets, as the center of gravity here: skills carry their own context (when to trigger, what to do, what to expect), can compose subagents, and respect the permission and hook systems automatically. Make targets do not.

A minimal SKILL.md:

```markdown
---
name: spec
description: Generate a PRD, task list, and draft PR for a new feature. Use when starting any non-trivial work that touches more than one file or surface. Drops into Plan mode to confirm scope before writing code.
---

# Spec workflow
1. Enter plan mode.
2. Use Explore to map the relevant code.
3. Use Plan to draft the implementation strategy.
4. Confirm with the user via AskUserQuestion.
5. ExitPlanMode for approval.
6. Write the spec to docs/specs/<slug>.md.
```

### 5.2 The three load-bearing skills

- **`/spec`** — generate the PRD, task list, draft tests, and draft PR for a new feature. Enters plan mode, uses Explore + Plan subagents, requires user approval before producing artifacts.
- **`/fix`** — atomic TDD bug fix. Reproduces, writes a failing test, applies the minimal patch, opens a PR. Composes the bundled `bugfix` skill.
- **`/refactor`** — maps dependencies, proposes a design, migrates incrementally. Plan-mode-first; never lands in a single commit.

These three are the user-facing API of the factory. Everything else is plumbing.

### 5.3 Subagents as division of labor

Built-in subagents the factory uses:

- **Explore** — file pattern search, symbol lookup, "where is X defined." Cheapest research substrate.
- **Plan** — implementation design and trade-off analysis. Used inside `/spec` and `/refactor`.
- **code-reviewer** — second-opinion reviews of PRs.
- **general-purpose** — open-ended multi-step research when no specialist fits.
- **claude-code-guide** — questions about Claude Code features themselves.

Custom subagents the factory could author (see §14.5):

- **schema-checker** — validates changed schemas against committed contracts
- **doc-keeper** — checks that runbooks and changelogs were updated alongside features
- **security-reviewer-deep** — slow, thorough security review in an isolated worktree
- **transcript-archivist** — periodic archival and indexing of session transcripts

Rule: **subagents do work that would otherwise pollute the main context, or that benefits from parallelism**. Spawn them generously when both are true; avoid spawning them when the target is known and a direct tool call suffices.

### 5.4 Loops and schedules

Three recurrence primitives, picked by cadence and supervision:

- **`/loop`** — active polling with model-paced or fixed cadence. Use when you want Claude to keep checking on something within a single working session ("watch this deploy until it's done").
- **`/schedule`** — cron-style remote routines that run unattended. Use for things that should happen on a regular interval regardless of whether you're in session ("daily portfolio briefing," "weekly memory consolidation").
- **`spawn_task`** — fire-and-forget background work spun off from the current session. Use when you notice an out-of-scope cleanup that should not block current work.

Decision rubric: in-session and watching something → `/loop`. Out-of-session and recurring → `/schedule`. Out-of-scope cleanup → `spawn_task`.

### 5.5 The developer loop in Claude Code terms

`buttress.md` §6 names the loop: `plan → implement → test → review → commit`.

In Claude Code, that becomes:

| Step | Mechanism |
|---|---|
| plan | Plan mode + Explore/Plan subagents |
| implement | Edit / Write / Bash |
| test | Bash running the project's test runner; PostToolUse hook triggers it automatically |
| review | `/review` skill (bundled) composed with `code-reviewer` subagent |
| commit | Bash running `git`; Stop hook prompts for changelog update |

No step is skipped. The hooks (see §6) make skipping hard.

### 5.6 Session navigation

Three tools that keep long sessions legible:

- **`mark_chapter`** — explicit chapter markers at phase shifts. The transcript gets a table of contents; future you can jump to the right section.
- **TodoWrite** — task tracking inside the session. Mark complete as you go, never batch.
- **AskUserQuestion** — structured clarification when the next step is ambiguous. Better than guessing.

---

## 6. Pillar III — Guardrails

### 6.1 Hooks as the primary safety mechanism

Hooks are shell commands triggered by Claude Code events. They are the load-bearing safety mechanism and the single highest-leverage feature in this section.

Four hook types the factory uses:

- **PreToolUse** — blocks or modifies risky tool calls before they run. Destructive bash patterns. Reads of `.env*` files. Writes to generated or vendored paths.
- **PostToolUse** — runs after a tool call. Auto-format on Write/Edit. Trigger the type-checker on changed packages. Re-run the affected tests.
- **UserPromptSubmit** — inspects the user's prompt before Claude sees it. Routes "spec for X" to suggest `/spec`. Catches secret leakage in prompts.
- **Stop** — runs at end of turn or session. Prompts for changelog updates on feature branches. Archives transcripts before context compression.

A minimal PreToolUse hook config (shape, not literal syntax):

```json
{
  "PreToolUse": [
    { "matcher": "Bash", "pattern": "rm -rf|git push --force|git reset --hard", "action": "block" }
  ]
}
```

The CI pipeline from `buttress.md` §8 (`commit → lint → type-check → test → security → preview → approve → prod`) is expressed primarily as hooks. The factory's quality gates are not a separate CI system; they are the editor's own rails.

### 6.2 Permissions and modes

Permissions cascade across three settings files:

- `.claude/settings.json` — project-level. Committed to the repo. The factory's policy.
- `~/.claude/settings.json` — user-level. Personal preferences across all projects.
- `.claude/settings.local.json` — local overrides. Not committed; ephemeral.

Project settings define the factory's allow/deny rules. The `fewer-permission-prompts` skill periodically harvests common safe operations from session transcripts and adds them to the allowlist.

A minimal `settings.json` shape (illustrative; real schemas evolve):

```json
{
  "permissions": {
    "allow": [
      "Bash(npm test:*)",
      "Bash(git status)",
      "Read(**)",
      "Edit(src/**)"
    ],
    "deny": [
      "Bash(rm -rf:*)",
      "Read(.env*)"
    ]
  },
  "hooks": { /* §6.1 entries */ },
  "env": { "CLAUDE_MODEL": "claude-opus-4-7" }
}
```

### 6.3 Plan mode as the human-in-the-loop gate

Plan mode is the read-only design phase that ends with `ExitPlanMode`. It is the factory's primary HITL gate:

- Mandatory for `/spec`.
- Mandatory for `/refactor`.
- Optional but recommended for any change touching multiple files.

The contract: the plan file is the only thing that gets edited in plan mode. Approval gates execution. Without approval, the work does not proceed.

### 6.4 Worktree isolation

For risky work, agents run in isolated git worktrees. Use cases:

- **Risky refactors** — try the migration in a worktree; if it works, replay onto main.
- **Parallel experiments** — A/B variations of a tricky implementation, each in its own tree.
- **Security review on real diffs** — the `security-review` skill operates on a PR's worktree, isolated from local edits.

Worktrees auto-clean if no changes are made; otherwise the path is returned for inspection.

### 6.5 Subagent context isolation

Subagents protect the main session's context. The pattern:

- Spawn a subagent for any work that would dump >1k lines of tool output into the main session.
- The subagent's summary returns; the raw output stays in the subagent's window.
- Security-sensitive work (transcript scans, secret audits) runs in subagents so the secrets never reach the main context.

This is a guardrail as much as a workflow choice. The main context is the limited resource.

### 6.6 Three-layer schema governance, mapped

`buttress.md` §7.3 names three governance layers. In Claude Code:

- **Layer 1 (data shapes)** — PreToolUse hooks running schema validators (Pydantic, Zod, or equivalent) on changed data definitions. Bad schemas fail at the boundary.
- **Layer 2 (code shapes)** — PostToolUse hooks running the type checker on changed files. Bad types never get committed.
- **Layer 3 (agent outputs)** — skills encode validation steps that check agent outputs against contracts before they reach users or other agents.

Three layers, three enforcement mechanisms, three boundaries.

The review process — the multi-perspective lattice that orchestrates these guardrails against actual changes — is detailed in `review_plan.md`.

---

## 7. Pillar IV — Governance

### 7.1 The context-file hierarchy

Claude Code reads context files at multiple levels; the factory commits to a routing pattern:

- **`~/.claude/CLAUDE.md`** — user-global. Personal preferences. Never committed.
- **`<repo>/CLAUDE.md`** — project root. The top-level routing file. Brief overview + pointers to everything else.
- **`<repo>/<dir>/CLAUDE.md`** — per-directory. Domain-specific rules and context (e.g., `apps/web/CLAUDE.md`).
- **`<repo>/.agents/*.md`** — per-domain rules (`backend.md`, `frontend.md`, `testing.md`, `security.md`).
- **`<repo>/AGENTS.md`** — the canonical agent contract. Points at `.agents/`.

Routing pattern: **top-level files point down, never inline content**. The root CLAUDE.md is a router; the details live in `.agents/` and per-directory READMEs.

### 7.2 The memory system

Claude Code maintains a persistent file-based memory system at `~/.claude/projects/<repo>/memory/`. Four typed memories:

- **user** — who the user is, role, preferences, expertise
- **feedback** — corrections and confirmations of approach
- **project** — ongoing work, decisions, incidents, deadlines
- **reference** — pointers to external systems (Linear, Grafana, etc.)

The index lives in `MEMORY.md` — a one-line-per-memory pointer file. Memory accumulates across sessions and is the antidote to re-explaining the project every time.

### 7.3 Memory hygiene

Memory rots without maintenance. The factory runs `anthropic-skills:consolidate-memory` on a `/schedule` cadence (weekly is a reasonable default):

- Merge duplicate entries.
- Verify cited facts against current code (memory ages; code is truth).
- Prune stale project memories.
- Update entries that have changed.

Discipline: memory describes what was true *when written*. Before recommending from memory, verify it's still true.

### 7.4 Skills as opinionated workflows = governance

Skills encode "the right way to do X" once. Every invocation of `/fix` follows the same pattern. Every `/spec` produces the same artifact shape. This is governance in procedural form.

The relationship to `.agents/*.md`:

- **Rules** (`.agents/*.md`) describe **constraints**: what must be true. Static.
- **Skills** describe **procedures**: how to act. Dynamic.

Both are governance. Rules constrain agents; skills equip them.

### 7.5 Session transcripts as audit trail

Session transcripts are searchable via `mcp__ccd_session_mgmt__search_session_transcripts`. The factory treats them as part of the audit trail:

- "How did we decide X six weeks ago" → search for X in transcripts.
- ADRs cite the session in which the decision was made.
- The `transcript-archivist` subagent (see §13.5) periodically indexes and tags transcripts for future search.

### 7.6 The `settings.json` as policy-as-code

The project's `settings.json` is committed to the repo. Permissions, hooks, env vars, and model preferences ship *with the code*. A fresh clone inherits the rails immediately.

This matters for forks: when someone uses flying_buttress as a template, they inherit the safety mechanisms automatically. The factory is not just code; it is policy.

---

## 8. MCP — the factory's nervous system

### 8.1 MCP as integration substrate

The Model Context Protocol (MCP) is how Claude Code reaches outside itself. The MCP registry (`list_connectors`, `search_mcp_registry`, `suggest_connectors`) is searchable.

The factory's principle: **if it's not in MCP, it doesn't exist for agents**. Agents do not shell out to undocumented external state. Every external system the factory needs gets an MCP connector — installed, configured, and treated as part of the substrate.

### 8.2 Load-bearing connectors

The first-wave connectors:

- **`claude-in-chrome`** — agent-driven browser automation. Used for preview-phase smoke tests, end-to-end UAT, screenshot capture.
- **`claude-preview`** — UI preview, eval, network inspection during prototype phase. Tighter loop than a full browser session.
- **`ccd_directory`** — filesystem bridge for desktop workflows that need to operate outside the repo root.
- **`scheduled-tasks`** — cron-style routines, complementary to `/schedule`.
- **`ccd_session_mgmt`** — archive, list, and search session transcripts. Pairs with the audit-trail role in §7.5.
- **`mcp-registry`** — self-discovery of what to install next.

### 8.3 Custom MCP servers

Deferred for v1. The door is open for project-specific integrations (your billing system, your auth provider) once the load-bearing first wave is stable. The factory does not author custom MCP servers in the initial scaffolding.

### 8.4 The "all integrations through MCP" rule

A governance choice with safety implications. When every external dependency is an MCP connector:

- Agents have a complete inventory of what they can reach.
- Permissions are uniform — denying a connector denies the whole class of operation.
- Audit trails are uniform — connector calls appear in transcripts the same way as native tool calls.

If an integration cannot be expressed as MCP today, the factory wraps it in a CLI tool first, then promotes that to an MCP server later.

**Note:** This "all integrations through MCP" rule is enforced by convention, not by an automated guardrail. There is no hook today that detects when an agent shells out to an external system without going through MCP. Teams must rely on code review and the carry-back culture (ADR-003) to maintain it. A PreToolUse hook enforcing this is a candidate for v2.

---

## 9. The lifecycle, mapped to Claude Code

The four lifecycle phases from `buttress.md` §5, expressed as concrete Claude Code surfaces and features:

| Phase | Primary surface | Primary skills | Primary hooks | Primary subagents | Primary MCP |
|---|---|---|---|---|---|
| **Sketch** | Plan mode + AskUserQuestion | `/spec`, `init` | UserPromptSubmit (route spec intent) | Explore, Plan | — |
| **Prototype** | Edit / Write / Bash + fast mode | `/scaffold`, `/spec` follow-on | PostToolUse (format, type-check, run tests on save) | general-purpose | `claude-preview` |
| **Productionize** | Bash + hooks + plan mode | `/fix`, `/review`, `/security-review`, `/refactor` | PreToolUse (safety, secret-scan), PostToolUse (full gates) | code-reviewer, security-reviewer-deep | `claude-in-chrome` |
| **Operate** | Background + `/schedule` | `/runbook`, `/adr`, `consolidate-memory` | Stop (changelog), PreCompact (archive) | doc-keeper, transcript-archivist | `scheduled-tasks`, `ccd_session_mgmt` |

**Sketch.** Cheapest loop. Plan mode lets the spec form without any code touching disk. Output is `docs/specs/<slug>.md`.

**Prototype.** Fastest loop. Fast mode keeps wall-clock latency low. PostToolUse hooks run formatters and type-check on every save so the prototype stays compilable.

**Productionize.** Tightest gates. Every PR runs the full hook pipeline. Worktree isolation for risky refactors. Subagents for security and review.

**Operate.** Longest loop. `/schedule` runs daily and weekly routines. Transcript archives feed the audit trail. ADRs and runbooks accumulate.

---

## 10. Factory development workflow

### 10.1 The two-repo distinction

flying_buttress is the workbench. Projects built with it are the output. These must never share a git history.

- **flying_buttress** — the factory itself. CLAUDE.md templates, skills, hooks, settings patterns, and scaffolding tooling live here. Only flying_buttress artifacts get committed to this repo.
- **Sibling repos** — projects scaffolded from flying_buttress. Each has its own git repo and history. Improvements observed while building them flow back to flying_buttress manually.
- **less_tokens** — a special case: a token-reduction utility that installs *on top of* flying_buttress (and any other project). It is not built with the factory; it augments it.

### 10.2 less_tokens as a nested utility

`less_tokens` is a toolkit that reduces Claude's token consumption via four strategies: vector search over the codebase (search before Read), terse output enforcement (caveman mode), tool output truncation, and session compaction. It is cloned *into* the flying_buttress directory and its installer targets the parent:

```bash
cd flying_buttress
git clone https://github.com/<you>/less_tokens.git
python3 less_tokens/install.py   # installs hooks and tools into flying_buttress/
```

`less_tokens/` is gitignored in flying_buttress — it has its own repo and history. To upgrade:

```bash
cd less_tokens && git pull && python3 install.py
```

`less_tokens` is not a project produced by the factory. It is infrastructure the factory runs on.

### 10.3 Test project architecture: sibling repos

To validate the factory, test projects live as sibling repos next to flying_buttress, never inside it:

```
~/Documents/GitHub/
  flying_buttress/          ← this repo; stays clean
  fb_test_alpha/            ← scaffolded with /scaffold; its own git repo
  fb_test_beta/             ← another test project; its own git repo
```

The test project is created by running `/scaffold` (see §14.1) from within flying_buttress, targeting a directory outside the repo. The factory's templates are copied into the new repo; flying_buttress's git history is never touched.

**The rule:** improvements discovered while building in a test project are carried back manually and committed to flying_buttress. Test project files never enter flying_buttress's index.

### 10.4 The scaffold-and-carry-back loop

The development loop for improving the factory:

1. **Scaffold** — run `/scaffold` to stamp out a sibling test project from the current factory state
2. **Build** — work in the test project, using and stressing the factory's skills, hooks, and templates
3. **Observe** — note what's missing, wrong, or improvable in the factory
4. **Carry back** — open a PR against flying_buttress with the improvement and evidence it works (see §10.7 for rules)
5. **Repeat** — the next test project inherits the improved factory

This loop *is* the factory's test suite. There is no automated end-to-end test; the test is "can we build something real with it?"

### 10.5 What /scaffold must do

The `/scaffold` skill (see §14.1) must:

1. Accept a target path — a sibling directory outside flying_buttress
2. Stamp out the CLAUDE.md hierarchy, `.agents/` rules, skills, hooks, and `settings.json` patterns into that path
3. Initialize a git repo in the target if none exists
4. Optionally install `less_tokens` by cloning it into the new project (prompted)
5. Never write any files back into flying_buttress as a side effect of scaffolding

### 10.6 Sandbox for throwaway experiments

For quick experiments that won't become real projects, a `sandbox/` directory inside flying_buttress can be used. It is gitignored and discarded freely. The distinction:

- **`sandbox/`** — throwaway; no git history; discarded after the experiment
- **sibling repo** — keeper; has its own git history; may become a real project

The `.gitignore` stays minimal:

```
less_tokens/
sandbox/
```

### 10.7 Team coordination (ADR-003)

Full rules in [ADR-003](docs/adr/ADR-003-team-coordination.md). Summary:

**PR and merge process**
- Juniors open PRs for every factory change; no direct commits to `main`.
- PRs self-merge after 48 hours if there is no blocking comment from the senior.
- Changes to `.claude/settings.json` or `.agents/*.md` require explicit senior approval before merge (not subject to the 48h rule; see ADR-006).
- Senior reviews all merged PRs at the weekly sync (Mondays).

**Carry-back rules**
- The person who observed the improvement opens the PR against flying_buttress, not the test project.
- PR description must include: what changed, why it's an improvement, and evidence it works (transcript excerpt, output artifact, or screenshot).
- Conflicts with another junior's in-progress work are flagged at the weekly sync, not resolved unilaterally.

**Ownership**

| Artifact | Approval to merge |
|---|---|
| `ONBOARDING.md`, `CLAUDE.md` (root), skills, `backlog.md` | 48h self-merge |
| `.agents/*.md`, `.claude/settings.json` | Senior approval |
| `docs/adr/` | Senior approval to advance status to Accepted |

**Memory**
Memory files (`~/.claude/projects/.../memory/`) are per-machine and not committed. Decisions the team needs to share go in ADRs or `backlog.md`, not memory.

---

## 11. The Agent SDK and publishing outward

Skills, subagents, and hooks authored here should eventually be publishable via the Agent SDK — but only once they're stable. v1 does not design for this. When the factory has survived one real sibling project end-to-end, revisit which artifacts are worth publishing and what stable interfaces they require.

---

## 12. Feature-to-role mapping table

Every Claude Code feature mapped to a pillar and a role. Features without a current role are flagged honestly.

| Feature | Pillar | Role |
|---|---|---|
| CLI surface | Build env | Substrate; primary working surface |
| Desktop app | Build env | Daily driver; long-session ergonomics |
| Web app (claude.ai/code) | Build env | Portable fallback |
| IDE extensions | Build env | Opportunistic, single-file work |
| Bash tool + permissions | Build env | Universal executor |
| Read / Write / Edit | Build env | File-op verbs |
| NotebookEdit | Build env | Jupyter-flavored ML work; speculative for this factory |
| Multimodal inputs | Build env | Sketch artifacts, bug reports |
| WebFetch / WebSearch | Build env | Research, CVE lookups |
| `run_in_background` | Build env | Long-running tests, dev servers |
| Worktree isolation | Guardrails | Risky refactors, parallel experiments |
| Plan mode | Guardrails | Human-in-the-loop approval gate |
| Fast mode | Build env | Tight prototype iterations |
| Long context + compression | Build env | Cross-cutting refactors |
| Memory system | Governance | Per-project compounding knowledge |
| Model selection (Opus/Sonnet/Haiku) | Build env | Cost/quality dial per phase |
| Skills | Workflow | The named procedure layer |
| Subagents | Workflow + Guardrails | Division of labor; context isolation |
| `/init` skill | Governance | Bootstraps CLAUDE.md |
| `/review` skill | Workflow | PR review wrapper |
| `/security-review` skill | Workflow + Guardrails | Pending-change security audit |
| `/loop` | Workflow | Active polling, in-session |
| `/schedule` | Workflow | Cron-style routines, out-of-session |
| `spawn_task` | Workflow | Fire-and-forget background work |
| `mark_chapter` | Workflow | Long-session navigation |
| TodoWrite | Workflow | In-session task tracking |
| AskUserQuestion | Workflow | Structured clarification |
| ExitPlanMode | Guardrails | Plan-approval contract |
| ScheduleWakeup | Workflow | Agent self-pacing in `/loop` |
| Hooks (Pre/PostToolUse, UserPromptSubmit, Stop) | Guardrails | The CI pipeline as enforcement |
| Settings.json hierarchy | Guardrails + Governance | Policy-as-code; cascading |
| `fewer-permission-prompts` skill | Guardrails | Auto-allowlist maintenance |
| CLAUDE.md / AGENTS.md / `.agents/*.md` | Governance | Cascading rules and context |
| MEMORY.md + typed memories | Governance | Persistent compounding learning |
| `consolidate-memory` skill | Governance | Memory hygiene |
| `simplify` skill | Governance | Post-implementation quality review |
| `update-config` skill | Governance | Maintains settings.json |
| `bugfix` skill | Workflow | TDD bug fixes; building block under `/fix` |
| `claude-api` skill | Workflow | For authoring MCP servers / SDK code |
| Session transcripts + search | Governance | Audit trail |
| MCP registry | MCP | Self-discovery and install |
| `claude-in-chrome` | MCP | Agent-driven UI testing |
| `claude-preview` | MCP | Prototype-phase UI inspection |
| `ccd_directory` | MCP | Filesystem bridge |
| `scheduled-tasks` | MCP | Cron infrastructure |
| `ccd_session_mgmt` | MCP + Governance | Transcript archive and search |
| Agent SDK | Outward (§10) | Eventual publishing surface |
| `pptx`/`pdf`/`xlsx`/`docx` skills | Speculative | Ops/reporting candidates |
| `keybindings-help` skill | Unused | Personal config; out of scope here |
| `morning` skill | Unused | Domain-specific (portfolio); illustrative pattern only |
| `less_tokens` (nested utility) | Build env | Token reduction layer installed on top of flying_buttress; not a project produced by the factory |
| `/scaffold` skill | Workflow | Stamps out sibling test projects; the mechanism for the scaffold-and-carry-back loop (§10) |
| `setup-cowork` skill | Build env | Onboarding helper; one-time use |
| `loop`, `schedule` skills (the meta-skills) | Workflow | Skill-tooling for skill-authoring |
| `skill-creator` skill | Build env | Authoring new skills |

---

## 13. Speculative possibilities

Three buckets. Every Claude Code feature lands in exactly one.

**Load-bearing now.** Features the v1 scaffolding would use immediately:

- Skills (`/spec`, `/fix`, `/refactor`)
- Built-in subagents (Explore, Plan, code-reviewer)
- Hooks (Pre/Post/UserPromptSubmit/Stop)
- `settings.json` permissions and policy
- CLAUDE.md hierarchy + `.agents/*.md`
- Plan mode + worktrees
- Model selection
- `/review`, `/security-review`, `/scaffold`, `bugfix` skills
- `claude-preview` and `claude-in-chrome` MCP connectors
- `less_tokens` installed as the token-reduction layer

**Load-bearing soon.** Features earmarked for v2 once v1 ships a vertical slice:

- Custom subagents (schema-checker, doc-keeper, transcript-archivist, security-reviewer-deep)
- Memory system populated and maintained on `/schedule`
- `consolidate-memory` running weekly
- Agent SDK for publishing skills outward
- Transcript indexing for audit trail
- `mcp-registry` automation for connector self-discovery

**Speculative.** Features with no clear role yet but worth flagging:

- `pptx` / `xlsx` skills for ops reporting (weekly status decks, dashboards)
- `pdf` skill for parsing PRDs and contracts that come in as attachments
- `docx` skill for exporting changelogs to formats stakeholders use
- `Claude in Chrome` extensions beyond UAT — investigation, screenshot-driven bug reports
- `mcp__mcp-registry__suggest_connectors` as a feedback loop: "based on this repo's needs, which MCP servers should we install?"
- Custom MCP servers wrapping internal APIs (deferred per §8.3)

---

## 14. Delivery status

Scope is committed via ADR-001. Legend: **✓ done** — shipped and verified; **→ v2** — queued, not yet started; **○ speculative** — no committed date.

### 14.1 Skills

| Skill | Status |
|---|---|
| `/spec` — generate PRD, task list, tests, draft PR | ✓ done (v1) |
| `/fix` — atomic TDD bug fix | ✓ done (Tier 2 milestone, 2026-05-17) |
| `/scaffold` — stamp out a new sibling project from flying_buttress | → v2 |
| `/review` — code review against `.agents/` rules | → v2 |
| `/refactor` — map dependencies, propose design, migrate incrementally | ○ speculative |
| `/bootstrap` — fork-time wizard that fills in role choices from `buttress.md` §3 | ○ speculative |
| `/adr` — author or amend an Architecture Decision Record | ○ speculative |
| `/runbook` — generate a runbook stub for a new feature | ○ speculative |
| `/promote` — graduate a prototype from `/apps/prototype/` to a real surface | ○ speculative |
| `/audit` — run all governance checks and produce a status report | ○ speculative |

### 14.2 Hooks

| Hook | Status |
|---|---|
| **PostToolUse(Bash)** bash-logger — record tool use patterns for active learning | ✓ done (2026-05-17) |
| **PostToolUse(Write)** tool-registry — track writes to `tools/` for skill promotion | ✓ done (2026-05-17) |
| **Stop** pattern-analyzer — surface repeated patterns as tool promotion candidates | ✓ done (2026-05-17) |
| **Stop** update_docs_on_commit — auto-insert CHANGELOG bullet on each commit | ✓ done |
| **PreToolUse(Bash)** — block destructive patterns (`rm -rf /`, force-push to main, hard reset) | → v2 |
| **PostToolUse(Write\|Edit)** — auto-format changed files | → v2 |
| **PostToolUse(Write\|Edit)** — trigger type-check on changed packages | → v2 |
| **PostToolUse(Write\|Edit)** — trigger affected tests on save | → v2 |
| **PreToolUse(Bash)** — MCP compliance guardrail (C1 candidate, ADR-007) | → v2 |
| **UserPromptSubmit** — route detected intent ("fix X", "spec Y") to matching skills | ○ speculative |
| **PreCompact** — archive transcript to `docs/transcripts/` before compression | ○ speculative |

### 14.3 `settings.json`

| Item | Status |
|---|---|
| `permissions.allow` — common read-only ops, project-scoped writes | ✓ done (v1) |
| `permissions.deny` — destructive bash, secrets paths, `.git/` internals | ✓ done (2026-05-16) |
| `hooks` — active learning hooks wired | ✓ done (2026-05-17) |
| `hooks` — format / type-check / test on save | → v2 |
| `env` — model preference, fast-mode default, project flags | ○ speculative |

### 14.4 CLAUDE.md sections

| Section | Status |
|---|---|
| Project overview — one paragraph; routes to `buttress.md` | ✓ done (v1) |
| Operating manual — routes to `plan.md` | ✓ done (v1) |
| Rules — routes to `.agents/*.md` | ✓ done (v1) |
| Workflows — routes to skills under `.claude/skills/` | ✓ done (v1) |
| Memory — routes to `~/.claude/projects/flying_buttress/memory/MEMORY.md` | ○ speculative |
| Gotchas — load-bearing exceptions specific to this repo | ○ speculative |

### 14.5 Custom subagents

| Subagent | Status |
|---|---|
| **security-reviewer-deep** — slow, thorough; runs in a worktree against a PR diff | ○ speculative |
| **schema-checker** — runs Pydantic/Zod validators on changed schemas | ○ speculative |
| **doc-keeper** — checks runbooks and changelogs were updated alongside features | ○ speculative |
| **transcript-archivist** — periodically archives and indexes session transcripts | ○ speculative |

### 14.6 MCP connectors

| Connector | Status |
|---|---|
| `claude-in-chrome`, `claude-preview`, `ccd_directory`, `scheduled-tasks`, `ccd_session_mgmt`, `mcp-registry` | ✓ installed |
| Custom MCP servers wrapping project-specific systems | ○ speculative (deferred per §8.3) |

Review-specific skills, hooks, subagents, and GitHub Actions are enumerated separately in `review_plan.md` §9.

---

The menu is the deliverable. Choices about sequence, ownership, and priority happen at scaffolding time — not in this document.
