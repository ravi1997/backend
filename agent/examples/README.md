# Examples Directory

This directory contains complete, real-world examples of using the AI Agent MD Pack.

## Available Examples

### 1. [Example Project Context](example_project_context.md)
**What it shows:** Complete filled `01_PROJECT_CONTEXT.md` for a Flask application

**Use this when:**
- Setting up the AI pack for the first time
- Unsure what values to fill in AUTO_CONTEXT
- Want to see a real-world configuration

**Key learnings:**
- Minimum vs. complete configuration
- How to structure environment-specific settings
- PHI/PII considerations

---

### 2. [Example Incident Workflow](example_incident_workflow.md)
**What it shows:** Complete incident response from 502 error to resolution

**Scenario:** Website returning 502 Bad Gateway due to missing Python dependency

**Use this when:**
- Learning how incident triage works
- Understanding evidence collection
- Seeing the complete flow from error to fix

**Key learnings:**
- Evidence-first approach
- Root cause analysis methodology
- Quality gates and verification
- Artifact generation

**Timeline:** 15 minutes from detection to resolution

---

### 3. [Example Feature Delivery](example_feature_delivery.md)
**What it shows:** Complete feature implementation from request to PR

**Scenario:** Implementing user login with email/password authentication

**Use this when:**
- Planning a new feature
- Understanding the development workflow
- Learning testing and quality gate requirements

**Key learnings:**
- Structured planning (forms → decision records)
- Test-driven development approach
- Security considerations
- PR documentation standards

**Timeline:** ~1.5 hours from request to PR-ready code

---

## How to Use These Examples

### For First-Time Users
1. Start with **Example Project Context** to understand configuration
2. Read **Example Incident Workflow** to see how errors are handled
3. Review **Example Feature Delivery** to understand development flow

### For AI Agents
These examples demonstrate:
- Expected level of detail in forms and artifacts
- Quality standards for code and tests
- Documentation completeness
- Verification and validation steps

### For Customization
Use these as templates:
- Copy structure for your own workflows
- Adapt forms and checklists to your needs
- Modify quality gates for your standards

---

## Example Patterns

### Common Elements Across Examples

1. **Clear Scenario** - Every example starts with a specific, realistic scenario
2. **Step-by-Step Flow** - Shows progression through the system
3. **Actual Commands** - Real commands with expected output
4. **Artifacts Generated** - Shows what documentation is produced
5. **Metrics** - Time estimates and success criteria

### Quality Standards Demonstrated

- ✅ Evidence collection before action
- ✅ Root cause analysis
- ✅ Comprehensive testing
- ✅ Security considerations
- ✅ Complete documentation
- ✅ Verification steps

---

## Creating Your Own Examples

To add a new example:

1. **Choose a scenario** - Real-world, specific use case
2. **Follow the structure:**
   ```markdown
   # Example: [Name]
   
   ## Scenario
   [Clear description]
   
   ## Step 1: [Phase]
   [Details with commands/code]
   
   ## Step N: [Final Phase]
   [Results and artifacts]
   
   ## Key Takeaways
   [Lessons learned]
   ```
3. **Include:**
   - Actual commands and output
   - Code snippets where relevant
   - Generated artifacts
   - Time estimates
   - Key learnings

4. **Update this README** with your new example

---

## Quick Reference

| Example | Type | Complexity | Time | Key Focus |
|---------|------|------------|------|-----------|
| Project Context | Setup | Low | 5 min | Configuration |
| Incident Workflow | Operations | Medium | 15 min | Debugging |
| Feature Delivery | Development | High | 1.5 hrs | Implementation |

---

## Related Documentation

- [`../00_INDEX.md`](../00_INDEX.md) - Main router
- [`../workflows/`](../workflows/) - Workflow templates
- [`../ARCHITECTURE.md`](../ARCHITECTURE.md) - System architecture
- [`../QUICKSTART.md`](../QUICKSTART.md) - Getting started guide

---

**Need more examples?** Open an issue or contribute your own!
