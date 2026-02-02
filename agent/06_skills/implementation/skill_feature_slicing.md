# Skill: Feature Slicing

## Purpose

Break down large features into shippable, vertical slices.

## Procedure

1. **Identify the Core**: What is the absolute minimum "Walking Skeleton"?
   - Example: For "User Login", slice 1 is "API Endpoint", slice 2 is "UI Form", slice 3 is "Integration".
2. **Vertical vs Horizontal**:
   - **Horizontal** (Avoid): "Build all DB tables", then "Build all APIs".
   - **Vertical** (Prefer): "Build DB+API+UI for Feature A".
3. **Define Slices**:
   - **Slice 1**: Core Data + Basic View (Read only).
   - **Slice 2**: Interactive Create/Update.
   - **Slice 3**: Validation & Error Handling.
   - **Slice 4**: Polish & CSS.

## Output

- List of subtasks in the Backlog, ordered by dependency.
