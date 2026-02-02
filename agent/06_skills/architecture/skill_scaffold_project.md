# Skill: Scaffold New Project

**Role**: Software Architect  
**Output**: Initial project structure  
**Complexity**: High

---

## Strategy

1. **Verify Requirements**: Confirm stack, scope, and naming.
2. **Select Tooling**: Use standard CLI tools (npx, pip, cargo, flutter) preferably.
3. **Execute Scaffold**: Run command to generate structure.
4. **Clean**: Remove default "Hello World" boilerplate if requested.
5. **Enrich**: Add Agent OS files (Docs, .github, Dockerfile).

---

## Stack-Specific Commands

### Next.js

```bash
npx create-next-app@latest ./ --typescript --eslint --tailwind --no-src-dir
```

### React (Vite)

```bash
npm create vite@latest ./ -- --template react-ts
```

### Node.js (Express)

- Manual creation: `package.json`, `src/index.ts`, `tsconfig.json`.
- Or generator if available.

### Python (uv/FastAPI)

```bash
uv init
# Create main.py, requirements.txt
```

### Python (Flask)

- Manual creation: `app.py`, `requirements.txt` (flask).

### Java (Spring Boot)

- Use `curl` to `start.spring.io` or `mvn archetype`.

### Flutter

```bash
flutter create . --org com.example
```

### C++

- Create `CMakeLists.txt`, `src/main.cpp`, `include/`.

---

## Agent OS Enrichment

After basic scaffolding, ALWAYS add:

1. **`README.md`**: With "How to Run", "Stack Info".
2. **`.gitignore`**: Stack specific + general.
3. **`Dockerfile`**: From `skill_dockerize`.
4. **`.github/workflows/ci.yml`**: From `skill_generate_github_actions`.
5. **`docs/` folder**: With `SRS.md`, `ARCHITECTURE.md` stubs.

---

## Post-Scaffold Checks

- [ ] Build runs successfully
- [ ] Tests run (if included)
- [ ] Linter is configured
- [ ] Git repo initialized (`git init`)

---

## Outputs

- A runnable "Hello World" project matching the requested stack
- Fully configured Agent OS environment (Docker, CI, Docs)
