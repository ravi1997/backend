# Workflow: Basic Debugging

**Purpose:** General debugging workflow for application errors
**When to use:** Application errors, exceptions, unexpected behavior
**Prerequisites:** Access to code and logs
**Estimated time:** 15-45 minutes
**Outputs:** Bug fixed, tests added

---

## Prerequisites

- [ ] Error is reproducible
- [ ] Access to logs
- [ ] Can run application locally
- [ ] Environment detected

---

## Step 0: Context & Safety Setup

**Objective**: Secure the active scope and determine allowed actions (Execution Level).

### 1. Resolve Scope
Identify the component we are working on.

```bash
# Set scope (must match a component in agent/components/)
export ACTIVE_SCOPE="${ACTIVE_SCOPE:-default}"

# Verify component exists
if [ ! -f "agent/components/${ACTIVE_SCOPE}.md" ]; then
  echo "Error: Component ${ACTIVE_SCOPE} not found."
  # create it or ask user
fi
```

### 2. Resolve Execution Level
Determine `PLAN_ONLY`, `SAFE_LOCAL`, or `ELEVATED` based on `agent/environments/EXECUTION_CONTRACT.md`.

```bash
# Detect Environment Mode
source agent/scripts/detect_environment.sh

# Determine Level
if [ "$ENV_MODE" == "PROD_READONLY" ]; then
  export EXECUTION_LEVEL="PLAN_ONLY"
elif [ -f ".agent/elevated_access_token" ]; then
  export EXECUTION_LEVEL="ELEVATED"
else
  export EXECUTION_LEVEL="SAFE_LOCAL"
fi

echo "Active Scope: $ACTIVE_SCOPE"
echo "Execution Level: $EXECUTION_LEVEL"
```

### 3. Policy Check
- **Read Policy**: `agent/environments/COMMAND_POLICY.md`

---

## Step 1: Reproduce the Error

### Collect Information
- What is the error message?
- When does it occur?
- What are the steps to reproduce?
- Does it happen consistently?

### Reproduce Locally
```bash
# Run application
python wsgi.py
# or
docker-compose up

# Trigger the error
# ... perform steps ...

# Check logs
tail -f logs/app.log
```

---

## Step 2: Locate the Bug

### Read the Stack Trace
```python
# Example stack trace
Traceback (most recent call last):
  File "app/routes.py", line 45, in get_user
    user = User.query.get(user_id)
  File "app/models.py", line 12, in get
    return self.filter_by(id=id).first()
AttributeError: 'NoneType' object has no attribute 'first'
```

**Key information:**
- File: `app/routes.py`, line 45
- Function: `get_user`
- Error: `AttributeError`

### Add Debug Logging
```python
# Add logging to understand state
import logging
logger = logging.getLogger(__name__)

def get_user(user_id):
    logger.debug(f"Getting user with id: {user_id}")
    logger.debug(f"User.query type: {type(User.query)}")
    user = User.query.get(user_id)
    logger.debug(f"Found user: {user}")
    return user
```

---

## Step 3: Fix the Bug

### Common Fixes

**A) Null/None Handling**
```python
# ❌ BAD
user = User.query.get(user_id)
return user.name  # Crashes if user is None

# ✅ GOOD
user = User.query.get(user_id)
if user is None:
    raise NotFoundError(f"User {user_id} not found")
return user.name
```

**B) Type Errors**
```python
# ❌ BAD
def add_numbers(a, b):
    return a + b  # Crashes if a or b is not a number

# ✅ GOOD
def add_numbers(a: int, b: int) -> int:
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("Both arguments must be integers")
    return a + b
```

**C) Missing Imports**
```python
# ❌ BAD
result = datetime.now()  # NameError

# ✅ GOOD
from datetime import datetime
result = datetime.now()
```

---

## Step 4: Test the Fix

### Write a Test
```python
def test_get_user_not_found():
    """Test that get_user handles missing user correctly"""
    with pytest.raises(NotFoundError):
        get_user(999999)  # Non-existent user

def test_get_user_success():
    """Test that get_user returns user when found"""
    user = get_user(1)
    assert user is not None
    assert user.id == 1
```

### Run Tests
```bash
# Run the specific test
pytest tests/test_users.py::test_get_user_not_found -v

# Run all tests
pytest -v
```

---

## Step 5: Verify

```bash
# 1. Error no longer occurs
# ... reproduce steps ...
# Expected: No error

# 2. Tests pass
pytest -v
# Expected: All passed

# 3. No new errors introduced
# ... test related functionality ...
```

---

## Completion Criteria

- ✅ Bug is fixed
- ✅ Error no longer reproducible
- ✅ Test added for the bug
- ✅ All tests pass
- ✅ No new issues introduced

---

## Common Debugging Techniques

### Use Python Debugger
```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use built-in breakpoint() (Python 3.7+)
breakpoint()
```

### Print Debugging
```python
# Add strategic prints
print(f"DEBUG: user_id = {user_id}, type = {type(user_id)}")
print(f"DEBUG: query result = {User.query.get(user_id)}")
```

### Check Assumptions
```python
# Verify your assumptions
assert user_id is not None, "user_id should not be None"
assert isinstance(user_id, int), f"user_id should be int, got {type(user_id)}"
```

---

## See Also

- [`../skills/pytest_debugging.md`](../skills/pytest_debugging.md)
- [`../workflows/feature_delivery.md`](feature_delivery.md)
