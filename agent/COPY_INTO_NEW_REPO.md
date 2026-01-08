# Copy into New Repo

## Quick Setup

### 1) Copy `agent/` folder to repo root

```bash
# Option A: Direct copy
cp -r /path/to/ai-agent-md-pack/agent /path/to/your/project/

# Option B: Clone then copy
git clone <template-repo-url>
cp -r ai-agent-md-pack/ai /path/to/your/project/
cd /path/to/your/project/

# Verify
ls -la agent/
# Should see: 00_INDEX.md, 00_SYSTEM.md, 01_PROJECT_CONTEXT.md, etc.
```

### 2) Fill `agent/01_PROJECT_CONTEXT.md`

Open the file and edit the `AUTO_CONTEXT` YAML block:

```yaml
app_name: "your-app-name"        # REQUIRED
env: "dev"                        # REQUIRED: dev|staging|production
domain: "localhost"               # Optional
repo_root: "."                    # Optional - usually "."
backend_dir: ""                   # Optional - agent will detect
# ... fill what you know, leave rest blank
```

**Minimum required fields:**
- `app_name` - Your application name
- `env` - Current environment (dev/staging/production)

**Everything else is optional** - the autofill system will infer from your project structure.

### 3) Add link in your README

Add this section to your project's `README.md`:

```markdown
## AI Agent Setup

This project uses AI agent configuration for automated development, testing, and maintenance.

**Agent docs:** [`agent/00_INDEX.md`](00_INDEX.md)

**Quick commands:** [`agent/QUICK_REFERENCE.md`](QUICK_REFERENCE.md)
```

### 4) Start working

Follow [`agent/QUICKSTART.md`](QUICKSTART.md) to begin using AI agents.

---

## Verification Steps

After copying, verify the setup:

### ✅ Check 1: Files exist
```bash
ls agent/00_INDEX.md agent/00_SYSTEM.md agent/01_PROJECT_CONTEXT.md
# Should show all three files
```

### ✅ Check 2: Context is filled
```bash
grep "app_name:" agent/01_PROJECT_CONTEXT.md
# Should show your app name, not empty string
```

### ✅ Check 3: Directory structure
```bash
ls agent/
# Should see: workflows/, checklists/, policy/, forms/, artifacts/, skills/, profiles/, etc.
```

### ✅ Check 4: Test with agent
Give your AI agent this command:
```
"Read agent/00_INDEX.md and tell me what workflows are available"
```

Agent should respond with a list of workflows.

---

## Common Pitfalls & Solutions

### ❌ Pitfall 1: Copied to wrong location
**Problem:** `agent/` folder is in subdirectory, not root

**Solution:**
```bash
# Move to root
mv some/subdirectory/ai ./
```

**Verify:** `ls agent/00_INDEX.md` should work from project root

---

### ❌ Pitfall 2: Didn't fill PROJECT_CONTEXT
**Problem:** Agent asks too many questions

**Solution:**
- Open `agent/01_PROJECT_CONTEXT.md`
- Fill at minimum: `app_name` and `env`
- Fill more fields if you know them

---

### ❌ Pitfall 3: Wrong environment setting
**Problem:** Production safety blocking dev actions

**Solution:**
- Check `env:` in `01_PROJECT_CONTEXT.md`
- Should be `"dev"` or `"staging"` for development
- Use `"production"` only for production environments

---

### ❌ Pitfall 4: Agent not reading files
**Problem:** Agent doesn't seem to know about workflows

**Solution:**
- Explicitly tell agent: "Read agent/00_INDEX.md"
- Check that files weren't corrupted during copy
- Verify file permissions: `chmod -R u+r agent/`

---

### ❌ Pitfall 5: Autofill not working
**Problem:** Agent can't infer project structure

**Solution:**
- Ensure standard project layout (see `autofill/PATH_AND_SERVICE_INFERENCE.md`)
- Fill more fields manually in `01_PROJECT_CONTEXT.md`
- Check that you have `pyproject.toml`, `requirements.txt`, or `package.json`

---

## Customization

After copying, you may want to customize:

### Project-specific conventions
Edit [`agent/02_CONVENTIONS.md`](02_CONVENTIONS.md):
- Code style preferences
- Git commit format
- Security rules specific to your domain

### Default behaviors
Edit [`agent/02_CONVENTIONS.md`](02_CONVENTIONS.md):
- Preferred testing framework
- Linting tools
- Database migration approach

### Custom workflows
Add new workflows to [`agent/workflows/`](workflows/):
1. Create `workflows/your_workflow.md`
2. Follow existing template structure
3. Add reference to `REFERENCE_MAP.md`

---

## Next Steps

1. ✅ Verify setup (see above)
2. 📖 Read [`QUICKSTART.md`](QUICKSTART.md)
3. 🎯 Give agent first task (see [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md))
4. 🔧 Customize conventions (see [`02_CONVENTIONS.md`](02_CONVENTIONS.md))

---

**Ready?** → Start with [`QUICKSTART.md`](QUICKSTART.md)
