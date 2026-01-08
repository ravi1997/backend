# PHI/PII Safe Logging Policy (Default ON)

Goal: diagnose issues without storing or exposing PHI/PII.

## Never log
- Authorization tokens, cookies, session ids
- Full request bodies by default
- Uploaded files (binary)
- DB rows containing patient identifiers

## Mask fields (examples)
- name, email, phone, address, aadhaar, pan, dob, mrn, uhid
- any identifier-like strings beyond last 4 chars

## Log instead
- request id / correlation id
- method, path, status, latency
- safe headers (User-Agent, X-Request-ID)
- body size + hash (optional) instead of full body
- exception type + stack trace (truncate)

## Redaction rules
- Header denylist: Authorization, Cookie, Set-Cookie, X-API-Key, X-CSRF-Token
- Query param denylist: token, password, secret, key
- JSON key regex: /name|email|phone|address|aadhaar|pan|dob|mrn|uhid/i

## When deeper inspection is needed
- Use a **time-limited debug window**
- Capture locally on developer machine
- Remove immediately after fix
