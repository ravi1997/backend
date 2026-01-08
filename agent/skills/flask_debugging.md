# Skill: Flask Debugging

## Common failure classes
- Import errors (module path, missing deps)
- Config/env var missing
- DB connection failures
- Template/static path issues
- Circular imports
- Request context misuse

## Standard steps
1. Confirm entry point: app factory vs global app
2. Verify config loading order
3. Reproduce with minimal request using Flask test client
4. Add regression test
5. Fix and verify

## Good patterns
- `create_app()` factory
- Blueprints
- structured error handlers
- request_id injection
