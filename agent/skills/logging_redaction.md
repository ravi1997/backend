# Skill: PHI/PII-safe Logging & Redaction

Rules:
- Never log Authorization/Cookie
- Never log raw request bodies by default
- Redact common PII keys
- Truncate long values
- Always include request_id/trace_id

Add:
- structured logs with event type and correlation fields
