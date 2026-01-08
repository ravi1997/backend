# Frontend Conventions (React/Tailwind)

## Structure
- `src/components/` reusable UI components
- `src/pages/` route-level pages
- `src/lib/` helpers (api client, utils)
- `src/styles/` tokens and globals

## Tailwind
- Prefer utility classes and shared component wrappers
- Use consistent spacing scale
- Ensure focus-visible outlines for accessibility

## Data fetching
- Centralize API client
- Handle loading/error states consistently

## Logging
- Never log PHI/PII to console in production
