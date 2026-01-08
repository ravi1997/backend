# Web Conventions

## File Structure
- `src/`: Application source.
    - `components/`: Reusable UI components.
    - `pages/` or `app/` (Next.js): Routes.
    - `hooks/`: Custom React hooks.
    - `utils/` or `lib/`: Helper functions.
    - `styles/`: CSS/SCSS modules.
- `public/`: Static assets (images, fonts).

## Naming
- **Components**: PascalCase (e.g., `Button.tsx`).
- **Hooks**: `use` prefix + camelCase (e.g., `useAuth.ts`).
- **Utilities**: camelCase (e.g., `formatDate.ts`).
- **CSS Classes**: BEM or Utility-first (Tailwind).

## Code Style
- Use TypeScript for type safety.
- Functional components over class components (React).
- atomic design or feature-based folder structure.
