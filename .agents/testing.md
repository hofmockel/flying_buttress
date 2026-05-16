# Testing rules

## Requirements
- Every bug fix includes a failing test that reproduces the bug before the fix is applied — no exceptions
- Tests live next to the code they test, not in a separate top-level `tests/` directory
- No mocking the database in integration tests; use a real test database (seeded, torn down after each run)
- Test names describe observable behavior, not implementation: `test_login_fails_with_wrong_password`, not `test_auth_method_returns_false`

## What to test
- **Happy path** — does it work when inputs are valid?
- **Boundary** — what happens at the edge of the valid input range?
- **Expected failure** — what happens when the system encounters a known error state?
- **Integration** — does the component work correctly with its real dependencies (DB, external API stub)?

## What not to test
- Framework internals (routing, ORM hydration, component rendering lifecycle)
- Implementation details that don't affect observable behavior
- Things the type system already rules out

## CI requirement
- Every PR must pass the full test suite before merge
- Flaky tests are treated as bugs: fix or delete, never skip
- Test runtime should stay under 2 minutes for the unit suite; flag anything slower
