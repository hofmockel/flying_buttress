# Onboarding

Five steps from "I just cloned this" to "I have a PR open."

---

## Step 1 — Understand the factory (30 min, one-time)

Read [buttress.md](buttress.md) in full. Then read [plan.md](plan.md) §1–§3 and §9.

Goal: know what flying_buttress is, what the four pillars are, and how the lifecycle maps to Claude Code. Skip the rest of `plan.md` for now.

---

## Step 2 — Understand the current work queue (10 min)

Read [backlog.md](backlog.md). Then read [docs/adr/README.md](docs/adr/README.md) and skim each open ADR.

Goal: know what's being built, what's already decided, and what's still proposed.

---

## Step 3 — Pick up a task (5 min)

Find the lowest-numbered ADR in `docs/adr/README.md` with status **Proposed**. That is the next thing to build. If someone else is already on it, take the next one.

If all ADRs are Accepted and you're unsure what's left, ask the senior.

---

## Step 4 — Set up your environment

1. Clone the repo (you've done this).
2. Install [Claude Code CLI](https://claude.ai/code) if not already installed.
3. Run `claude` from the repo root and confirm it loads `CLAUDE.md`.
4. Run `make validate-hooks` — all checks should pass green.

_This section grows as the factory gains new tooling. If a step is broken, update it in your first PR._

---

## Step 5 — Open your first PR

Implement the deliverable from the ADR you picked. Open a PR with:

- A one-line title naming the ADR (e.g., `ADR-004: add tier-1 smoke checklist to Makefile`).
- A one-paragraph description: what changed and why.
- The smoke checklist from `make validate-hooks` checked off.
- If you carried back an improvement from a test project: a transcript excerpt or output artifact as evidence.

Self-merge after 48 hours if there is no blocking comment. The senior reviews at the weekly sync (Mondays).

---

## Maintenance rule

Update this file whenever Step 4 gains a new required tool or the ADR sequence changes. It goes stale fast — keep it honest.
