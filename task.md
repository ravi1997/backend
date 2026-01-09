# Tasks - Phase 2: Workflow Engine

- [x] Implement Workflow Models <!-- id: 0 -->
    - [x] Create `WorkflowAction` embedded document <!-- id: 1 -->
    - [x] Create `FormWorkflow` document <!-- id: 2 -->
- [x] Implement Workflow API Endpoints <!-- id: 3 -->
    - [x] POST /api/v1/workflows/ (Create) <!-- id: 4 -->
    - [x] GET /api/v1/workflows/ (List) <!-- id: 5 -->
    - [x] GET /api/v1/workflows/{id} (Get) <!-- id: 6 -->
    - [x] PUT /api/v1/workflows/{id} (Update) <!-- id: 7 -->
    - [x] DELETE /api/v1/workflows/{id} (Delete) <!-- id: 12 -->
- [x] Implement Workflow Evaluation Logic <!-- id: 8 -->
    - [x] Update `submit_response` to evaluate workflows <!-- id: 9 -->
    - [x] Implement condition evaluator (pythonic safe eval) <!-- id: 10 -->
    - [x] Return `next_action` payload in response <!-- id: 11 -->
- [x] Implement Workflow Tests <!-- id: 13 -->
    - [x] Test CRUD Workflows <!-- id: 14 -->
    - [x] Test Trigger Evaluation (Condition matching) <!-- id: 15 -->
    - [x] Test Data Mapping response <!-- id: 16 -->
