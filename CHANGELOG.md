# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `settings.json` baseline (allow-only): `Bash(git status)`, `Bash(make*)`, `Read(**)` — factory repo and scaffolded-project template; deny list deferred to backlog (C4)
- `ADR-001` accepted: v1 MVP scope locked — 8 deliverables in sequence, `/spec` end-to-end as the acceptance test
- `CHANGELOG.md`: this file; tracks all notable changes from here forward
- Factory development workflow (`plan.md` §10): sibling-repo testing pattern, less_tokens integration as a nested utility layer, scaffold-and-carry-back loop as the factory's test discipline
- `review_plan.md`: multi-perspective review lattice — ten review kinds (spec, correctness, architecture, security, schema, rules, docs, perf, human, post-merge) and the five mechanisms that execute them (rules, skills, hooks, subagents, GitHub Actions)
- `buttress.md`: manifesto defining the flying_buttress software-factory concept and its tool-agnostic spec
- `plan.md`: operating manual mapping the factory lifecycle onto Claude Code primitives (build environment, workflow, guardrails, governance, scaffolding menu)
- Exploratory source notes: `Core Components of a Modern "Super-Repo".md`, `Repo layout.md`, `claude-features.md`
- `.gitignore`: excludes `less_tokens/` (installed tooling managed separately from factory git history)

[Unreleased]: https://github.com/hofmockel/flying_buttress/compare/HEAD...HEAD
