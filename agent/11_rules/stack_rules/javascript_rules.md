# Rules: JavaScript & TypeScript Core

**Scope**: General language usage across Frontend and Backend.

## 1. Syntax & Modern Standards

- **ES6+**: Use `const` and `let`. No `var`.
- **Arrow Functions**: Preferred for callbacks and non-method functions.
- **Destructuring**: Use object/array destructuring for cleaner parameter access.
- **Template Literals**: Use backticks for string interpolation.

## 2. TypeScript (Preferred)

- **Strict Mode**: `strict: true` in `tsconfig.json`.
- **Any**: Avoid `any`. Use `unknown` or specific types/interfaces.
- **Interfaces**: Prefer `interface` over `type` for object shapes.

## 3. Asynchronous Patterns

- **Async/Await**: Preferred over raw `.then()` chains.
- **Error Handling**: Always use `try/catch` with async/await.
- **Parallelism**: Use `Promise.all()` for independent concurrent tasks.

## 4. Code Hygiene

- **Equality**: Always use `===` and `!==`.
- **Semicolons**: Consistent usage (follow project Prettier).
- **Naming**: `camelCase` for vars/functions, `PascalCase` for classes/types.

## 5. Functional Patterns

- **Immutability**: Prefer creating new objects/arrays over mutation (e.g., `map`, `filter`, `reduce`).
- **Pure Functions**: Aim for deterministic functions without side effects where possible.
