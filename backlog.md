# backlog.md

> Items surfaced by architect review of `plan.md`. Each entry is a gap, concern, or open question that needs resolution before the factory can serve a small team reliably.

---

## Critical gaps

### G1 — No sequencing; §14 is a menu, not a plan
**Problem:** The document explicitly defers sequencing to "scaffolding time." A small group can't parallelize twelve open choices; they'll converge on different parts of the menu and produce an inconsistent factory.
**Recommended action:** Define a concrete v1 MVP cut of ~5 items. Candidate set: CLAUDE.md hierarchy, one PreToolUse hook (block destructive bash), one PostToolUse hook (run tests on save), `/spec` and `/fix` skills, baseline `settings.json`. Ship that and stop.
**Owner:** TBD
**Status:** Open

---

### G2 — No team coordination model
**Problem:** The audience list in §1.3 names "solo builder," "collaborator inheriting it," and "template-cloner." There is no model for *simultaneous* collaboration. Unresolved questions for a small group:
- Who owns factory changes? Does every developer PR to flying_buttress?
- How do memory files stay consistent across developers? (Memory is per-machine, per-project.)
- When two developers scaffold different test projects and discover different factory improvements, who arbitrates what gets carried back?
- How does a skill change get reviewed before becoming the team's shared workflow?

The scaffold-and-carry-back loop (§10.4) is a manual, single-developer discipline. Under a group it will produce divergence within weeks.
**Recommended action:** Add a "team coordination" section to `plan.md` covering: factory ownership, PR process for factory changes, memory sync strategy, and carry-back arbitration.
**Owner:** TBD
**Status:** Open

---

### G3 — No Day 1 onboarding path
**Problem:** A new developer joining has no answer to "what do I do first, second, third?" §1.3 gives reading order, not a setup path. `/scaffold` is aspirational and unimplemented; `less_tokens` requires manual installation. A new team member will spend hours guessing.
**Recommended action:** Add a concrete "Day 1" section with 5 ordered steps. Steps can reference skills not yet built, but the sequence must be stated.
**Owner:** TBD
**Status:** Open

---

### G4 — Test strategy too weak for a team context
**Problem:** "Can we build something real with it?" (§10.4) is a reasonable smell test for a solo engineer. It's not a test strategy for a team. When factory behavior changes — a hook fires differently, a skill produces different artifacts — there's no regression check, no expected-output contract, no way to know if a carry-back broke something. Hook behavior is easy to break silently; this is the highest-risk gap.
**Recommended action:** Define a minimal factory test harness. At minimum: a set of expected hook outcomes for known inputs, and a checklist that must pass before any carry-back lands in flying_buttress.
**Owner:** TBD
**Status:** Closed — ADR-004 accepted 2026-05-16. Three-tier strategy in place: Tier 1 PR smoke checklist active now; Tier 2 integration milestone gates v2 start; Tier 3 carry-back evidence gate active from first carry-back.

---

### G5 — Vendor lock-in deeper than acknowledged; no abstraction layer
**Problem:** §1.2 claims "tool-agnostic for what you build, all-in on Claude Code for how you build it." The Makefile underlay mentioned in §5.1 as "the durable underlay" is never specified. If Claude Code changes pricing, retires a feature, or the team needs an alternative for any period, nothing survives. There's no abstraction layer between factory procedures and Claude Code-specific primitives.
**Recommended action:** Specify the Makefile underlay concretely. Every factory workflow that can be expressed as a Make target should be. Claude Code skills call Make; Make is the durable substrate. Document this explicitly.
**Owner:** TBD
**Status:** Closed — ADR-005 accepted 2026-05-16. Makefile exists with all six required targets. Skill-to-Make constraint documented in plan.md §5.1 and MANUAL.md §11. /spec skill already delegates to `make spec`.

---

### G6 — Permission model is coarse and its governance is absent
**Problem:** The `settings.json` policy-as-code idea is good, but the governance of the policy itself is unspecified. Open questions: Who can change project-level policy? Is a settings change a PR or unilateral? What happens when a developer's local override conflicts with team policy? The plan names the mechanism but not the rules for changing it.
**Recommended action:** Add a short "settings governance" section: who can merge changes to `.claude/settings.json`, what review is required, and how local overrides are handled.
**Owner:** TBD
**Status:** Closed — ADR-006 accepted 2026-05-16. File-by-file rules, PR trigger list, and senior review checklist documented in MANUAL.md §7. `_comment` key in settings.json names the owner and links ADR-006.

---

## Smaller concerns

### C1 — "All integrations through MCP" rule is a convention, not a guardrail
§8.4 states the rule but there's no hook that detects when an agent shells out to an external system without going through MCP. It's enforced by convention only.
**Recommended action:** Name it explicitly as a convention in the document. Optionally: write a PreToolUse hook that audits Bash calls for common external-system patterns (curl, direct DB calls, etc.) and warns.
**Status:** Closed — ADR-007 accepted 2026-05-16. Convention note added to plan.md §8.4; v2 hook flagged as candidate.

---

### C2 — §11 (Agent SDK publishing) is premature noise
For a small team on a first project, this section costs reading time and signals ambition that isn't load-bearing. It should be a footnote or cut entirely from v1 documentation.
**Recommended action:** Move §11 to a `future.md` or collapse it to a two-sentence note at the bottom of §13.
**Status:** Closed — ADR-007 accepted 2026-05-16. plan.md §11 collapsed to a single-paragraph footnote.

---

### C3 — Model selection rubric will drift faster than the document
Model capabilities change faster than docs do. The rubric in §4.4 is stated as settled fact but will be wrong within months.
**Recommended action:** Add a review cadence note to §4.4: "Review this table quarterly against current Anthropic release notes."
**Status:** Closed — ADR-007 accepted 2026-05-16. Quarterly review cadence note added to plan.md §4.4.

---

### C4 — `settings.json` deny list deferred
The deny list was intentionally omitted from the v1 baseline to keep the allow list minimal and reviewable. Candidate deny rules to add once the allow list stabilizes:

```json
"Bash(rm -rf*)",
"Bash(git push --force*)",
"Bash(git reset --hard*)",
"Bash(git clean -f*)",
"Bash(git push --force-with-lease*)",
"Read(.env*)",
"Read(.claude/settings.local.json)"
```

Same candidates apply to `templates/.claude/settings.json.tmpl` (minus the factory-specific `settings.local.json` entry).
**Recommended action:** Add deny list to both files once the team has a session's worth of data on what the allow list covers. Review against G6 governance model before merging.
**Status:** Closed — deny list added to `.claude/settings.json` and `templates/.claude/settings.json.tmpl` on 2026-05-16. Factory-specific `Read(.claude/settings.local.json)` entry included in factory settings only, omitted from template.

---

---

## Carry-back items (from Tier 2 milestone, 2026-05-17)

### CB1 — scaffold.py missing --name/--slug flags
**Problem:** `make scaffold TARGET=<path> --yes` still requires interactive prompts for project name and slug. Piping input works (`printf "name\nslug\n" | python3 ...`) but is not ergonomic or documented. Makes scripted re-scaffolding brittle.
**Recommended action:** Add `--name` and `--slug` flags to `scaffold.py`. When both are present with `--yes`, skip all interactive prompts.
**Status:** Closed — `--name`, `--slug` flags added to `scaffold.py` and wired through `make scaffold` (NAME/SLUG/YES=1). 11 tests added in `tests/unit/test_scaffold.py`. 2026-05-17.

---

## Overall verdict

The plan is a **strong solo-architect document** that needs to become a **team operating document**. The four-pillar structure is coherent. The v1/v2/speculative bucketing is mature. The policy-as-code and context-discipline sections are above average.

What it lacks for a small group: a forced ordering decision (G1), a team coordination model (G2), a concrete onboarding path (G3), and a minimal factory test harness (G4). Without those, three developers will diverge by week two.

**Single highest-leverage next step:** Call a one-hour meeting and force-rank the §14 menu into a v1 scope of five items. Write that decision into a first ADR. The plan is sophisticated enough — it needs a committed starting point.
