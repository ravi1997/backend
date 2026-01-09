---
description: Iteratively implements the next feature from the SRS.md roadmap.
---

1. **Identify Next Feature**:
   - Review `task.md` to see if there are pending tasks.
   - If no pending tasks, review `SRS.md` (specifically Appendix D and E) to identify the next high-priority unimplemented feature.
   - Add the new feature and its sub-tasks to `task.md`.

2. **Plan Implementation**:
   - Analyze the feature requirements.
   - Identify necessary model changes (`app/models/`).
   - Identify necessary route/endpoint changes (`app/routes/`).
   - Identify necessary utility changes (`app/utils/`).

3. **Implementation Cycle**:
   - **Model Changes**: Update MongoDB models if required. Verify with `verify_models.py` (if exists) or simple import check.
   - **Logic & Routes**: Implement the backend logic and API endpoints. 
   - **Unit/Integration Tests**: Create a new test file `tests/test_<feature_name>.py` covering positive and negative cases.
   - **Run Tests**: Execute the specific test file using `pytest`.
   - **Debug**: If tests fail, analyze logs/output, fix code, and re-run tests.

4. **Documentation & Release**:
   - Update `CHANGELOG.md` with the new feature.
   - Mark tasks as completed in `task.md`.

// turbo
5. **Commit Changes**:
   - Run `git add .`
   - Run `git commit -m "feat: Implement <Feature Name>"`

6. **Loop**:
   - If there are remaining steps in `task.md` for this feature, continue.
   - If functionality is complete, return to Step 1 for the *next* feature.
