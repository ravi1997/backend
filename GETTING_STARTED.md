# Getting Started with AI Agent MD Pack

## For Existing Projects (5 minutes)

### Step 1: Copy the `agent/` folder
```bash
# Navigate to your project
cd /path/to/your/project

# Copy the ai folder
cp -r /path/to/ai-agent-md-pack/agent ./

# Verify
ls -la agent/
# You should see: 00_INDEX.md, 01_PROJECT_CONTEXT.md, workflows/, etc.
```

### Step 2: Fill Project Context (2 minutes)
```bash
# Open the context file
nano agent/01_PROJECT_CONTEXT.md
# or
code agent/01_PROJECT_CONTEXT.md
```

**Fill only these 2 required fields:**
```yaml
app_name: "your-app-name"        # e.g., "my-flask-app"
env: "dev"                        # dev, staging, or production
```

**Everything else is optional** - the system will auto-detect:
- Language and framework
- Build system
- File paths
- Ports and services

### Step 3: Start Using
```bash
# Tell your AI agent:
"Read agent/00_INDEX.md and help me fix this error: [paste error]"

# Or for features:
"Read agent/00_INDEX.md and implement: user authentication"

# Or for deployment:
"Read agent/00_INDEX.md and deploy to staging"
```

**That's it!** The AI agent will:
1. Read your project context
2. Auto-detect your setup
3. Route to the right workflow
4. Execute with safety checks

---

## For New Projects (10 minutes)

### Step 1: Create Project Structure
```bash
# Create project directory
mkdir my-new-project
cd my-new-project

# Initialize git
git init

# Copy AI folder
cp -r /path/to/ai-agent-md-pack/agent ./
```

### Step 2: Choose Your Stack

**Option A: Python/Flask**
```bash
# Create basic structure
mkdir -p app tests
touch app/__init__.py app/routes.py
touch requirements.txt
touch wsgi.py

# Tell AI:
"Read agent/00_INDEX.md and set up a Flask project with:
- User authentication
- Database (PostgreSQL)
- Docker setup"
```

**Option B: React/Vite**
```bash
# Create with Vite
npm create vite@latest . -- --template react

# Copy AI folder
cp -r /path/to/ai-agent-md-pack/agent ./

# Tell AI:
"Read agent/00_INDEX.md and set up:
- Tailwind CSS
- React Router
- API integration"
```

**Option C: Any Other Stack**
```bash
# Create your basic structure
# (whatever your stack needs)

# Copy AI folder
cp -r /path/to/ai-agent-md-pack/agent ./

# Tell AI:
"Read agent/00_INDEX.md and help me set up [your stack]"
```

### Step 3: Fill Project Context
```bash
nano agent/01_PROJECT_CONTEXT.md
```

**Minimal required:**
```yaml
app_name: "my-new-project"
env: "dev"
```

**Optional (AI will detect if you skip):**
```yaml
language: "python"              # Will auto-detect
framework: "flask"              # Will auto-detect
build_system: "pip"             # Will auto-detect
# ... leave rest blank
```

### Step 4: Let AI Build Your Project
```bash
# Tell your AI agent:
"Read agent/00_INDEX.md and:
1. Set up the project structure
2. Create initial files
3. Set up Docker
4. Create README
5. Initialize database"
```

The AI will:
- Follow `workflows/feature_delivery.md`
- Use `skills/project_auto_setup.md`
- Apply quality gates
- Create documentation

---

## Quick Commands

Once set up, use these commands with your AI:

### Development
```
"Read agent/00_INDEX.md and implement feature: [feature name]"
"Read agent/00_INDEX.md and fix this bug: [paste error]"
"Read agent/00_INDEX.md and add tests for [component]"
```

### Debugging
```
"Read agent/00_INDEX.md and debug: 502 error"
"Read agent/00_INDEX.md and fix: Docker won't start"
"Read agent/00_INDEX.md and investigate: slow performance"
```

### Operations
```
"Read agent/00_INDEX.md and deploy to staging"
"Read agent/00_INDEX.md and run database migration"
"Read agent/00_INDEX.md and create rollback plan"
```

---

## What Happens Behind the Scenes

1. **AI reads** `00_INDEX.md` (main router)
2. **AI loads** `01_PROJECT_CONTEXT.md` (your config)
3. **AI auto-fills** missing details from your project
4. **AI routes** to appropriate workflow
5. **AI collects** evidence (if debugging)
6. **AI executes** with safety checks
7. **AI validates** with quality gates
8. **AI outputs** documentation/reports

---

## Supported Project Types

✅ **Languages:** Python, JavaScript, TypeScript, Java, C++, Go, Rust, PHP, Ruby, etc.  
✅ **Frameworks:** Flask, FastAPI, React, Vue, Angular, Spring Boot, Express, Next.js, etc.  
✅ **Build Systems:** pip, npm, Maven, Gradle, Cargo, CMake, Makefile, etc.  
✅ **Databases:** PostgreSQL, MySQL, MongoDB, SQLite, Redis, etc.  
✅ **Deployment:** Docker, Kubernetes, systemd, Serverless, etc.

**Works with ANY project type!**

---

## Troubleshooting

### "AI can't find my files"
→ Check `repo_root` in `01_PROJECT_CONTEXT.md`

### "Wrong workflow selected"
→ Be specific in your request: "Read agent/00_INDEX.md and [specific task]"

### "AI asking too many questions"
→ Fill more fields in `01_PROJECT_CONTEXT.md` (optional but helps)

### "Production safety blocking me"
→ You're in production! Check `agent/policy/ENV_DETECTION.md`

---

## Next Steps

1. ✅ **Copy `agent/` folder** to your project
2. ✅ **Fill 2 required fields** in `01_PROJECT_CONTEXT.md`
3. ✅ **Start using** - just tell AI to "Read agent/00_INDEX.md and..."

**That's it! You're ready to go.**

---

## Learn More

- **Full Documentation:** `agent/README.md`
- **Quick Reference:** `agent/QUICK_REFERENCE.md`
- **All Workflows:** `agent/workflows/README.md`
- **Examples:** `agent/examples/`

---

**Questions?** Check `agent/README.md` or ask your AI agent:
```
"Read agent/00_INDEX.md and explain how to [do something]"
```
