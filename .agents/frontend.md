# Frontend rules

## Boundaries
- No inline styles; use the project's design token system
- No direct DOM manipulation outside of framework primitives
- All user inputs validated before submission, not only on error return
- Every interactive element has a keyboard equivalent and an ARIA label where the visual label isn't sufficient

## Naming
- Components: `PascalCase`
- Files: `kebab-case.tsx`
- Event handlers: `on` + PascalCase verb (`onClick`, `onSubmit`, `onFilterChange`)
- Props interfaces: component name + `Props` (`ButtonProps`, `UserCardProps`)

## State
- Prefer local component state; lift only when a sibling component genuinely needs the same value
- No client-side state for data that belongs on the server (user roles, feature flags, pricing)
- Derived values are computed, not stored: if you can calculate it from existing state, don't add another state variable

## Structure
- One component per file; co-locate tests and stories in the same directory
- Keep components under ~150 lines; extract sub-components rather than growing one file
- Data fetching lives at the route or page level, not inside leaf components
