# Backend rules

## Boundaries
- All external calls go through explicitly defined interfaces — no ad-hoc HTTP calls scattered in business logic
- Database access is always parameterized; no string interpolation in queries
- Secrets are never hardcoded; read from environment variables only
- API responses have typed contracts (Pydantic, Zod, or equivalent); no untyped dicts returned across boundaries

## Naming
- Python files: `snake_case.py`; TypeScript files: `kebab-case.ts`
- Functions: verb_noun pattern (`get_user`, `create_session`, `validate_token`)
- Constants: `UPPER_SNAKE_CASE`
- Avoid abbreviations in names visible across module boundaries

## Error handling
- Fail fast at system boundaries (user input, external APIs, file I/O)
- Trust internal framework guarantees; don't add defensive code for states the type system rules out
- Errors are logged with enough context to reproduce: request ID, user ID, operation name, inputs (redacted if sensitive)
- Never surface internal stack traces or file paths to API callers

## Structure
- One responsibility per module; if a file needs to import from more than three sibling files, it's doing too much
- Put business logic in plain functions, not buried in framework callbacks
- Configuration is injected, not imported globally
