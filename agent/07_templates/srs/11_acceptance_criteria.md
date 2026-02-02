# SRS Acceptance Criteria: [Project Name]

## 1. Requirement mapping

This document tracks the binary pass/fail criteria for every functional and non-functional requirement.

## 2. Global Acceptance Standards

- [ ] No regression of existing features.
- [ ] Code meets `agent/11_rules/code_style_rules.md`.
- [ ] Documentation updated to reflect changes.

## 3. Feature-Specific Criteria

| ID | Requirement | Acceptance Criteria | Methodology | Status |
| --- | --- | --- | --- | --- |
| AC-001 | User Login | User receives JWT after valid email/pass. | Postman/Manual | |
| AC-002 | Password Reset | System sends email link within 5 seconds. | Integration Test | |

## 4. Non-Functional Criteria

| ID | Goal | Acceptance Criteria | Methodology | Status |
| --- | --- | --- | --- | --- |
| AC-NF-01 | Latency | API response < 200ms for p95. | Load Test | |
| AC-NF-02 | Security | Zero PII present in debug logs. | `skill_scrub_secrets` | |

---
**Authority**: [Product Owner / Lead Architect]  
**Last Review**: [YYYY-MM-DD]
