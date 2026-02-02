# Rules: React

**Scope**: Frontend React Components and Hooks.

## 1. Component Structure

- **Functional**: Use Functional Components with Hooks. No Class Components (unless legacy).
- **PascalCase**: Filenames and Component names.
- **Props**: Define strict prop types (TypeScript Interfaces).

## 2. Hooks Rules

- **Top Level**: Only call hooks at the top level of the component.
- **Dependencies**: Exhaustive dependency arrays for `useEffect` and `useCallback`.
- **Custom Hooks**: Prefix with `use`.

## 3. State Management

- **Local**: Use `useState` for simple UI state.
- **Global**: Use Context or Redux/Zustand only when necessary.
- **Immutability**: Never mutate state directly. Use setters.

## 4. Performance

- **Memoization**: Use `useMemo` and `useCallback` for expensive calculations or reference stability.
- **Lazy Loading**: Use `React.lazy` and `Suspense` for large routes.

## 5. OSX/JSX

- **Semantics**: Use semantic HTML tags.
- **Fragments**: Use `<>` or `<React.Fragment>` to avoid extra DIVs.
- **Keys**: Unique and stable keys for lists (no array indices if order changes).
