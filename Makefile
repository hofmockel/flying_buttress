# flying_buttress Makefile
# Durable substrate for factory operations. Skills call make; make is the underlay.
# See docs/adr/ADR-005-makefile-underlay.md and docs/adr/ADR-001-v1-mvp-scope.md
#
# Owner: senior dev. Changes here require the same review as settings.json (ADR-006).

.PHONY: help spec test lint fmt validate-hooks scaffold promote-queue tool-registry scaffold-tool

help:
	@echo "flying_buttress factory targets:"
	@echo ""
	@echo "  make spec                     open spec template (or run /spec in Claude)"
	@echo "  make spec SLUG=my-feature     create docs/specs/my-feature.md from template"
	@echo "  make test                     run the test suite"
	@echo "  make lint                     run the linter"
	@echo "  make fmt                      run the formatter"
	@echo "  make validate-hooks           run tier-1 smoke checklist (ADR-004)"
	@echo "  make scaffold TARGET=<path>   stamp a new sibling project at <path>"

# ── spec ─────────────────────────────────────────────────────────────────────

spec:
	@mkdir -p docs/specs
ifdef SLUG
	@if [ -f docs/specs/$(SLUG).md ]; then \
		echo "Already exists: docs/specs/$(SLUG).md"; \
	else \
		cp templates/docs/specs/spec.md.tmpl docs/specs/$(SLUG).md; \
		sed -i '' \
			's/{{slug}}/$(SLUG)/g; s/{{date}}/$(shell date +%Y-%m-%d)/g' \
			docs/specs/$(SLUG).md; \
		echo "Created: docs/specs/$(SLUG).md"; \
	fi
else
	@echo "Tip: run /spec in Claude Code for the full guided workflow."
	@echo "     Or: make spec SLUG=<feature-slug> to create a blank spec."
endif

# ── quality gates (stubs — fill in as tooling is added) ──────────────────────

test:
	python3 -m pytest tests/ -v

lint:
	@echo "No linter configured yet. Add your lint command here."

fmt:
	@echo "No formatter configured yet. Add your format command here."

# ── validate-hooks (ADR-004 tier-1 smoke checklist) ──────────────────────────

validate-hooks:
	@echo "==> Tier-1 smoke checklist"
	@python3 -c \
		"import json, sys; json.load(open('.claude/settings.json')); print('[✓] settings.json valid JSON')" \
		2>/dev/null || echo "[✗] settings.json missing or invalid"
	@test -f CLAUDE.md       && echo "[✓] CLAUDE.md exists"           || echo "[✗] CLAUDE.md missing"
	@test -f ONBOARDING.md   && echo "[✓] ONBOARDING.md exists"       || echo "[✗] ONBOARDING.md missing"
	@test -f Makefile        && echo "[✓] Makefile exists"             || echo "[✗] Makefile missing"
	@test -d .agents         && echo "[✓] .agents/ exists"             || echo "[✗] .agents/ missing"
	@test -f .agents/backend.md   && echo "[✓] .agents/backend.md"    || echo "[✗] .agents/backend.md missing"
	@test -f .agents/frontend.md  && echo "[✓] .agents/frontend.md"   || echo "[✗] .agents/frontend.md missing"
	@test -f .agents/testing.md   && echo "[✓] .agents/testing.md"    || echo "[✗] .agents/testing.md missing"
	@test -f .agents/security.md  && echo "[✓] .agents/security.md"   || echo "[✗] .agents/security.md missing"
	@test -d .claude/skills/spec  && echo "[✓] /spec skill exists"     || echo "[✗] .claude/skills/spec/ missing"
	@test -d templates            && echo "[✓] templates/ exists"      || echo "[✗] templates/ missing"
	@test -f scripts/scaffold.py  && echo "[✓] scripts/scaffold.py"    || echo "[✗] scripts/scaffold.py missing"
	@python3 -c \
		"import json; json.load(open('.claude/tool_registry.json')); print('[✓] tool_registry.json valid JSON')" \
		2>/dev/null || echo "[✗] tool_registry.json missing or invalid"
	@test -f .claude/hooks/bash-logger.py     && echo "[✓] bash-logger hook exists"     || echo "[ ] bash-logger.py not installed (run make install-hooks)"
	@test -f .claude/hooks/pattern-analyzer.py && echo "[✓] pattern-analyzer hook exists" || echo "[ ] pattern-analyzer.py not installed (run make install-hooks)"
	@test -f .claude/hooks/tool-registry.py   && echo "[✓] tool-registry hook exists"   || echo "[ ] tool-registry.py not installed (run make install-hooks)"
	@python3 -c "\
import json, pathlib; \
log = pathlib.Path('.claude/state/bash-log.jsonl'); \
lines = [l for l in log.read_text().splitlines() if l.strip()] if log.exists() else []; \
[json.loads(l) for l in lines]; \
print(f'[✓] bash-log.jsonl valid ({len(lines)} entries)') \
" 2>/dev/null || echo "[ ] bash-log.jsonl not yet created (ok on fresh install)"
	@echo ""
	@echo "Manual checks (run these yourself):"
	@echo "  [ ] claude starts from repo root with no errors"
	@echo "  [ ] ask Claude 'what is this repo?' — CLAUDE.md should route correctly"
	@echo "  [ ] ONBOARDING.md steps are still accurate"

# ── scaffold ──────────────────────────────────────────────────────────────────

scaffold:
ifndef TARGET
	$(error TARGET is required. Usage: make scaffold TARGET=../my-project)
endif
	@python3 scripts/scaffold.py --target "$(TARGET)"

# ── active learning system ────────────────────────────────────────────────────

promote-queue:
	@if [ -f .claude/promote_queue.md ]; then \
		echo "==> Pending tool promotions:"; \
		grep -c '"status": "pending"' .claude/promote_queue.md 2>/dev/null \
			| xargs -I{} echo "  {} pending"; \
		grep -c '"status": "needs-confirmation"' .claude/promote_queue.md 2>/dev/null \
			| xargs -I{} echo "  {} needs confirmation"; \
		echo ""; \
		cat .claude/promote_queue.md; \
	else \
		echo "No promote queue yet (.claude/promote_queue.md not found)."; \
	fi

tool-registry:
	@if [ -f .claude/tool_registry.json ]; then \
		python3 -c "\
import json; \
entries = json.load(open('.claude/tool_registry.json')); \
print(f'{len(entries)} registered tool(s)'); \
[print(f'  {e[\"skill\"]}/{e[\"name\"]}  —  {e[\"description\"]}') for e in entries] \
"; \
	else \
		echo "No tool registry found (.claude/tool_registry.json not found)."; \
	fi

scaffold-tool:
ifndef SKILL
	$(error SKILL is required. Usage: make scaffold-tool SKILL=<skill-name> NAME=<tool-name>)
endif
ifndef NAME
	$(error NAME is required. Usage: make scaffold-tool SKILL=<skill-name> NAME=<tool-name>)
endif
	@mkdir -p .claude/skills/$(SKILL)/tools
	@TARGET=.claude/skills/$(SKILL)/tools/$(NAME).py; \
	if [ -f $$TARGET ]; then \
		echo "Already exists: $$TARGET"; \
	else \
		printf '#!/usr/bin/env python3\n"""Tool: $(NAME)\n\nSkill: $(SKILL)\nDate: $(shell date +%%Y-%%m-%%d)\n"""\nfrom __future__ import annotations\n\n\ndef $(NAME)() -> None:\n    """TODO: implement."""\n    raise NotImplementedError\n' > $$TARGET; \
		echo "Created: $$TARGET"; \
	fi

