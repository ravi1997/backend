# Security Baseline (actionable)

## App-level
- Validate and normalize inputs
- Use parameterized DB queries / ORM
- Protect file paths: use allowlisted directories, never join untrusted paths blindly
- Enforce size limits for uploads and request bodies
- CSRF protection where applicable
- Rate limit login and sensitive endpoints

## Proxy-level (nginx)
- Limit request body size
- Add basic rate limiting for abusive patterns
- Block obvious traversal patterns carefully

## Headers (guidance)
- Consider: HSTS (https only), X-Content-Type-Options, Referrer-Policy
- CSP is powerful but needs careful rollout; start in report-only mode

## Logging
- Follow `policy/PHI_SAFE_LOGGING.md`

## Minimum checks
- run dependency audit if available
- review auth/session handling
