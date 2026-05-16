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
- The **Tier 1 smoke checklist** below, checked off in the PR description.
- If you carried back an improvement from a test project: a transcript excerpt or output artifact as evidence (required — see Tier 3 below).
- If Step 4 above gained a new required tool or the ADR sequence changed: update this file in the same PR.

### Tier 1 PR smoke checklist (ADR-004)

Copy this into every PR that touches a skill, hook, or `settings.json`. Check each item before opening the PR.

```
- [ ] Opened Claude Code from the repo root with no errors
- [ ] CLAUDE.md loads and routes correctly (asked Claude "what is this repo?" and got a correct answer)
- [ ] If a skill changed: ran the skill on a toy input and got the expected output shape
- [ ] If settings.json changed: confirmed Claude Code started without permission errors
- [ ] ONBOARDING.md is still accurate — no steps are broken by this change
- [ ] make validate-hooks passes all automated checks
```

The `make validate-hooks` target covers the automated subset (file existence, valid JSON). The items above it require a live Claude Code session — run them manually.

**Carry-back evidence (Tier 3):** if your PR includes an improvement carried back from a sibling project, attach a transcript excerpt, output artifact, or screenshot. "I tested it and it works" with no artifact is not acceptable.

Self-merge after 48 hours if there is no blocking comment. The senior reviews at the weekly sync (Mondays).

---

## Maintenance rule

Update this file whenever Step 4 gains a new required tool or the ADR sequence changes. It goes stale fast — keep it honest.
