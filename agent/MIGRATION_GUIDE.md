# Migration Guide: v3 → v4

## Overview

Version 4 introduces the **autofill system** to minimize user input and improve agent autonomy. This guide helps you upgrade from v3 to v4.

---

## What's New in v4

### 1. Autofill System
- Agents can now infer 80% of configuration from repo structure
- New `autofill/PATH_AND_SERVICE_INFERENCE.md` with inference rules
- Structured `AUTO_CONTEXT` YAML block in `01_PROJECT_CONTEXT.md`

### 2. Improved Documentation
- New `README.md` in agent/ folder
- New `ARCHITECTURE.md` with system diagrams
- New `examples/` directory with real-world examples

### 3. Standardized Naming
- All profile files now lowercase (`default.md` not `DEFAULT.md`)
- All artifact templates lowercase
- Consistent file naming across the board

### 4. Enhanced Routing
- Better keyword matching in `ROUTING_RULES.md`
- More examples in `00_INDEX.md`
- Clearer workflow selection

---

## Breaking Changes

### ⚠️ Profile File Names
**Old (v3):**
```
agent/profiles/DEFAULT.md
agent/profiles/PROD_SAFE.md
agent/profiles/AUTOFIX_AGGRESSIVE.md
```

**New (v4):**
```
agent/profiles/default.md
agent/profiles/production_safe.md
agent/profiles/aggressive_autofix.md
```

**Action Required:** Update any references to profile files in your documentation or scripts.

---

### ⚠️ PROJECT_CONTEXT Structure
**Old (v3):**
```markdown
## Identity
- Project name: myapp
- Repo URL: ...
```

**New (v4):**
```yaml
## AUTO_CONTEXT
```yaml
app_name: "myapp"
env: "dev"
...
```
```

**Action Required:** Convert your v3 context to the new YAML format. See `examples/example_project_context.md`.

---

## Migration Steps

### Step 1: Backup Current Configuration
```bash
# Backup your current agent/ folder
cp -r agent/ ai.v3.backup/
```

### Step 2: Update Core Files

#### Update `01_PROJECT_CONTEXT.md`
1. Open `01_PROJECT_CONTEXT.md`
2. Replace the old format with new `AUTO_CONTEXT` YAML block
3. Fill only what you know - leave rest blank for autofill

**Before (v3):**
```markdown
## Identity
- Project name: eye-donation
- Framework: Flask
```

**After (v4):**
```yaml
## AUTO_CONTEXT
```yaml
app_name: "eye-donation"
env: "dev"
# Leave rest blank - agent will infer
```
```

#### Update Profile References
Search for any references to UPPERCASE profile names:
```bash
grep -r "DEFAULT.md\|PROD_SAFE.md\|AUTOFIX_AGGRESSIVE.md" agent/
```

Replace with lowercase versions:
- `DEFAULT.md` → `default.md`
- `PROD_SAFE.md` → `production_safe.md`
- `AUTOFIX_AGGRESSIVE.md` → `aggressive_autofix.md`

### Step 3: Add New Files

Copy new files from v4:
```bash
# From v4 template
cp ai-v4-template/agent/README.md agent/
cp ai-v4-template/agent/ARCHITECTURE.md agent/
cp -r ai-v4-template/agent/examples/ agent/
cp -r ai-v4-template/agent/autofill/ agent/
```

### Step 4: Remove Duplicate Files

If you have UPPERCASE versions, remove them:
```bash
cd agent/profiles/
rm -f DEFAULT.md PROD_SAFE.md AUTOFIX_AGGRESSIVE.md

cd ../artifacts/
rm -f INCIDENT_REPORT.md POSTMORTEM.md PR_SUMMARY.md
```

### Step 5: Verify Migration

Run verification checks:

```bash
# Check AUTO_CONTEXT exists
grep -A 5 "AUTO_CONTEXT" agent/01_PROJECT_CONTEXT.md

# Check no UPPERCASE profiles remain
ls agent/profiles/

# Check new files exist
ls agent/README.md agent/ARCHITECTURE.md agent/examples/
```

---

## Feature Comparison

| Feature | v3 | v4 |
|---------|----|----|
| **Autofill** | ❌ No | ✅ Yes |
| **Structured Context** | ❌ Freeform | ✅ YAML schema |
| **Examples** | ❌ None | ✅ 3 complete examples |
| **Architecture Docs** | ❌ No | ✅ Complete diagrams |
| **Visual Diagrams** | ❌ No | ✅ 10+ Mermaid diagrams |
| **README** | ❌ No | ✅ Comprehensive |
| **Inference Rules** | ❌ No | ✅ Documented |

---

## Compatibility

### Backward Compatibility
- ✅ All v3 workflows still work
- ✅ All v3 checklists unchanged
- ✅ All v3 policies unchanged
- ✅ All v3 skills unchanged

### What Changed
- ⚠️ Profile file names (lowercase)
- ⚠️ PROJECT_CONTEXT format (YAML)
- ✅ New autofill system (additive)
- ✅ New documentation (additive)

---

## Rollback Plan

If you need to rollback to v3:

```bash
# Restore backup
rm -rf agent/
mv ai.v3.backup/ agent/

# Verify
ls agent/profiles/DEFAULT.md  # Should exist in v3
```

---

## Getting Help

### Common Issues

#### Issue 1: Agent asking too many questions
**Solution:** Fill more fields in `AUTO_CONTEXT` block, or check autofill rules in `autofill/PATH_AND_SERVICE_INFERENCE.md`

#### Issue 2: Profile not found
**Solution:** Update references from UPPERCASE to lowercase

#### Issue 3: Context format error
**Solution:** Ensure YAML block is properly formatted with quotes around strings

---

## Next Steps

After migration:

1. ✅ Test with a simple request: "Read agent/00_INDEX.md"
2. ✅ Verify autofill works: Leave some fields blank in AUTO_CONTEXT
3. ✅ Review new examples: Check `agent/examples/`
4. ✅ Read architecture docs: `agent/ARCHITECTURE.md`
5. ✅ Customize for your project: Update conventions, add workflows

---

## Changelog

### v4 (2026-01-05)
- ✨ Added autofill system
- ✨ Added structured AUTO_CONTEXT
- ✨ Added comprehensive documentation
- ✨ Added examples directory
- ✨ Added ARCHITECTURE.md
- 🔧 Standardized file naming (lowercase)
- 🔧 Enhanced routing with examples
- 📚 Added 10+ Mermaid diagrams

### v3 (Previous)
- Initial workflow system
- Basic policy framework
- Artifact templates

---

**Questions?** See [`README.md`](README.md) or [`QUICKSTART.md`](QUICKSTART.md)
