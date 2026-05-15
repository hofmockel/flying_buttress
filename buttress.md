# buttress.md

> *A buttress holds up the cathedral without being the cathedral.*

This document is the foundation of **flying_buttress** — the doc you read first, the doc that says what this repo is for and how it works.

---

## 1. What is Flying Buttress?

Flying Buttress is a **software factory**: a repository template and methodology for building applications end-to-end. It supports the path from a sketch on a napkin to production-grade software, with AI-native workflows woven in from the start.

The factory rests on nine pillars:

- **app building** — primitives, scaffolding, and structure for shipping real applications
- **rapid iteration** — short feedback loops at every phase
- **best practices** — engineering discipline baked in, not bolted on
- **prototyping** — a path that welcomes the rough draft
- **production-grade** — the same path hardens into something you can run for years
- **tools** — concrete utilities for the things you do every day
- **agents** — AI collaborators as first-class participants
- **workflows** — repeatable named procedures for common work
- **rules** — explicit contracts that agents (human and AI) follow

A buttress is not the building. It does not pretend to be your application. It is the structure that lets the application stand and grow.

---

## 2. Why this exists

### The prototype-to-production gap

Most projects die in the gap. "It works in my notebook" does not translate to "it survives production traffic." The cost of crossing the gap is usually a rewrite — different stack, different patterns, different team. Flying Buttress closes the gap by making the same path serve both. The prototype is built on the production substrate; production is the prototype, hardened.

### The AI-native shift

In 2026, agents are infrastructure, not features. Code is written, reviewed, refactored, and deployed with AI in the loop. A factory that ignores this fact is already legacy. Flying Buttress treats agents as collaborators: they need rules, context, and a contract — the same as any other contributor.

### Why a factory, not a framework

Frameworks lock you in. They impose their own abstractions, their own naming, their own runtime. Factories give you scaffolding you keep ownership of. Flying Buttress is stack-agnostic by design — it tells you which **roles** every production application needs filled, but lets you choose the tools that fill them.

---

## 3. The methodology

Every production application needs six roles filled. The opinions in this section are about *which roles must exist* and *what properties each role must have*. The tool choices are yours.

### Foundation
The orchestrator that makes a monorepo navigable: caching, task graphs, shared dependencies, consistent versioning.

*Examples: Turborepo, Nx, pnpm workspaces, Bazel, Pants.*

**Required properties:** task graph with caching, workspace-aware dependency management, support for multiple language runtimes.

### Application surfaces
The runnable artifacts users touch — web frontends, HTTP APIs, mobile apps, background workers.

*Examples: Next.js, SvelteKit, FastAPI, NestJS, Expo, React Native.*

**Required properties:** server-rendered or static fallback for web; typed contracts at every boundary; first-class testing harness.

### Agent layer
The orchestration framework for AI workflows. State machines, retry semantics, human-in-the-loop checkpoints.

*Examples: OpenAI Agents SDK, LangGraph, PydanticAI, CrewAI, Temporal (for durable execution).*

**Required properties:** support stateful and cyclical flows, not just linear chains; expose a checkpoint API for human approval; emit structured traces.

### Developer tooling
The coding loop where humans and AI agents meet the codebase.

*Examples: Claude Code, Cursor, Codex CLI, GitHub Copilot.*

**Required properties:** read the repo's rules files (see §7); operate on diffs, not whole-file rewrites; respect the quality gates in §8.

### Quality + governance
The bar for "is this code allowed in?" Type system, linter, formatter, test runner, schema validator, security scanner.

*Examples: TypeScript, mypy, ESLint, Ruff, Prettier, Vitest, pytest, Playwright, Pydantic, Zod, Semgrep, Trivy.*

**Required properties:** runs on every commit; cannot be disabled without an ADR; covers data shapes, code shapes, and agent outputs (the three-layer model in §7).

### Operations
What you run in production and how you watch it. Deploy target, error tracking, product analytics, agent observability.

*Examples: Vercel, Fly.io, Railway, Render, Sentry, PostHog, OpenTelemetry, LangSmith, Grafana.*

**Required properties:** structured logs by default; traces that cross service boundaries; agent calls instrumented like any other dependency.

---

**The test:** Swap any one layer without rewriting the others. If your Foundation choice forces your Application choice, you have a framework, not a factory.

---

## 4. Repo layout

This is the target state. Section 10 tracks what is scaffolded and what is not.

```text
/apps           — runnable applications (web, api, worker, mobile)
/packages       — shared libraries (ui, config, sdk, agents)
/.agents        — per-domain rules files (backend, frontend, testing, security)
/.github        — CI/CD workflows
/docs           — architecture decisions, runbooks, onboarding
/scripts        — repo-level tooling
/less_tokens    — installed token-reduction layer (see §7)
AGENTS.md       — top-level agent contract
CLAUDE.md       — top-level Claude Code context
buttress.md     — this document
Makefile        — durable workflow surface
README.md       — public-facing intro
```

Per-directory READMEs handle the next level of detail. The top-level layout is the load-bearing contract; nested structure belongs to whoever owns that directory.

---

## 5. The lifecycle: sketch → prototype → production → operate

The spine of the factory. Every piece of work flows through four phases. Each phase has a cheapest-possible-loop; you only graduate when you have to.

### 5.1 Sketch

The cheapest loop. Output is human-readable artifacts — a PRD, a task list, a sequence diagram — *not* code. The goal is alignment, not implementation.

The factory accelerates this phase with `make spec` (or `/spec` — see §6). A one-line prompt produces a structured plan you can review, edit, and discard before any code is written.

> *Example:* `make spec FEATURE="add billing portal"` → produces `docs/specs/billing-portal.md` with goals, non-goals, surfaces touched, and a task list.

### 5.2 Prototype

The cheapest loop that produces running code. Workspace scaffolded via generators; devcontainer ensures parity with production; feature flags from day one so prototypes don't sneak into production by accident.

Preview deploys are mandatory at this stage — stakeholder feedback on a rough version is cheaper than feedback on a finished one. Every PR gets a URL.

> *Example:* `make scaffold APP=billing` → generates `/apps/billing/` from the application template, wires it into the workspace, and opens a draft PR with a Vercel preview link.

### 5.3 Productionize

The phase where the prototype hardens. Quality gates from §8 run on every PR. Schema contracts (Pydantic, Zod) lock down data shapes. LLM guardrails wrap any agent-facing surface that talks to users.

The bar: **no merge unless all green.** Exceptions require an ADR — a short written record of what rule was broken, why, and when the debt will be repaid.

> *Example:* A PR adds a `/checkout` endpoint. CI runs lint, types, tests, security scan, schema validation, and a smoke test against the preview deploy. All green → ready for human review.

### 5.4 Operate

The phase that lasts forever. Observability across the stack: app traces (OpenTelemetry), error reports (Sentry), product analytics (PostHog), agent traces (LangSmith or equivalent). Each new feature ships with a runbook and a dashboard panel.

ADRs are auto-maintained alongside features. The changelog is generated, not hand-written. The doc you're reading is the only doc you maintain by hand.

> *Example:* A latency regression appears in the agent layer. LangSmith trace points at a specific tool call; the runbook (committed alongside the feature) tells the on-call engineer what to check first.

---

## 6. Workflows: the user-facing API

Workflows are the factory's user-facing API. They have a **dual surface**:

- **Makefile targets** — the durable mechanics. Run anywhere, in any shell, from any AI agent, by any human. The substrate.
- **Claude Code skills** — the agentic wrappers. Same logic, friendlier interface, agent-aware context. The skin.

You can use either. They produce the same artifacts.

### Three load-bearing workflows

**`make spec` / `/spec`** — generate a PRD, task list, tests, and a draft PR for a new feature.

```text
plan a feature → review the spec → adjust → graduate to prototype
```

**`make fix` / `/fix`** — reproduce a bug, write a failing test, patch, open a PR.

```text
identify the bug → red test → green test → review → ship
```

**`make refactor` / `/refactor`** — map dependencies, propose a design, migrate safely with rollback.

```text
map → propose → migrate incrementally → verify → land
```

### The underlying developer loop

Every workflow above hangs on the same five-step loop:

```text
plan → implement → test → review → commit
```

The factory is opinionated that no step is skipped. The loop is short enough that skipping a step never saves real time.

> *Note:* As of this writing, the slash-command surface is target state. The Makefile substrate is scaffolded incrementally; see §10.

---

## 7. Rules and the context system

This is the highest-leverage section of the factory. Rules files do more per byte than any other artifact in the repo.

### The `.agents/` directory

Per-domain rules, one file per concern:

- `.agents/backend.md` — service patterns, error handling, database access
- `.agents/frontend.md` — component patterns, state management, accessibility
- `.agents/testing.md` — what to mock, what not to mock, coverage expectations
- `.agents/security.md` — secrets handling, authn/authz, input validation

Each file is short and specific. Each rule has a **why** so future readers can judge edge cases.

### Top-level contracts

- `AGENTS.md` — the canonical contract every agent (human or AI) reads first
- `CLAUDE.md` — Claude Code-specific context that points at `.agents/`
- `.cursorrules` — Cursor-specific context that points at `.agents/`

The contracts are routers, not content. They point at `.agents/` and the relevant per-directory READMEs.

### Schema-as-contract: the three-layer model

Governance is layered. Each layer rejects bad inputs at a different boundary:

1. **Data shapes** — Pydantic, Zod, or equivalent at every API boundary
2. **Code shapes** — the type system at every function boundary
3. **Agent outputs** — LLM guardrails at every agent-to-system boundary

The layers do different jobs. The first catches malformed requests. The second catches programmer errors. The third catches hallucinations and prompt injections.

### `less_tokens` — installed tooling, not source code

`less_tokens` is a **token-reduction add-on**: a tooling layer that installs into the repo, lives under `/less_tokens/`, and is ignored by git. It is upgraded by re-running its installer, which gracefully overwrites the previous version.

Treat `less_tokens` as managed infrastructure, the same way you treat `node_modules/` or a `.venv/` — not source code you edit by hand. For usage details, see `less_tokens/CLAUDE.md` after installation.

### The discipline

Rules files are merged via PR like code. They are short, specific, and dated. They are never tribal-knowledge dumps. If a rule cannot be written in three lines with a clear why, it is not a rule yet — it is a discussion.

---

## 8. Quality gates and the CI pipeline

Every change flows through the same pipeline:

```text
commit → lint → type-check → test → security scan → preview deploy → human approve → production
```

| Gate | Checks | Fails on | Override path |
|---|---|---|---|
| **lint** | code style, dead code | any rule violation | none — fix the code |
| **type-check** | static types | any type error | none — fix the types |
| **test** | unit + integration | any failing test | none — fix the test or the code |
| **security scan** | known CVEs, secret leakage, dangerous patterns | any high-severity finding | ADR documenting accepted risk |
| **preview deploy** | smoke test on a real URL | deploy failure or smoke test failure | none — fix the deploy |
| **human approve** | review by a maintainer | maintainer asks for changes | iterate until approved |

The bar: **no merge unless all green; no exceptions without an ADR.**

The ADR mechanism is the escape hatch. It is not a backdoor — every ADR is a written, reviewed, dated record of a deliberate trade-off. ADRs accumulate; if too many pile up against one rule, the rule changes.

---

## 9. How to use this repo

Three paths in.

### Clone and explore

The fastest way to understand the factory. Read in this order:

1. This document (`buttress.md`)
2. `AGENTS.md` and `.agents/*.md` — the rules
3. One application under `/apps/` — pick the one closest to what you want to build

You will know in 20 minutes whether the factory fits your project.

### Use as a template

Fork the repo. Run `make bootstrap`. The bootstrap script asks you to fill in the role choices from §3 — which Foundation, which Application surfaces, which Agent layer — and scaffolds the workspace to match.

Once bootstrapped, the factory becomes yours. You own the rules, the workflows, and the tool choices. The factory's job ends at the moment of fork.

### Contribute upstream

Improvements that benefit every fork belong upstream. The contribution path:

1. Read `CONTRIBUTING.md` (target state)
2. Add an entry to `BACKLOG.md` describing the problem
3. Open a draft PR linked to the backlog entry
4. Iterate against the same quality gates everyone else uses

The BACKLOG/CHANGELOG split is borrowed directly from `less_tokens` — a working precedent already in this repo.

---

## 10. Status and next steps

Most of what this document describes is target state. The repo is fresh. This section is the load-bearing honesty mechanism.

### Scaffolding checklist

- [x] `buttress.md` (this document)
- [ ] `less_tokens/` installed via its proper installer (currently present as a sibling directory — needs integration)
- [ ] `/apps`, `/packages`, `/.agents` directories created
- [ ] `Makefile` with `bootstrap`, `spec`, `fix`, `refactor` targets
- [ ] `.claude/` skills wrapping the Make targets
- [ ] GitHub Actions workflows for the §8 pipeline
- [ ] ADR template at `docs/adr/0000-template.md` and first ADRs
- [ ] `CLAUDE.md`, `AGENTS.md`, `README.md`, `CONTRIBUTING.md` at the repo root
- [ ] First example application under `/apps/` demonstrating the lifecycle end-to-end

### Working principles for the build-out

- **Vertical slices over horizontal layers.** Ship the spec → prototype → production path for one tiny feature before generalizing.
- **The doc is the spec.** Sections of this file become checklists; when a section's promises are real, the corresponding checkbox flips.
- **Rules before tools.** `.agents/*.md` lands before the tools they govern. Agents need the rules to make good choices.

---

## 11. Glossary

- **Buttress** — the supporting structure that lets the cathedral stand. This repo.
- **Factory** — a template plus methodology, owned and modifiable by the user.
- **Role** — an architectural slot in the methodology (Foundation, Application, Agent layer, etc.) that must be filled but can be filled by any reasonable tool.
- **Agent** — an AI collaborator that follows the same rules and gates as a human contributor.
- **Workflow** — a named, repeatable procedure with both a Makefile and a Claude Code skill surface.
- **Rule** — a short, specific, dated contract written down in `.agents/*.md` or a top-level AGENTS-style file.
- **Gate** — an automated check that a change must pass to merge.
- **Golden path** — the supported route through the lifecycle: sketch → prototype → production → operate.
- **Sketch** — the cheapest loop in the lifecycle; produces a spec, not code.
- **Devcontainer** — a containerized development environment that mirrors production.
- **ADR** — Architecture Decision Record. The written, reviewed escape hatch for breaking a rule.
- **less_tokens** — a token-reduction tooling layer that installs into the repo and is treated as managed infrastructure.
