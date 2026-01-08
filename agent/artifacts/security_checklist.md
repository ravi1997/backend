# Security Checklist (Per Change)

- [ ] Inputs validated (length, charset, count)
- [ ] SQL parameterized (no string SQL)
- [ ] File paths safe (no traversal, base dir enforced)
- [ ] Secrets not logged (headers/body redacted)
- [ ] AuthZ checks present (if route is protected)
- [ ] Rate limiting for sensitive endpoints (optional)
- [ ] Tests cover malicious inputs
