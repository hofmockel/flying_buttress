# Security rules

## Hard rules — never violate
- No secrets in code, commits, or logs — ever; use environment variables or a secrets manager
- No `eval()` or equivalent dynamic code execution on user-supplied input
- No SQL string interpolation — always use parameterized queries or an ORM's query builder
- No `innerHTML` assignment with user-supplied content — use `textContent` or a sanitizer
- All file paths derived from user input must be validated against an allowlist before use

## Every PR checklist
Before opening a PR that touches user-facing code, auth, or data access, check:

- [ ] Are all inputs validated and sanitized at the system boundary?
- [ ] Are error messages safe to show users? (No stack traces, internal paths, or raw DB errors.)
- [ ] Does this change touch authentication or authorization? If yes, flag for senior review before merge.
- [ ] Are new dependencies pinned to a specific version and justified in the PR description?

## Dependency policy
- New runtime dependencies require a one-sentence justification in the PR description
- Run `pip-audit` (Python) or `npm audit` (Node) before merging any dependency addition or upgrade
- Prefer packages with a track record; avoid packages last updated more than two years ago

## Incident rule
If a secret is accidentally committed: rotate it immediately, then clean the git history. Rotation first — always.
