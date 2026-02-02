# Workflow: UX/UI Design & Prototyping

**ID:** 12_ux_design_prototype
**Trigger:** Start of a frontend feature or new app design.

## 1. Purpose

To Translate requirements into visual designs, wireframes, and prototypes before coding begins.

## 2. Inputs

- `plans/SRS/srs_document.md`
- `agent/11_rules/html_css_js_rules.md` (or specific stack UI rules)
- `agent/08_gates/ux_design_checklist.md`

## 3. Steps

### 3.1. Wireframing

- **Action**: Create low-fidelity wireframes for key screens.
- **Reference**: `agent/07_templates/diagrams/DIAGRAM_TEMPLATE.md` (Mermaid/ASCII).

### 3.2. Visual Design

- **Action**: Define color palette, typography (Google Fonts), and component styles.
- **Output**: `plans/Design/design_system_specs.md`.

### 3.3. Prototyping (Mockups)

- **Action**: Generate high-fidelity mockups of the interface.
- **Tool**: `generate_image` tool (if available) or CSS implementations.

### 3.4. User Flow Validation

- **Action**: Walk through the design with "User Hat" on.
- **Check**: Does the flow make sense? Is it intuitive?

## 4. Output Artifacts

- `plans/Design/wireframes/`
- `plans/Design/mockups/`
- `plans/Design/design_spec.md`

## 5. Gates & Checks

- [ ] **Aesthetics**: Does it meet "Premium" design rules?
- [ ] **Responsiveness**: Is mobile layout considered?
- [ ] **Accessibility**: Contrast ratios and tap targets checked.

## 6. State Update

- Update `agent/09_state/project_state.md` -> `stage: "design_complete"`
