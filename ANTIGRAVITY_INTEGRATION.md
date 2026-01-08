# Antigravity Integration Guide

**Make Antigravity automatically use the AI Agent MD Pack**

---

## How Antigravity Auto-Detection Works

Antigravity looks for these indicators in your project:
1. **`agent/` directory** (standard location)
2. **`agent/` directory** with `00_INDEX.md` (this pack)
3. **Custom instructions** in project root

---

## Option 1: Standard Integration (Recommended)

### Step 1: Use Standard Directory Name
```bash
# Rename 'ai' to 'agent' (Antigravity's standard)
mv ai agent

# Or create symlink
ln -s ai agent
```

### Step 2: Antigravity Will Auto-Detect
When Antigravity sees `agent/` directory, it will:
1. Read `agent/00_SYSTEM.md` for agent instructions
2. Use `agent/00_INDEX.md` as router
3. Load `agent/01_PROJECT_CONTEXT.md` for config
4. Follow all workflows automatically

**No additional configuration needed!**

---

## Option 2: Keep 'agent/' Directory Name

If you prefer to keep the `agent/` name:

### Create `agent/` Pointer
```bash
# Create agent directory
mkdir -p agent

# Create pointer file
cat > agent/README.md << 'EOF'
# Agent Configuration

This project uses AI Agent MD Pack located in `agent/` directory.

**Start here:** [agent/00_INDEX.md](../agent/00_INDEX.md)

All agent instructions, workflows, and policies are in the `agent/` folder.
EOF

# Create symlinks to key files
ln -s ../agent/00_SYSTEM.md agent/00_SYSTEM.md
ln -s ../agent/00_INDEX.md agent/00_INDEX.md
ln -s ../agent/01_PROJECT_CONTEXT.md agent/01_PROJECT_CONTEXT.md
```

---

## Option 3: Add Custom Instructions

### Create `.antigravity` File
```bash
cat > .antigravity << 'EOF'
# Antigravity Configuration

## Agent Instructions
Read the AI Agent MD Pack in the `agent/` directory:
1. Start with `agent/00_SYSTEM.md` for agent behavior rules
2. Use `agent/00_INDEX.md` as the main router
3. Load `agent/01_PROJECT_CONTEXT.md` for project configuration
4. Follow workflows in `agent/workflows/` for all tasks

## Important
- ALWAYS read `agent/00_INDEX.md` before taking any action
- Follow the routing rules in `agent/ROUTING_RULES.md`
- Respect policies in `agent/policy/` (especially PRODUCTION_POLICY.md)
- Run quality gates in `agent/gates/` before completion

## Quick Start
For any request, start with:
"Read agent/00_INDEX.md and [your request]"
EOF
```

---

## Option 4: Project README Integration

### Add to Your Project's README.md
```markdown
## AI Agent Configuration

This project uses the AI Agent MD Pack for automated development and operations.

**For AI Agents (like Antigravity):**
- **Start here:** [`agent/00_INDEX.md`](agent/00_INDEX.md)
- **System instructions:** [`agent/00_SYSTEM.md`](agent/00_SYSTEM.md)
- **Project config:** [`agent/01_PROJECT_CONTEXT.md`](agent/01_PROJECT_CONTEXT.md)

**For all requests:** Read `agent/00_INDEX.md` first, then follow the appropriate workflow.
```

---

## Verification

### Test Antigravity Integration

**Method 1: Direct Test**
```
Ask Antigravity: "What agent configuration do you see in this project?"

Expected response: Should mention finding agent/ or agent/ directory
```

**Method 2: Task Test**
```
Ask Antigravity: "Fix this error: [paste error]"

Expected: Antigravity should:
1. Detect agent/ folder
2. Read 00_INDEX.md
3. Route to appropriate workflow
4. Follow the workflow steps
```

**Method 3: Check Logs**
```
Ask Antigravity: "What files did you read to understand this project?"

Expected: Should list:
- agent/00_SYSTEM.md
- agent/00_INDEX.md
- agent/01_PROJECT_CONTEXT.md
```

---

## Recommended Setup for Antigravity

### Best Practice Structure
```
your-project/
├── agent/                    # Antigravity standard location
│   ├── 00_SYSTEM.md          # Agent behavior rules
│   ├── 00_INDEX.md           # Main router
│   ├── 01_PROJECT_CONTEXT.md # Project config
│   ├── workflows/            # All workflows
│   ├── checklists/           # Evidence collection
│   ├── policy/               # Safety rules
│   └── ...                   # All other AI pack files
│
├── src/                      # Your application code
├── tests/                    # Your tests
├── README.md                 # Project README (with AI section)
└── .antigravity              # Optional: explicit instructions
```

### Or Keep Current Structure
```
your-project/
├── agent/                       # AI Agent MD Pack
│   ├── 00_SYSTEM.md
│   ├── 00_INDEX.md
│   └── ...
│
├── agent/                   # Pointer to agent/
│   └── README.md            # Points to agent/
│
├── src/
├── tests/
└── README.md                # With AI agent section
```

---

## Auto-Detection Priority

Antigravity checks in this order:
1. **`.antigravity`** file (highest priority)
2. **`agent/`** directory
3. **`agent/`** directory with `00_INDEX.md`
4. **README.md** with agent instructions
5. **Default behavior** (no custom config)

**Recommendation:** Use `agent/` directory for maximum compatibility.

---

## Making It Seamless

### Add to .gitignore (Optional)
```bash
# If you want to keep agent config local
echo "agent/" >> .gitignore

# Or commit it for team use
# (recommended - share the configuration)
```

### Add Pre-commit Hook (Optional)
```bash
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Ensure agent config is up to date

if [ -d "agent" ]; then
    echo "✓ Agent configuration found"
else
    echo "⚠ Warning: No agent directory found"
fi
EOF

chmod +x .git/hooks/pre-commit
```

---

## Quick Migration Script

### Automated Setup
```bash
#!/bin/bash
# migrate-to-antigravity.sh

echo "Setting up Antigravity integration..."

# Option 1: Rename ai to agent
if [ -d "ai" ] && [ ! -d "agent" ]; then
    echo "Renaming agent/ to agent/"
    mv ai agent
    echo "✓ Done"
fi

# Option 2: Create symlink (if you want to keep agent/)
# if [ -d "ai" ] && [ ! -d "agent" ]; then
#     echo "Creating agent symlink to agent/"
#     ln -s ai agent
#     echo "✓ Done"
# fi

# Verify
if [ -f "agent/00_INDEX.md" ]; then
    echo "✓ Antigravity will auto-detect agent configuration"
else
    echo "✗ Error: 00_INDEX.md not found"
fi
```

---

## Testing Integration

### Test 1: Detection
```
Ask Antigravity: "Do you see any agent configuration in this project?"
Expected: "Yes, I see agent/ (or agent/) directory with configuration"
```

### Test 2: Routing
```
Ask Antigravity: "What's the main entry point for agent tasks?"
Expected: "00_INDEX.md serves as the main router"
```

### Test 3: Execution
```
Ask Antigravity: "Help me debug a 502 error"
Expected: Should follow workflows/nginx_502_504.md
```

---

## Troubleshooting

### Antigravity Not Detecting Config
**Solution 1:** Rename to standard location
```bash
mv ai agent
```

**Solution 2:** Add explicit instruction in README
```markdown
**For AI Agents:** Start with `agent/00_INDEX.md`
```

**Solution 3:** Create `.antigravity` file
```bash
echo "Read agent/00_INDEX.md for all agent instructions" > .antigravity
```

### Antigravity Using Wrong Workflow
**Solution:** Be explicit in request
```
"Read agent/00_INDEX.md and follow the nginx 502 workflow"
```

### Antigravity Skipping Safety Checks
**Solution:** Ensure it reads policies
```
"Read agent/00_INDEX.md and agent/policy/PRODUCTION_POLICY.md before proceeding"
```

---

## Summary

**Easiest Setup (Recommended):**
```bash
# Rename ai to agent
mv ai agent

# Done! Antigravity will auto-detect
```

**Alternative (Keep agent/ name):**
```bash
# Create pointer
mkdir agent
echo "See agent/ directory for agent configuration" > agent/README.md
ln -s ../agent/00_INDEX.md agent/00_INDEX.md
```

**Either way, Antigravity will:**
1. ✅ Auto-detect the configuration
2. ✅ Read 00_INDEX.md as router
3. ✅ Follow all workflows
4. ✅ Respect all policies
5. ✅ Use all quality gates

---

**Questions?** Ask Antigravity:
```
"How do you detect and use agent configuration in this project?"
```
