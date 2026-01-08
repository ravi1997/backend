# Skill: Pytest Debugging

**Purpose:** Debug failing pytest tests
**When to use:** When tests fail or behave unexpectedly
**Prerequisites:** pytest installed, test files exist
**Estimated time:** 10-30 minutes

---

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_users.py

# Run specific test
pytest tests/test_users.py::test_create_user

# Run with verbose output
pytest -v

# Run with print statements
pytest -s

# Run last failed tests
pytest --lf

# Run failed first
pytest --ff
```

---

## Debugging Techniques

### 1. Use Print Debugging

```python
def test_something():
    result = my_function()
    print(f"DEBUG: result = {result}")  # Will show with pytest -s
    assert result == expected
```

### 2. Use Pytest's Built-in Debugger

```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger at start of test
pytest --trace
```

### 3. Use Breakpoints

```python
def test_something():
    result = my_function()
    breakpoint()  # Python 3.7+
    assert result == expected
```

### 4. Show Locals on Failure

```bash
# Show local variables when test fails
pytest -l

# Show full diff
pytest -vv
```

---

## Common Issues

### Issue 1: Import Errors

**Symptom:** `ModuleNotFoundError` or `ImportError`

**Causes:**
- Missing `__init__.py`
- Wrong PYTHONPATH
- Missing dependencies

**Fixes:**
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Install in editable mode
pip install -e .

# Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

### Issue 2: Fixture Issues

**Symptom:** `fixture 'xyz' not found`

**Causes:**
- Fixture not defined
- Fixture in wrong file
- Wrong scope

**Fixes:**
```python
# Define fixture
@pytest.fixture
def my_fixture():
    return "value"

# Use fixture
def test_something(my_fixture):
    assert my_fixture == "value"

# Check conftest.py
# Fixtures in conftest.py are available to all tests
```

---

### Issue 3: Database/State Issues

**Symptom:** Tests pass individually but fail together

**Causes:**
- Shared state
- Database not cleaned
- Order dependency

**Fixes:**
```python
# Use function-scoped fixtures
@pytest.fixture(scope="function")
def db():
    # Setup
    db = create_db()
    yield db
    # Teardown
    db.drop_all()

# Or use pytest-django's transactional tests
@pytest.mark.django_db(transaction=True)
def test_something():
    pass
```

---

### Issue 4: Slow Tests

**Symptom:** Tests take too long

**Diagnosis:**
```bash
# Show slowest tests
pytest --durations=10

# Profile tests
pytest --profile
```

**Fixes:**
- Use mocks instead of real services
- Parallelize: `pytest -n auto` (requires pytest-xdist)
- Mark slow tests: `@pytest.mark.slow`

---

## Useful Pytest Options

```bash
# Stop on first failure
pytest -x

# Stop after N failures
pytest --maxfail=3

# Run only marked tests
pytest -m "not slow"

# Show coverage
pytest --cov=app tests/

# Generate HTML coverage report
pytest --cov=app --cov-report=html tests/

# Run in parallel
pytest -n auto  # requires pytest-xdist

# Rerun failures
pytest --lf --tb=short
```

---

## Debugging Checklist

- [ ] Run with `-v` for verbose output
- [ ] Run with `-s` to see print statements
- [ ] Run with `-l` to see local variables
- [ ] Run with `--pdb` to debug on failure
- [ ] Check test isolation (run individually vs together)
- [ ] Check fixtures are properly scoped
- [ ] Check for shared state issues
- [ ] Use `pytest --collect-only` to see what tests will run
- [ ] Check conftest.py for global fixtures
- [ ] Verify database is cleaned between tests

---

## Common Patterns

### Mocking

```python
from unittest.mock import Mock, patch

def test_with_mock():
    # Mock a function
    with patch('module.function') as mock_func:
        mock_func.return_value = "mocked"
        result = my_function()
        assert result == "mocked"
        mock_func.assert_called_once()
```

### Parametrize

```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    assert double(input) == expected
```

### Fixtures with Cleanup

```python
@pytest.fixture
def temp_file():
    # Setup
    f = open('temp.txt', 'w')
    yield f
    # Cleanup
    f.close()
    os.remove('temp.txt')
```

---

## See Also

- [`../workflows/debug_basic.md`](../workflows/debug_basic.md)
- [`../workflows/feature_delivery.md`](../workflows/feature_delivery.md)
- [Pytest Documentation](https://docs.pytest.org/)
