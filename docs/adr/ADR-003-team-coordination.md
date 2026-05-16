# ADR-003: Team Coordination Model

**Status:** Accepted  
**Date:** 2026-05-15  
**Deciders:** Senior dev  
**Fixes:** G2 — No team coordination model  

---

## Context

The team is 1 senior + 1–2 junior developers. The stated model: juniors own their pieces, senior does periodic audits. The stated cadence: weekly sync where senior reviews what landed since last week.

`plan.md` §10.4 describes the scaffold-and-carry-back loop as a single-developer discipline. Under a small group, this produces divergence: juniors discover different factory improvements in different test projects, and without a coordination mechanism, conflicts go unresolved and the factory drifts.

Three questions need answers: how do changes get reviewed, how does carry-back work, and who can touch what.

---

## Decision

### PR and merge process

- Juniors open PRs for every factory change. No direct commits to `main`.
- PRs self-merge after **48 hours** if there is no blocking comment from the senior.
- The senior reviews all merged PRs at the **weekly sync** (Mondays, or nearest working day). Anything that needs fixing gets a new issue opened immediately.
- Exception: changes to `.claude/settings.json` or `.agents/*.md` require explicit senior approval before merge (not subject to the 48h rule). See ADR-006.

### Weekly sync agenda (timebox: 30 min)

1. Senior reads all PRs merged since last sync. (5 min, async before the meeting.)
2. Team discusses anything the senior flagged. (10 min.)
3. Team reviews the `docs/adr/README.md` status column together — any ADR to advance from Proposed → Accepted? (10 min.)
4. Carry-back items from test projects: any improvements observed this week? Who writes the PR? (5 min.)

### Carry-back rules

When an improvement is observed in a sibling test project and is worth bringing back to flying_buttress:

1. The person who observed it opens the PR against flying_buttress, not the test project.
2. The PR description must include: what changed, why it's an improvement, and evidence it works (transcript excerpt, output artifact, or screenshot).
3. If the improvement conflicts with another junior's in-progress work, flag it at the weekly sync before merging — don't resolve it unilaterally.

### Ownership map

| Artifact | Owner | Approval required to merge |
|---|---|---|
| `ONBOARDING.md` | Junior (rotating) | 48h self-merge |
| `CLAUDE.md` (root) | Junior | 48h self-merge |
| `.agents/*.md` | Senior | Senior approval |
| `.claude/settings.json` | Senior | Senior approval |
| Skills under `.claude/skills/` | Junior (assigned per ADR) | 48h self-merge |
| `docs/adr/` files | Whoever writes the ADR | Senior approval to advance status to Accepted |
| `backlog.md` | Anyone | 48h self-merge |

### Memory

Memory files live at `~/.claude/projects/<repo>/memory/` — per-machine, not committed. They are not shared across developers. The only shared persistent state is what's in the repo.

Implication: don't put decisions in memory that the team needs to share. Those go in ADRs or `backlog.md`.

---

## Consequences

**Good:**
- Juniors move at their own pace without being blocked on senior availability.
- Senior's weekly sync is bounded (30 min) and not a bottleneck.
- The 48h window gives the senior a real veto without requiring synchronous review.
- Carry-back evidence requirement prevents "I think this is better" improvements without proof.

**Risks:**
- Two juniors could open conflicting PRs that both self-merge before the weekly sync catches it. Mitigated by: both working from the ADR queue (which is sequential), and the weekly sync as the reconciliation point.
- The weekly sync will be skipped under deadline pressure. Mitigated by: nothing. This is a team discipline issue, not a process issue. Name it explicitly.
