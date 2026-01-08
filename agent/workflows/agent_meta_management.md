# Workflow: Agent Meta-Management

**Purpose:** Add, update, or refine the `agent` directory itself
**When to use:** When adding new skills, refining workflows, updating policies, or improving the agent's "brain"
**Prerequisites:** Deep understanding of the existing `agent` hierarchy

---

## Step 1: Analyze the Gap
Identify what is missing or broken in the current configuration.

### Actions
- Check `00_INDEX.md` and `REFERENCE_MAP.md` to see if a similar feature exists.
- Determine if the change should be a **Skill** (procedural), a **Workflow** (step-by-step), or a **Policy** (rule).

---

## Step 2: Create or Update Feature
Follow the established patterns for the target directory.

### Standards
- **Skills**: Use `skills/project_auto_setup.md` as a template (comprehensive commands).
- **Workflows**: Use `workflows/feature_delivery.md` as a template (numbered steps, validation, completion criteria).
- **Checklists**: Ensure they produce evidence that can be cited.

---

## Step 3: Update Discovery
Ensure the new feature is visible to other agents.

### Actions
- Add the new file to `REFERENCE_MAP.md` with an appropriate tag.
- Link the feature in `00_INDEX.md` or a relevant `README.md`.
- Update `.cursorrules` if a major new entry point is added.

---

## Step 4: Verify Universality
Ensure the new feature does not contain hardcoded project assumptions.

### Validation
- [ ] Check for hardcoded paths.
- [ ] Use variables from `01_PROJECT_CONTEXT.md` (e.g., `{{app_name}}`).
- [ ] Verify links are absolute or correctly relative within `agent`.

---

## Completion Criteria
- ✅ New agent feature is implemented and documented.
- ✅ Discovery indices are updated.
- ✅ Meta-check: "Can another agent understand and use this perfectly?" → YES.
