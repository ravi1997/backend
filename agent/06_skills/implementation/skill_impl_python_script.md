# Skill: Implement Python Script

## Context

When creating a standalone Python script or module.

## 1. Structure

- Shebang (for scripts): `#!/usr/bin/env python3`
- Imports: Calculated order (Standard -> Third Party -> Local).
- Main Guard: `if __name__ == "__main__":`

## 2. Scaffold

```python
#!/usr/bin/env python3
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main() -> int:
    try:
        logger.info("Starting execution...")
        # Logic here
        return 0
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

## 3. Implementation Steps

1. Setup structure with main guard.
2. Define helper functions with type hints (`def foo(bar: int) -> str:`).
3. Implement logic.
4. Add error handling.

## 4. Verification

- `python script.py` runs without defined errors.
- `flake8 script.py` passes.
