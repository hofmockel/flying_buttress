# ADR-006: Settings Governance

**Status:** Accepted  
**Date:** 2026-05-15  
**Deciders:** Senior dev  
**Fixes:** G6 — Permission model coarse and its governance absent  

---

## Context

`plan.md` §7.6 makes the right call: `.claude/settings.json` is committed to the repo as policy-as-code. But it does not answer who can change the policy, what review is required, and how local overrides are handled. For a team where juniors own their pieces and self-merge after 48h, a junior could unilaterally change the permission model that governs the whole team.

Three files are in scope: `.claude/settings.json` (project policy), `~/.claude/settings.json` (user policy), and `.claude/settings.local.json` (local overrides).

---

## Decision

### File-by-file rules

**`.claude/settings.json` — project policy**  
- Committed to the repo. Affects every developer.
- Changes require **explicit senior approval** before merge. Not subject to the 48h self-merge rule.
- A header comment in the file names the owner and links to this ADR:

```jsonc
// Owner: senior dev. Changes require senior approval before merge. See docs/adr/ADR-006.
{
  ...
}
```

**`~/.claude/settings.json` — user policy**  
- Lives on the developer's machine. Never committed. Never shared.
- Unrestricted. Developers manage their own personal preferences.

**`.claude/settings.local.json` — local overrides**  
- In `.gitignore`. Never committed.
- Unrestricted. Used for temporary personal overrides (e.g., switching models for an experiment).
- Rule: if you find yourself keeping a local override for more than a week, it probably belongs in a PR against the project settings — or it's a personal preference that belongs in `~/.claude/settings.json`.

### What requires a settings PR

Any of these triggers a required PR with senior approval:

- Adding or removing a permission (`allow` or `deny`)
- Adding, modifying, or removing a hook entry
- Changing the default model or env vars
- Changing the `mcpServers` block

### What does NOT require a settings PR

- Adding to `settings.local.json` (not committed)
- Changing personal `~/.claude/settings.json`

### Review checklist for settings PRs

Senior uses this checklist when reviewing:

```
- [ ] Is this the most targeted change possible? (Prefer scoped allows over broad ones.)
- [ ] Does a new deny rule risk blocking legitimate team operations?
- [ ] Does a new allow rule introduce a security surface?
- [ ] Is the change documented with a comment in the file?
```

---

## Consequences

**Good:**
- Juniors cannot accidentally change team-wide policy without the senior seeing it.
- The local override escape hatch means juniors aren't blocked on personal preferences.
- The header comment makes ownership discoverable without reading this ADR.

**Risks:**
- If the senior is unavailable for more than 48h, a settings PR will block. Mitigated by: the senior should aim to review settings PRs within 24h, even async. If truly unavailable (vacation, etc.), designate a backup reviewer.
- The boundary between "this should be project policy" vs. "this is a personal preference" will be ambiguous at first. The one-week local override rule gives a heuristic.
