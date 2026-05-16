# flying_buttress

> *A buttress holds up the cathedral without being the cathedral.*

**A software factory for AI-native development.** flying_buttress is a repository template and methodology that closes the prototype-to-production gap — with Claude Code as the build substrate, rules-driven agents as first-class collaborators, and quality gates that ship with the repo.

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Made with Claude Code](https://img.shields.io/badge/built%20with-Claude%20Code-blueviolet)
![License](https://img.shields.io/badge/license-MIT-blue)

---

```
$ make scaffold TARGET=../my-app

flying_buttress scaffold
────────────────────────────────────────
Project name [my-app]: Acme API
Project slug (kebab-case) [acme-api]:
Install less_tokens? (y/N): y

Scaffolding 'Acme API' → /Users/dev/my-app
────────────────────────────────────────
  [+] CLAUDE.md
  [+] ONBOARDING.md
  [+] Makefile
  [+] .agents/backend.md
  [+] .agents/frontend.md
  [+] .agents/testing.md
  [+] .agents/security.md
  [+] .claude/settings.json
  [+] .claude/skills/spec/SKILL.md
  [+] docs/specs/
  [+] .gitignore
  [+] git init
  [+] less_tokens cloned

────────────────────────────────────────
Done. Next steps:
  cd ../my-app
  make validate-hooks
  claude   # run /spec to start your first feature
```

---

## Table of Contents

- [What is flying_buttress?](#what-is-flying_buttress)
- [Why a factory, not a framework](#why-a-factory-not-a-framework)
- [Quick Start](#quick-start)
- [How it works](#how-it-works)
  - [The four pillars](#the-four-pillars)
  - [The lifecycle](#the-lifecycle)
  - [The six roles](#the-six-roles)
- [Features](#features)
- [Project structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## What is flying_buttress?

Most projects die in the gap between prototype and production. "It works in my notebook" does not translate to "it survives production traffic." The cost of crossing the gap is usually a full rewrite — different stack, different patterns, different team.

**flying_buttress closes that gap** by making the same path serve both. The prototype is built on the production substrate. Production is the prototype, hardened.

It does this by shipping a repo that comes with its own rails:

- **Domain rules** in `.agents/` that every AI agent reads before touching the codebase
- **Skills** like `/spec`, `/fix`, and `/refactor` that enforce the right workflow every time
- **Quality gates** in the `Makefile` that run locally and in CI
- **An ADR system** that turns every architectural decision into a searchable, dated record

When you scaffold a new project with flying_buttress, you inherit all of it immediately.

---

## Why a factory, not a framework

Frameworks lock you in. They impose their own abstractions, naming, and runtime. Factories give you scaffolding **you keep ownership of**.

flying_buttress is opinionated about *how you work* — the workflow, the rules system, the quality gates. It is deliberately agnostic about *what you build* — the language, the framework, the deploy target are all yours to choose.

The test: swap any one layer without rewriting the others. If your Foundation choice forces your Application choice, you have a framework. flying_buttress passes that test.

---

## Quick Start

**Requirements:** Python 3.9+, [Claude Code CLI](https://claude.ai/code), Git

```bash
# 1. Clone the factory
git clone https://github.com/hofmockel/flying_buttress.git
cd flying_buttress

# 2. Verify the factory is healthy
make validate-hooks

# 3. Scaffold a new project into a sibling directory
make scaffold TARGET=../my-project

# 4. Move into your new project
cd ../my-project

# 5. Open Claude Code and run your first workflow
claude
# → /spec add user authentication
```

Your new project now has the full factory infrastructure: rules files, the `/spec` skill, a baseline `settings.json`, and a `Makefile` with quality gate stubs ready to fill in.

---

## How it works

### The four pillars

flying_buttress rests on four Claude Code-native pillars:

| Pillar | What it does |
|---|---|
| **Build environment** | CLI-first surfaces, tool primitives, execution modes, model selection |
| **Workflow** | Named procedures as skills (`/spec`, `/fix`, `/refactor`); subagents as division of labor |
| **Guardrails** | Hooks, permissions, plan mode, and worktree isolation as the safety mechanism |
| **Governance** | Context files, memory, session transcripts, and `settings.json` as policy-as-code |

### The lifecycle

Every piece of work flows through four phases. Each has a cheapest-possible loop; you only graduate when you have to.

```
sketch → prototype → productionize → operate
```

| Phase | Cheapest loop | Primary workflow | Output |
|---|---|---|---|
| **Sketch** | Plan mode + spec | `/spec` | PRD in `docs/specs/` |
| **Prototype** | Edit + fast mode | `/spec` follow-on | Running code |
| **Productionize** | Full quality gates | `/fix`, `/review`, `/security-review` | Merged PR |
| **Operate** | Scheduled routines | `/runbook`, `/adr` | Runbooks, ADRs |

### The six roles

Every production application needs six roles filled. flying_buttress names the roles; you choose the tools:

| Role | What it does | Examples |
|---|---|---|
| **Foundation** | Monorepo orchestration, task graphs, shared deps | Turborepo, Nx, pnpm workspaces |
| **Application surfaces** | Runnable artifacts users touch | Next.js, FastAPI, NestJS, Expo |
| **Agent layer** | AI workflow orchestration, state machines, HITL | LangGraph, PydanticAI, Temporal |
| **Developer tooling** | The coding loop for humans and agents | Claude Code, Cursor, Codex CLI |
| **Quality + governance** | Types, linters, tests, schema validators, scanners | TypeScript, Ruff, pytest, Pydantic, Semgrep |
| **Operations** | Deploy target, observability, agent tracing | Vercel, Fly.io, Sentry, PostHog, LangSmith |

---

## Features

| Feature | Description |
|---|---|
| **`make scaffold`** | Stamp out a new project from the factory in under a minute |
| **`/spec` skill** | Guided PRD generation — plan mode, Explore + Plan subagents, approval gate |
| **`.agents/` rules** | Domain rules (backend, frontend, testing, security) that every AI session inherits |
| **`settings.json`** | Permissions and deny list shipped with the repo — policy-as-code from day one |
| **`make validate-hooks`** | Tier-1 smoke checklist that runs in under 5 seconds |
| **ADR system** | Structured decision records in `docs/adr/` — every gap has a record and a fix |
| **`less_tokens` support** | Optional token-reduction layer (vector search, terse output, tool truncation) |
| **Makefile underlay** | Every skill delegates to a Make target — works without Claude Code in CI |
| **Stack-agnostic** | No framework opinions; choose any tool that fills each of the six roles |

---

## Project structure

```
flying_buttress/
│
├── templates/                  ← the backbone: what every new project inherits
│   ├── CLAUDE.md.tmpl
│   ├── ONBOARDING.md.tmpl
│   ├── Makefile.tmpl
│   ├── .agents/                ←   domain rules templates
│   ├── .claude/skills/spec/    ←   /spec skill template
│   └── docs/specs/             ←   spec output template
│
├── scripts/
│   └── scaffold.py             ← copies templates, substitutes values, inits git
│
├── .agents/                    ← domain rules for the factory repo itself
│   ├── backend.md
│   ├── frontend.md
│   ├── testing.md
│   └── security.md
│
├── .claude/
│   ├── settings.json           ← project-level permissions (policy-as-code)
│   └── skills/spec/SKILL.md   ← /spec slash command
│
├── docs/
│   ├── adr/                    ← architecture decision records
│   └── specs/                  ← specs generated by /spec
│
├── CLAUDE.md                   ← Claude Code entry point (router, not content)
├── ONBOARDING.md               ← 5-step path from clone to first PR
├── Makefile                    ← durable workflow substrate
├── buttress.md                 ← the manifesto
└── plan.md                     ← operating manual for Claude Code as factory floor
```

---

## Documentation

| Doc | What it covers |
|---|---|
| [MANUAL.md](MANUAL.md) | **Start here for day-to-day use** — scaffold, /spec, Makefile, rules, settings, ADRs |
| [ONBOARDING.md](ONBOARDING.md) | First PR in 5 steps — for new contributors |
| [buttress.md](buttress.md) | Philosophy, methodology, and the six roles |
| [plan.md](plan.md) | Claude Code internals — pillars, lifecycle, MCP, governance |
| [docs/adr/](docs/adr/README.md) | Architecture decisions and current work queue |

---

## Contributing

The factory is actively developed. The contribution model is the same one it ships with:

1. Read [ONBOARDING.md](ONBOARDING.md) — it applies to contributors too.
2. Read [backlog.md](backlog.md) for open gaps and [docs/adr/README.md](docs/adr/README.md) for in-progress decisions.
3. Find the lowest-numbered ADR with status **Proposed** — that is the next thing to build.
4. Open a PR following the process in [docs/adr/ADR-003-team-coordination.md](docs/adr/ADR-003-team-coordination.md).

Improvements that generalize — better rules, new skills, stronger quality gates — belong upstream. Improvements that are project-specific stay in your fork.

---

## License

MIT — see [LICENSE](LICENSE).

> **flying_buttress** is a factory, not a product. It gives you a starting point you own completely. The scaffolding is yours; what you build with it is yours. The factory's job ends at the moment of the fork.
