---
description: Run the comprehensive test suite and generate reports on failure
---

This workflow runs all unit, integration, and flow tests defined in the `tests/` directory. If any tests fail, it automatically generates a detailed `TEST_FAILURE_REPORT.md` analyzing the failures.

### Steps

1. **Navigate to the workspace root**
   Ensure you are in the backend directory.

2. **Run the test runner script**
   Execute the python script that wraps pytest execution.

   ```bash
   python3 scripts/run_tests_with_report.py
   ```

3. **Check results**
   - If the command returns exit code `0`, all tests passed.
   - If the command returns exit code `1`, check `TEST_FAILURE_REPORT.md` for details on what failed and how to fix it.

### Troubleshooting

- If `scripts/run_tests_with_report.py` is missing, ensure you have pulled the latest changes or restored the script.
- Ensure `pytest` is installed in your environment (`pip install pytest`).
