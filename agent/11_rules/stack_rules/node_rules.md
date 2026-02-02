# Rules: Node.js Backend

**Scope**: Server-side JavaScript/TypeScript.

## 1. Runtime & Environment

- **LTS**: Use Active LTS Node.js versions (e.g., 18.x, 20.x).
- **Process**: Handle `process.on('unhandledRejection')` and `process.on('uncaughtException')`.
- **Env Vars**: Access configuration via `process.env`. Validate presence at startup.

## 2. Modules & Imports

- **Format**: ES Modules (`import/export`) preferred over CommonJS (`require`).
- **Paths**: Use relative paths or configured aliases. No absolute system paths.

## 3. Performance

- **Blocking**: NEVER block the Event Loop. Use async I/O methods (`fs.promises`, `async/await`).
- **Streams**: Use Streams for large file processing.

## 4. Security (Backend)

- **FS**: Be cautious with file system access using user input.
- **Child Process**: Avoid `exec` with user input. Use `spawn` or `execFile`.
- **Logs**: Do not log sensitive data (tokens, PII).

## 5. API Patterns

- **REST**: Follow standard HTTP verbs and status codes.
- **Validation**: Validate all incoming request bodies (e.g., using Joi/Zod).
