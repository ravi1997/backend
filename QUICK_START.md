# AI Agent MD Pack - Quick Start

**Get started in 5 minutes for existing projects, 10 minutes for new projects.**

---

## Existing Project (5 minutes)

### 1. Copy AI Folder
```bash
cp -r /path/to/ai-agent-md-pack/agent /path/to/your/project/
```

### 2. Fill Context (2 required fields)
Edit `agent/01_PROJECT_CONTEXT.md`:
```yaml
app_name: "your-app-name"
env: "dev"  # or staging, production
```

### 3. Use It
Tell your AI agent:
```
"Read agent/00_INDEX.md and fix this error: [paste error]"
```

**Done!** Everything else auto-detects.

---

## New Project (10 minutes)

### 1. Create Project
```bash
mkdir my-project && cd my-project
git init
```

### 2. Copy AI Folder
```bash
cp -r /path/to/ai-agent-md-pack/agent ./
```

### 3. Choose Stack & Let AI Build
```bash
# Python/Flask
"Read agent/00_INDEX.md and set up Flask project with auth and Docker"

# React/Vite
"Read agent/00_INDEX.md and set up React project with Tailwind"

# Any other
"Read agent/00_INDEX.md and set up [your stack]"
```

**Done!** AI handles the rest.

---

## Common Commands

```
"Read agent/00_INDEX.md and implement: [feature]"
"Read agent/00_INDEX.md and debug: [error]"
"Read agent/00_INDEX.md and deploy to staging"
```

---

**Full Guide:** See `GETTING_STARTED.md`  
**Documentation:** See `agent/README.md`
