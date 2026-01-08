# Workflow: Test Management

**Purpose:** Add, update, delete, and run tests
**When to use:** When modifying the test suite or verifying code changes
**Prerequisites:** Access to test directory and test runner (e.g., pytest)

---

## Step 1: Add a Test
Create new tests for features or bug fixes.

### Actions
- Identify the component to be tested.
- Create a new test file in `tests/` following the naming convention (e.g., `test_<component>.py`).
- Implement happy path, edge cases, and error scenarios.

### Validation
- [ ] Test covers the intended logic.
- [ ] Test is repeatable and isolated.

---

## Step 2: Update a Test
Modify existing tests to match changes in application behavior.

### Actions
- Locate the existing test file.
- Update assertions and test data to reflect current requirements.
- Ensure the test suite remains robust.

---

## Step 3: Delete a Test
Remove obsolete or redundant tests.

### Actions
- Verify the test is no longer needed (e.g., feature removed).
- Remove the test file or specific test cases.
- Update any test coverage tracking.

---

## Step 4: Run Tests
Execute the test suite and log results.

### Commands
```bash
# Run all tests
pytest -v

# Run specific test file
pytest tests/test_my_feature.py -v
```

### Logging Results
**IMPORTANT:** Write test results to `tests/results.log` for future troubleshooting and error fixing.
```bash
echo "$(date): Test run results recorded." >> tests/results.log
# Append detailed failure info if applicable
# pytest --tb=short >> tests/results.log
```

---

## Completion Criteria
- ✅ Tests are added, updated, or removed as requested.
- ✅ All tests pass or failures are documented.
- ✅ Results are logged in the specified output file.
