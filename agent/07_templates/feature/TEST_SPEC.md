# Test Specification: [Feature Name]

## 1. Overview

- **Connected Feature**: `agent/07_templates/feature/FEATURE_SPEC.md`
- **Quality Goal**: [e.g., 90% coverage for core logic]

## 2. Test Cases (Success Path)

| ID | Scenario | Input | Expected Output | Status |
| --- | --- | --- | --- | --- |
| TS-001 | Successful Login | Valid Creds | 200 OK + JWT | |
| TS-002 | Data Retrieval | Active ID | Correct JSON | |

## 3. Edge Cases & Error Handling

| ID | Scenario | Input | Expected Behavior |
| --- | --- | --- | --- |
| TE-001 | Invalid Token | Expired JWT | 401 Unauthorized |
| TE-002 | Large Payload | 10MB JSON | 413 Payload Too Large |

## 4. Environment Requirements

- [ ] Mock Database setup.
- [ ] Environment variables defined.

## 5. Security Validation

- [ ] No PII in logs.
- [ ] Rate limiting enforced.

## 6. Verification Command

`npm test path/to/feature.test.js`
