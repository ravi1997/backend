# Gate: Accessibility (WCAG 2.1)

## Purpose

Ensures inclusive design and compliance with global accessibility standards.

## Explicit Pass/Fail Rubric

| Criterion | Methodology | Pass Threshold | Fail Trigger |
| --- | --- | --- | --- |
| **ARIA Compliance** | `axe-core` / `Pa11y` | 0 Critical errors | Missing Alt text or labels |
| **Color Contrast** | `lighthouse` | Contrast >= 4.5:1 | Unreadable text |
| **Keyboard Nav** | Manual Tab testing | Full focus management | Trapped focus |
| **Semantic HTML** | `w3c validator` | Valid <main>, <nav> | Div-only structures |

## Sign-off Command
>
> Required for all Frontend and Documentation tasks.

## Related Files

- `agent/03_profiles/profile_ux_reviewer.md`
- `agent/12_checks/rubrics/docs_rubric.md`
