# review_plan.md

> *Reviews are not a single gate. They are a lattice.*

This document specifies the review process for the **flying_buttress** factory: the kinds of reviews that fire, the perspectives they bring, the mechanisms that run them, and how they align with the workflow in `plan.md`.

Companion docs:
- `buttress.md` — the manifesto and tool-agnostic spec
- `plan.md` — the operating manual for Claude Code as the factory floor
- `review_plan.md` (this doc) — the review process detailed

---

## 1. What this document is

`plan.md` §6 names guardrails (hooks, permissions, plan mode, worktrees). `plan.md` §8 names the CI pipeline as a conceptual flow. Neither says *who reviews what, from what perspective, with what mechanism, and at what point in the lifecycle*. This doc does.

A weak review process treats reviews as a single binary gate: "did the PR pass CI?" A strong review process treats reviews as a **lattice** — multiple perspectives, multiple mechanisms, multiple firing moments. The same change is examined for correctness *and* architecture *and* security *and* schema compatibility *and* rules compliance, by tools tuned to each question.

This document is opinionated about the lattice. It defers concrete tool picks (which linter, which test runner, which schema validator) to fork time, the same way `buttress.md` does. It is all-in on Claude Code mechanisms for the human-readable layer of reviews — skills, subagents, hooks — and on GitHub Actions for the asynchronous PR-gated layer.

---

## 2. Review philosophy

### 2.1 Layered defense

The same change is reviewed by **multiple mechanisms** that catch different classes of problem. A failing test catches behavior. A type checker catches contracts. A security scanner catches CVEs. An architecture review catches design drift. A human review catches what no automated system can — *intent*.

No single mechanism is a substitute for the others. The lattice is the point.

### 2.2 Multi-perspective

Each review kind answers a **different question**:

- *Does the spec address the right problem?*
- *Does the change compile, type-check, and pass tests?*
- *Does the change fit the architecture?*
- *Does the change introduce vulnerabilities?*
- *Do the data contracts still hold?*
- *Does the change follow `.agents/*.md` rules?*
- *Are docs and runbooks updated alongside the change?*
- *Does the change regress performance?*
- *Does this actually solve the user's problem?*

A reviewer who tries to answer all of these in one pass answers none of them well. The lattice splits the questions.

### 2.3 Automate broadly, humans at the keystone

Every review kind that *can* be automated should be. Humans review the residue — the things automation cannot judge: intent, taste, long-term design, ethical edges. The factory's job is to drain everything else into hooks, CI, and subagents so the human review is fast, focused, and rare.

### 2.4 Every review produces a named artifact

A review that leaves no trace cannot be audited. The lattice produces artifacts: CI logs, subagent reports, PR comments, ADRs, transcript chapters. Each review kind names its artifact format up front (§3) so the audit trail is consistent.

### 2.5 The review process is itself reviewable

Rules can be wrong. Skills can drift. Hooks can become noise. The lattice has a **meta-review** layer: a periodic audit (via `/schedule`) of which reviews are firing, which are catching real problems, and which are theatre. ADRs document deliberate changes to the process.

---

## 3. The review kinds

Ten review kinds, each answering one question.

| # | Review kind | Question answered | Perspective | Trigger | Primary mechanism | Output artifact |
|---|---|---|---|---|---|---|
| 1 | **Spec** | Is this the right problem? | Product owner | `/spec` invocation | Plan mode + AskUserQuestion | `docs/specs/<slug>.md` |
| 2 | **Correctness** | Does it compile, type, and pass tests? | Compiler | Every commit + PR | GitHub Actions + PostToolUse hooks | CI check |
| 3 | **Architecture** | Does it fit the design? | Architect | `/review` skill + PR | `code-reviewer` subagent + human | PR review comments |
| 4 | **Security** | Does it introduce vulnerabilities? | Adversary | `/security-review` + PR (always) | `security-reviewer-deep` subagent + Semgrep/Trivy CI | Security report |
| 5 | **Schema / contract** | Do data contracts still hold? | Downstream consumer | PR if schemas touched | `schema-checker` subagent + validators in CI | Contract diff report |
| 6 | **Rules compliance** | Does it follow `.agents/*.md`? | Maintainer | PostToolUse hook + PR | `rules-checker` subagent + lint rules | Rule violations report |
| 7 | **Docs** | Are docs updated alongside? | Future reader | PR | `doc-keeper` subagent | Missing-docs warning |
| 8 | **Performance** | Does it regress? | Operator | PR on flagged paths | Benchmark suite in CI | Perf comparison |
| 9 | **Final human** | Does it solve the user's problem? | Stakeholder | After §1–§8 pass | Human via PR review | Merge or request-changes |
| 10 | **Post-merge `/ultrareview`** | What did we miss? | Independent | Weekly via `/schedule`; per-release | `/ultrareview` (cloud, multi-agent) | Review summary |

The most load-bearing review kinds get deeper treatment below.

### 3.1 Spec review (sketch phase)

The cheapest review: does the spec describe the right problem before any code is written? Triggered when `/spec` runs.

The skill enters plan mode, uses Explore to find related code, uses Plan to draft the strategy, surfaces uncertainties via AskUserQuestion, and exits with `ExitPlanMode` only after the user approves. The output — a written spec at `docs/specs/<slug>.md` — is itself a review artifact for later phases.

A spec review failure looks like: "this spec misunderstands the problem; abort and clarify." This is the cheapest possible failure in the lifecycle.

### 3.2 Correctness review (every phase)

The most-automated review. Two firing moments:

- **PostToolUse hooks** (during dev) — on Write/Edit, the formatter runs and the type checker runs on the changed package. Fast feedback in seconds, not minutes.
- **GitHub Actions** (on PR) — the full test suite, linter, type checker, secret scanner. Authoritative; CI checks must be green to merge.

The two layers catch different things. PostToolUse keeps the prototype loop tight; CI is the bar for merge.

### 3.3 Architecture review

Fires both synchronously during `/refactor` (via Plan mode) and asynchronously on PR (via the `code-reviewer` subagent and a human reviewer). The two moments answer slightly different versions of the question: *should we do this?* during planning, *did we do it right?* during PR.

Architecture reviews are the place where the factory's `.agents/*.md` rules cash in. A reviewer (human or subagent) reads the rules, reads the diff, and asks: *does this change respect the constraints written down?*

### 3.4 Security review

The non-negotiable review. Fires on every PR, automatically. Two layers:

- **CI security scanners** — Semgrep, Trivy, secret-detection (gitleaks or equivalent). Catches known patterns and CVE-shaped issues.
- **`security-reviewer-deep` subagent** — runs in an isolated worktree, takes the PR diff as input, reasons about attack surfaces (authn, authz, injection, deserialization, supply chain). Slower; produces a written report.

Security reviews never approve their own bypass. An override requires an ADR.

### 3.5 Schema / contract review

Fires when a PR touches schema files (`/schema/`, `*.proto`, Pydantic/Zod models). The `schema-checker` subagent:

- Diffs the schema against `main`.
- Flags breaking changes (removed fields, narrowed types, renames without migration).
- Verifies that downstream consumers (per the consumer manifest) are not broken.

The CI counterpart runs the validators against fixture data. Both must pass.

### 3.6 Rules compliance review

Fires continuously. PostToolUse hooks run a lightweight rules checker on every save. On PR, the heavier `rules-checker` subagent reads `.agents/*.md` end-to-end and produces a violations report.

Two-layer split because the rules are too rich for a single linter to encode. Pattern-based rules (e.g., "no `eval()` in `backend/`") become lint rules. Semantic rules (e.g., "all API endpoints must call `auth.require_user()` first") become subagent checks.

### 3.7 Docs review

The `doc-keeper` subagent answers a narrow question: *for every behavior change in this PR, is there a corresponding docs update?* Catches:

- A new API endpoint with no entry in the OpenAPI spec.
- A new runbook-shaped failure mode with no runbook.
- A new ADR-worthy decision with no ADR.
- A new feature with no changelog line.

The subagent posts a PR comment listing what's missing. Non-blocking by default; the human reviewer can mark missing docs as an acceptable debt with an ADR.

### 3.8 Performance review

Fires on PRs that touch flagged paths (hot loops, query layers, agent calls). The benchmark suite runs in CI and compares against baseline. A regression beyond a threshold (say, >10% latency increase) blocks merge.

For un-flagged paths, performance review is on-demand: `/review-perf` triggers it explicitly.

### 3.9 Final human review

The keystone. After every automated review passes, a human approver reads the diff, the spec, the test results, and the subagent reports. The human's job is not to redo what automation did — it's to answer the question automation cannot: *does this actually solve the user's problem?*

Human review is rare and fast because the lattice has already filtered the noise.

### 3.10 Post-merge `/ultrareview`

Runs asynchronously after merge — weekly via `/schedule`, or per-release on demand. Spins up multiple specialized cloud agents to re-review the change against the full repo context. Catches integration issues, drift from older code, missed patterns. Output is a review summary that may produce follow-up issues or ADRs.

`/ultrareview` is human-triggered and billed; the factory wires it into `/schedule` but the user controls cadence.

---

## 4. Mechanisms

Five mechanisms, layered:

### 4.1 Rules (`.agents/`)

Rules are the contract reviewers (human and AI) follow. A dedicated `.agents/review.md` encodes the review process itself: which kinds fire, who owns each, what counts as failure.

Example excerpt:

```markdown
# .agents/review.md (excerpt)

## Required reviews per PR
- Correctness (CI)
- Security (CI + subagent)
- Rules compliance (subagent)
- Final human

## Conditionally required
- Architecture: if change crosses module boundaries
- Schema: if /schema/ or models change
- Docs: if behavior changes
- Performance: if change touches flagged paths

## Bypass
- Security failures: ADR required, signed by maintainer
- Other failures: ADR required
```

Other rules files participate:

- `.agents/security.md` — what security review checks for
- `.agents/testing.md` — coverage thresholds, what must be mocked vs. real
- `.agents/backend.md`, `frontend.md` — domain-specific patterns the architecture review enforces
- `.agents/schema.md` — contract evolution rules

### 4.2 Skills

Custom review skills wrap the bundled `/review` and `/security-review` primitives, adding flying_buttress-specific context.

A minimal review skill SKILL.md:

```markdown
---
name: review-architecture
description: Review a PR diff for architectural fit. Loads .agents/*.md, diffs against main, runs code-reviewer subagent, surfaces design concerns. Use when a PR touches more than one module or proposes a new abstraction.
---

# Architecture review
1. Read .agents/*.md to load constraints.
2. Get the diff via Bash(`gh pr diff <num>`).
3. Spawn code-reviewer subagent with the diff + constraints.
4. Post the subagent's summary as a PR comment via gh.
```

Review skills to author (full list in §9.2):

- `/review` — bundled wrapper, used as the default PR review entry point
- `/review-architecture` — focused on design fit
- `/security-review` — bundled wrapper
- `/review-schema` — schema/contract diff
- `/review-docs` — docs presence check
- `/review-perf` — performance benchmark + comparison
- `/review-rules` — `.agents/` compliance check
- `/review-spec` — sanity-check a spec for completeness
- `/ultrareview` — bundled; user-triggered cloud multi-agent

### 4.3 Hooks

Synchronous review gates that fire during development. The session itself catches problems before CI sees them.

- **PreCommit (Stop hook on commit-shaped Bash)** — block commit if lint/type-check fail
- **PostToolUse(Write|Edit)** — auto-format, run type-checker on changed package, run affected tests
- **PostToolUse(Write|Edit) on `/schema/`** — run schema validators immediately
- **PostToolUse(Write|Edit) on `*.py|*.ts`** — run lightweight rules-checker against `.agents/`
- **UserPromptSubmit** — detect intent like "review this PR" and route to the right review skill
- **PreToolUse(Bash) for `git push`** — block push to `main` directly; redirect to PR flow
- **Stop** — at session end, if there are unreviewed local changes, suggest `/review`

Hooks are fast or async. None should add more than ~2s to the interactive loop.

### 4.4 Subagents

Specialized reviewers, each in isolated context so large diffs and tool outputs don't pollute the main session.

Built-in:

- **`code-reviewer`** — general PR review; the default architecture-review backbone

Custom (to be authored):

- **`security-reviewer-deep`** — slow, thorough; operates in a worktree on the PR diff. Models attack surfaces, checks dep changes against CVE feeds, scans for secret patterns and dangerous calls.
- **`schema-checker`** — runs schema diffs, validates against fixture data, checks downstream consumer manifest.
- **`rules-checker`** — reads `.agents/*.md` and the diff; produces a violations report against the semantic rules linters cannot catch.
- **`doc-keeper`** — checks docs presence for every behavior change in the diff. Produces a missing-docs list.
- **`performance-reviewer`** — runs the benchmark suite, compares against baseline, surfaces regressions.
- **`spec-reviewer`** — given a draft spec, checks for completeness against a spec checklist (problem statement, non-goals, surfaces touched, rollback plan).

Subagents return short summaries to the orchestrating skill; raw output stays in their isolated context.

### 4.5 GitHub Actions (CI)

Asynchronous, PR-gated, authoritative. The bar for merge.

Recommended workflow files under `.github/workflows/`:

- **`ci.yml`** — lint, type-check, unit tests, integration tests. Runs on every push and PR.
- **`security.yml`** — Semgrep, Trivy, secret scanning (gitleaks). Runs on every PR; fails on high-severity findings.
- **`schema.yml`** — schema validation against fixtures. Runs on PRs that touch `/schema/`.
- **`docs.yml`** — runs the `doc-keeper` subagent or a static check that links from changelogs to PRs match.
- **`perf.yml`** — benchmarks on flagged paths. Runs on PRs touching paths in `.bench-paths`.
- **`preview.yml`** — preview deploy to Vercel/Fly/Railway/etc. (whatever the deploy target is). Runs on PR.
- **`claude-review.yml`** — invokes Claude Code in CI to run `/review` on the PR and post comments. The agentic layer of PR review, available to PR authors who didn't run it locally.
- **`ultrareview.yml`** — runs `/ultrareview` weekly via `schedule:` cron and on `workflow_dispatch` for ad-hoc runs.

Required checks (cannot merge without): `ci.yml`, `security.yml`, `claude-review.yml` (advisory), plus conditional checks (`schema.yml`, `perf.yml`) when their paths fire.

---

## 5. The review matrix

The dense reference page. Rows are review kinds; columns are mechanisms.

| Review kind | Rules | Skills | Hooks | Subagents | GitHub Actions |
|---|---|---|---|---|---|
| Spec | `.agents/review.md` checklist | `/spec`, `/review-spec` | Plan mode entry | `spec-reviewer` | — |
| Correctness | `.agents/testing.md` | (none specific) | PostToolUse(format, types, tests) | — | `ci.yml` |
| Architecture | `.agents/backend.md`, `frontend.md` | `/review`, `/review-architecture` | (none) | `code-reviewer` | `claude-review.yml` |
| Security | `.agents/security.md` | `/security-review` | PreToolUse(secrets) | `security-reviewer-deep` | `security.yml` |
| Schema | `.agents/schema.md` | `/review-schema` | PostToolUse on `/schema/` | `schema-checker` | `schema.yml` |
| Rules compliance | `.agents/*.md` (all) | `/review-rules` | PostToolUse(lint) | `rules-checker` | (in `ci.yml`) |
| Docs | `.agents/review.md` § docs | `/review-docs` | Stop (suggest changelog) | `doc-keeper` | `docs.yml` |
| Performance | `.agents/perf.md` (if exists) | `/review-perf` | (none — manual) | `performance-reviewer` | `perf.yml` |
| Final human | `.agents/review.md` § human gate | (none — human reviewer) | (none) | (none) | (PR approval gate) |
| Post-merge `/ultrareview` | `.agents/review.md` § ultrareview cadence | `/ultrareview` | (none) | (cloud agents) | `ultrareview.yml` |

The matrix is load-bearing: every cell is either filled with a mechanism or honestly left blank.

---

## 6. Lifecycle alignment

`plan.md` §9 lays out the lifecycle phases. Review kinds slot into each phase as follows.

### 6.1 Sketch phase

**Reviews running:** Spec review only.

The whole phase *is* a review: of whether the right problem has been identified. No code, no CI, no PR yet. Just `/spec`, Plan mode, AskUserQuestion, and a written spec at the end.

### 6.2 Prototype phase

**Reviews running:** Correctness (PostToolUse), Rules compliance (PostToolUse), light Architecture (informal).

Tight inner loop. The factory protects developer flow by keeping reviews fast and local. Heavy reviews (security, schema, perf) do not fire here unless explicitly requested. The bar is *compilable and conformant*, not *production-ready*.

### 6.3 Productionize phase

**Reviews running:** All of §3.2–§3.9.

This is where the lattice fully engages. Every PR runs CI, security, schema (if touched), rules, docs, and perf (if touched). The `/review` skill orchestrates the subagent reviews. A human reviews last.

Worktree isolation is the default for `security-reviewer-deep` and any review touching sensitive paths.

### 6.4 Operate phase

**Reviews running:** Post-merge `/ultrareview`, periodic security re-review, ADR audits, memory consolidation.

Reviews here are about *what was missed*. `/ultrareview` runs weekly. Security re-runs whenever dep CVEs update. ADR audits ensure that "we'll fix this debt next quarter" actually happens. Memory consolidation is itself a review — pruning stale facts that would mislead future reviewers.

---

## 7. Roles and ownership

| Role | Owns |
|---|---|
| **Author** | The PR itself; ensures CI is green; runs `/review` locally before requesting human review |
| **Automated reviewers** | CI workflows + subagents; produce reports, do not approve |
| **Human reviewer** | The keystone judgment; reads diff + reports; approves or requests changes |
| **Maintainer** | Final arbitrator on contested reviews; signs ADRs that bypass reviews |
| **Review-process owner** | Owns `.agents/review.md` and review_plan.md itself; runs meta-review on schedule |

Conflict resolution:

1. Author addresses every automated review failure. Cannot merge with failures.
2. Author addresses every human reviewer comment. Reviewer re-approves or escalates.
3. Stalemate → maintainer arbitrates.
4. Maintainer's call is documented in an ADR if it overrides the lattice.

---

## 8. Failure handling and escape hatches

### 8.1 When a review fails

Automated review failures **block merge**. The author fixes the underlying issue. There is no "force merge" path for CI failures.

Subagent reviews are advisory by default. The author may dismiss a `doc-keeper` warning by adding an ADR documenting the deferred work. They may not dismiss a `security-reviewer-deep` finding without maintainer sign-off and an ADR.

### 8.2 ADR as the escape hatch

When a review fails and the author judges the failure to be wrong or acceptable, the path forward is an ADR:

- A short markdown file at `docs/adr/<id>-<slug>.md`.
- States the failed review, the disagreement, the trade-off accepted, and the maintainer who signed.
- Linked from the PR description.

ADRs accumulate. If multiple ADRs cluster against one rule, the rule changes.

### 8.3 Reviewing the review process

The review process is itself reviewable:

- Quarterly: a meta-review scheduled via `/schedule` audits which reviews fired, which caught real issues, which never caught anything. Theatre reviews are deleted.
- Per-incident: any production incident triggers a backward-looking review: *which review kind should have caught this?* If none, a new kind is proposed (and added to this doc via PR).
- Memory feedback: feedback memories (per the auto-memory system) about review experience tune the rules.

---

## 9. Scaffolding menu

Possibility menu, same posture as `plan.md` §13. No sequencing commitments here.

### 9.1 Rules to write

- `.agents/review.md` — the review meta-rules (which reviews fire, ownership, bypass)
- `.agents/security.md` — security check list
- `.agents/testing.md` — coverage thresholds and mocking rules
- `.agents/schema.md` — contract evolution rules
- `.agents/backend.md`, `frontend.md` — domain-specific architecture rules
- `.agents/perf.md` — performance bars and flagged paths

### 9.2 Skills to author

- `/review` — bundled; the default PR review wrapper
- `/review-architecture` — design-fit review with `code-reviewer` subagent
- `/security-review` — bundled
- `/review-schema` — schema/contract diff
- `/review-docs` — docs presence check
- `/review-perf` — perf benchmark + comparison
- `/review-rules` — `.agents/` compliance check
- `/review-spec` — spec completeness check
- `/ultrareview` — bundled; user-triggered cloud multi-agent review
- `/audit-reviews` — meta: which reviews ran on a PR, which surfaced findings, which were dismissed

### 9.3 Hooks to write

- **PostToolUse(Write|Edit)** — format
- **PostToolUse(Write|Edit)** — type-check changed package
- **PostToolUse(Write|Edit)** — run affected tests
- **PostToolUse(Write|Edit) on `/schema/`** — schema validation
- **PostToolUse(Write|Edit) on source files** — lightweight rules-checker
- **PreToolUse(Bash, `git commit`)** — block commit if lint or type-check fail
- **PreToolUse(Bash, `git push`)** — block direct push to `main`; redirect to PR
- **UserPromptSubmit** — route "review X" intent to appropriate skill
- **PreToolUse(Read, `.env*`)** — block secret-file reads
- **Stop** — suggest `/review` if there are unreviewed changes; suggest changelog if behavior changed

### 9.4 Subagents to define

- **`security-reviewer-deep`** — slow, thorough security in worktree
- **`schema-checker`** — schema diff + contract validation
- **`rules-checker`** — `.agents/*.md` semantic checks
- **`doc-keeper`** — docs presence audit
- **`performance-reviewer`** — benchmark + compare
- **`spec-reviewer`** — spec completeness check
- **`review-auditor`** — runs the quarterly meta-review

### 9.5 GitHub Actions to set up

- **`.github/workflows/ci.yml`** — lint, type-check, tests
- **`.github/workflows/security.yml`** — Semgrep, Trivy, gitleaks
- **`.github/workflows/schema.yml`** — schema validators on PRs touching `/schema/`
- **`.github/workflows/docs.yml`** — docs presence check via `doc-keeper`
- **`.github/workflows/perf.yml`** — benchmarks on flagged paths
- **`.github/workflows/preview.yml`** — preview deploy
- **`.github/workflows/claude-review.yml`** — Claude Code runs `/review` on the PR and posts comments
- **`.github/workflows/ultrareview.yml`** — weekly cron + manual dispatch
- **Branch protection rules** — required checks: `ci`, `security`, plus conditional `schema`/`perf` when paths fire; require human approval

### 9.6 Supporting infrastructure

- **`docs/adr/`** — ADR directory with a template (`0000-template.md`)
- **`.bench-paths`** — file listing paths that trigger performance review
- **`docs/specs/`** — directory for `/spec`-produced specs
- **`docs/runbooks/`** — directory for `/runbook`-produced runbooks
- **CODEOWNERS** — GitHub file routing reviews to the right people

---

## 10. Cross-references

- The four lifecycle phases this review process aligns with: `plan.md` §9
- The CI pipeline this review process implements concretely: `buttress.md` §8
- The three-layer schema governance these reviews enforce: `buttress.md` §7.3
- The guardrails pillar this review process extends: `plan.md` §6
- The workflow skills (`/spec`, `/fix`, `/refactor`) these reviews participate in: `plan.md` §5.2

---

The lattice is the deliverable. Each cell is a deliberate choice about what catches what, when, and how. Reviewers run automatically wherever automation is possible; humans review only the residue.
