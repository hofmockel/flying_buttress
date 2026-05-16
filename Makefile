# flying_buttress Makefile
# Durable substrate for factory operations. Skills call make; make is the underlay.
# See docs/adr/ADR-005-makefile-underlay.md and docs/adr/ADR-001-v1-mvp-scope.md
#
# Owner: senior dev. Changes here require the same review as settings.json (ADR-006).

.PHONY: help spec test lint fmt validate-hooks scaffold

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
	@echo "No test suite configured yet. Add your test command here."

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
