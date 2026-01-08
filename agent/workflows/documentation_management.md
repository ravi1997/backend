# Documentation Management Workflow

**Purpose:** Standard procedures for creating, updating, and maintaining documentation from different perspectives.
**When to use:** When adding new features, performing major refactors, or preparing for a release.

---

## 1. Prerequisites
- [ ] Feature or module is defined or implemented.
- [ ] Core technical details are understood (for Developer Guide).
- [ ] User personas and use cases are identified (for User Guide).
- [ ] Test plan is drafted (for Tester Guide).

## 2. Steps

### Selection
1. Identify the target audience:
   - **Developers:** Use `DEVELOPER_GUIDE_TEMPLATE.md`.
   - **Users:** Use `USER_GUIDE_TEMPLATE.md`.
   - **Testers:** Use `TESTER_GUIDE_TEMPLATE.md`.

### Execution
2. **Read Source:** Examine the relevant source files using `view_file` or `grep_search`.
3. **Draft Content:** Fill in the chosen template based on the gathered information.
4. **Link Files:** Use absolute file links (e.g., `file:///...`) to reference specific code locations.
5. **Add Diagrams:** Use Mermaid diagrams to visualize complex logic or architectures.

### Review
6. Perform an `AGENT_SELF_CHECK` on the drafted documentation.
7. Ensure all links are valid and content is accurate.

## 3. Completion Criteria
- [ ] Documentation file(s) created in the appropriate project directory (e.g., `docs/`).
- [ ] Content covers all sections of the template.
- [ ] File links and diagrams are functional.

## 4. See Also
- [`../artifacts/DOCS_MANIFEST.md`](../artifacts/DOCS_MANIFEST.md)
- [`../gates/QUALITY_GATES.md`](../gates/QUALITY_GATES.md)
