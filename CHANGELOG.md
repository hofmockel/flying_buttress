# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- fix: update_docs_on_commit cd-regex now recognises \\n as a command separator — 2026-05-20
- fix: update_docs_on_commit uses last cd in chain, not first, for sibling-repo guard — 2026-05-20
- fix: tool-registry hook now triggers on Edit as well as Write (`c128b59`) — 2026-05-20

- fix: tool-registry hook now triggers on Edit as well as Write for skill tool stubs — 2026-05-20
- fix: mcp_check curl regex ^curls?$ -> ^curl$ eliminates phantom match (`8ebc33a`) — 2026-05-20

- fix: mcp_check.py curl regex changed from ^curls?$ to ^curl$ — eliminates spurious match on phantom command 'curls' — 2026-05-20
- fix: update_docs_on_commit resolves CHANGELOG.md from repo root not CWD (`4502d20`) — 2026-05-20

- fix: update_docs_on_commit resolves CHANGELOG.md from repo root not CWD — 2026-05-20
- fix: search() skips corrupt embedding blobs instead of crashing (`6ff98c7`) — 2026-05-20

- fix: search() skips corrupt embedding blobs instead of crashing with ValueError; warns to stderr — 2026-05-20
- fix: index-refresh now triggers re-embed for root_globs paths (`0d1a9fe`) — 2026-05-20

- fix: index-refresh now triggers re-embed for docs/**/*.md and .agents/*.md by importing and checking INDEXED_ROOT_GLOBS — 2026-05-20
- fix: search-first gate now enforces search-before-Read for root_globs paths (`1a76b14`) — 2026-05-20

- fix: search-first gate now enforces search-before-Read for docs/**/*.md and .agents/*.md files by consulting INDEXED_ROOT_GLOBS via PurePosixPath.match() — 2026-05-20

- feat: add --add mode for non-destructive install into existing projects (`16c17fa`) — 2026-05-19

- feat: add --add mode for non-destructive install into existing projects (`16c17fa`) — 2026-05-19

- feat: add --add mode for non-destructive install into existing projects (`c2dff29`) — 2026-05-19

- feat: add /scaffold skill (`8932675`) — 2026-05-19

- feat: add PreToolUse(Bash) MCP compliance hook (`3ef1df3`) — 2026-05-19

- Add PostToolUse on-write hooks: fmt, lint, test-on-save (`6951f43`) — 2026-05-17

- Add /review skill: code review against .agents/ rules (`caf05e9`) — 2026-05-17

- G2/G3: add team coordination and onboarding pointers to plan.md (`6ae2101`) — 2026-05-17

- G1: rewrite plan.md §14 as delivery-status table (`5377572`) — 2026-05-17

- CB1: add --name/--slug flags to scaffold.py (`8ce743c`) — 2026-05-17

- Tier 2 milestone complete: carry-back CHANGELOG hook scoping fix (`5b48c07`) — 2026-05-17

- Add /fix skill: atomic TDD bug-fix loop for factory and templates (`6b03a18`) — 2026-05-17

- Add /fix skill: atomic TDD bug-fix loop for factory and templates (`6b03a18`) — 2026-05-17

- Add /fix skill: atomic TDD bug-fix loop for factory and templates (`d35eb8b`) — 2026-05-17

- Wire active learning hooks into settings.json; activate make test (`ef813bb`) — 2026-05-17

- Add active learning system: hook-driven tool promotion, spec deferral, and tool registry (`05c1c2b`) — 2026-05-16

- continue.md: expand Tier 2 milestone with step-by-step instructions and /fix options (`e519798`) — 2026-05-16

- C4: add deny list to settings.json and template; declare v1 complete (`ea6df07`) — 2026-05-16

- ADR-007: accept doc cleanup; fix C1/C2/C3 in plan.md (`8e9b814`) — 2026-05-16

- ADR-006: accept settings governance; expand MANUAL.md §7 with PR trigger list (`9a03932`) — 2026-05-16

- Add Claude Code hooks and vector search tooling; update settings and gitignore (`5a1d6b1`) — 2026-05-16

- ADR-005: accept Makefile underlay; anchor plan.md §5.1 to concrete spec (`357f331`) — 2026-05-16

- ADR-004: accept factory test strategy; add three-tier checklist to docs (`20d72ac`) — 2026-05-16

## [0.1.0] - 2026-05-15

### Added

**Core documentation**
- `README.md`: full project overview — quickstart, four-pillar model, lifecycle, six roles, feature table, project structure
- `MANUAL.md`: comprehensive day-to-day operations reference — scaffold, `/spec`, Makefile, rules, permissions, ADRs, team coordination, lifecycle, extensibility, troubleshooting
- `ONBOARDING.md`: Day 1 path (5 steps) from clone to first PR; addresses G3 from `backlog.md`
- `buttress.md`: manifesto defining the flying_buttress software-factory concept and its tool-agnostic spec
- `plan.md`: operating manual mapping the factory lifecycle onto Claude Code primitives (build environment, workflow, guardrails, governance, scaffolding menu); §10 documents sibling-repo testing pattern and `less_tokens` relationship
- `review_plan.md`: multi-perspective review lattice — ten review kinds and five execution mechanisms (rules, skills, hooks, subagents, GitHub Actions)
- `backlog.md`: gap registry — six critical gaps (G1–G6) and three smaller concerns (C1–C3) surfaced by architect review; each tied to an ADR
- Exploratory source notes: `Core Components of a Modern "Super-Repo".md`, `Repo layout.md`, `claude-features.md`
- `CHANGELOG.md`: this file

**Architecture Decision Records**
- `ADR-001` accepted: v1 MVP scope locked — 8 deliverables in sequence, `/spec` end-to-end as acceptance test
- `ADR-002` (proposed): Day 1 onboarding path — 5-step sequence, `make validate-hooks` smoke gate
- `ADR-003` (proposed): team coordination model — PR process, weekly sync cadence, carry-back arbitration, ownership table
- `ADR-004` (proposed): factory test strategy — tier-1 smoke checklist (`make validate-hooks`), tier-2 scaffold integration test
- `ADR-005` (proposed): Makefile underlay — every skill that shells out calls a Make target; Make is the durable substrate
- `ADR-006` (proposed): settings governance — senior approval required for `.claude/settings.json` and `.agents/security.md` changes
- `ADR-007` (proposed): documentation cleanup — resolves C1 (MCP convention), C2 (§11 agent SDK noise), C3 (model rubric cadence)

**Templates** (`templates/` — stamped into every new project by `make scaffold`)
- `CLAUDE.md.tmpl`: Claude Code entry point, pre-configured with `.agents/` pointer
- `ONBOARDING.md.tmpl`: team onboarding doc template
- `Makefile.tmpl`: quality gate stubs (`test`, `lint`, `fmt`, `validate-hooks`, `spec`, `help`)
- `.agents/backend.md.tmpl`, `frontend.md.tmpl`, `testing.md.tmpl`, `security.md.tmpl`: domain rule templates with project-specific placeholders
- `.claude/settings.json.tmpl`: permissions baseline (allow-only; deny list deferred — see C4 in `backlog.md`)
- `.claude/skills/spec/SKILL.md.tmpl`: `/spec` skill template
- `docs/specs/spec.md.tmpl`: blank spec template

**Scripts and tooling**
- `scripts/scaffold.py`: project scaffolder — copies `templates/`, substitutes `{{project_name}}`, `{{project_slug}}`, `{{date}}`, initializes git, optionally clones `less_tokens`
- `Makefile`: factory-level workflow substrate — `scaffold`, `validate-hooks`, `spec`, `test`, `lint`, `fmt`, `help`

**Factory domain rules** (`.agents/` — applies to the factory repo itself)
- `.agents/backend.md`, `frontend.md`, `testing.md`, `security.md`

**Factory skill**
- `.claude/skills/spec/SKILL.md`: `/spec` — guided PRD generation with plan mode gate, Explore + Plan subagents, approval before any file write

**Settings**
- `.claude/settings.json` baseline (allow-only): `Bash(git status)`, `Bash(make*)`, `Read(**)` — deny list deferred to backlog (C4)
- `.gitignore`: excludes `less_tokens/` (installed tooling managed separately from factory git history)

[Unreleased]: https://github.com/hofmockel/flying_buttress/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/hofmockel/flying_buttress/releases/tag/v0.1.0
