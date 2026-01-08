# Workflow: Model and Config Management

**Purpose:** Add, update, delete, and test models, classes, and configurations
**When to use:** When modifying the data layer, core logic classes, or application settings
**Prerequisites:** Access to model/config files and validation scripts

---

## Step 1: Add a Model/Class/Config
Introduce new data structures or settings.

### Actions
- Create the new model or class following project conventions (e.g., in `models/` or `classes/`).
- Define fields, methods, and constraints clearly.
- For configurations, add the new keys to the default config file (e.g., `config/default.yaml`).

### Validation
- [ ] Schema is valid.
- [ ] Type hints are included.

---

## Step 2: Update a Model/Class/Config
Modify existing structures or settings.

### Actions
- Update the definition to include new fields or logic.
- **IMPORTANT:** If changing a model, ensure a migration is created if using a database.
- Update configuration values and ensure they are loaded correctly.

---

## Step 3: Delete a Model/Class/Config
Remove obsolete components.

### Actions
- Verify no other parts of the system are using the component.
- Remove the file or configuration keys.
- Perform a cleanup of any related artifacts.

---

## Step 4: Test Models and Configs
Verify integrity and correctness.

### Commands
```bash
# Run unit tests for models/classes
pytest tests/models/

# Verify configuration loading
# Example:
# ./scripts/validate_configs.py
```

### Logging Results
**IMPORTANT:** Write test results to `tests/models/results.log`.
```bash
echo "$(date): Model/Config test result: <PASS/FAIL>" >> tests/models/results.log
```

---

## Completion Criteria
- ✅ Components are added, updated, or deleted.
- ✅ All schema and type checks pass.
- ✅ Results are logged in the specified output file.
