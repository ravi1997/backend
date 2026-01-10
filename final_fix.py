
table_content = """| Method | Endpoint                                     | Auth       | Request Body                                                             | Response                                   | Usage               |
| ------ | -------------------------------------------- | ---------- | ------------------------------------------------------------------------ | ------------------------------------------ | ------------------- |
| POST   | `/api/v1/auth/register`                      | ❌         | `{ username, email, employee_id, mobile, password, confirm_password }`   | `{ message }`                              | FR-FRONT-AUTH-02    |
| POST   | `/api/v1/auth/login`                         | ❌         | `{ email, password }` **or** `{ mobile, otp }`                           | `{ access_token, user }`                   | FR-FRONT-AUTH-01    |
| POST   | `/api/v1/auth/generate-otp`                  | ❌         | `{ mobile }`                                                             | `{ message }`                              | FR-FRONT-AUTH-03    |
| POST   | `/api/v1/auth/logout`                        | ✅         | `{}`                                                                     | `{ message }`                              | FR-FRONT-AUTH-05    |
| GET    | `/api/v1/user/status`                        | ✅         | -                                                                        | `IUser`                                    | FR-FRONT-AUTH-04    |
| POST   | `/api/v1/form/`                              | ✅         | `Partial<IForm>`                                                         | `{ form_id }`                              | Builder create      |
| GET    | `/api/v1/form/`                              | ✅         | -                                                                        | `IForm[]`                                  | List forms          |
| GET    | `/api/v1/form/{id}`                          | ✅         | -                                                                        | `IForm`                                    | Load/edit           |
| PUT    | `/api/v1/form/{id}`                          | ✅         | `Partial<IForm>`                                                         | `{ message }`                              | Update              |
| DELETE | `/api/v1/form/{id}`                          | ✅         | -                                                                        | `{ message }`                              | Delete              |
| PATCH  | `/api/v1/form/{id}/publish`                  | ✅         | -                                                                        | `{ message }`                              | Publish             |
| POST   | `/api/v1/form/{id}/clone`                    | ✅         | -                                                                        | `{ form_id }`                              | Clone               |
| POST   | `/api/v1/form/{id}/responses`                | ✅         | `{ data: Record<string, any> }`                                          | `{ response_id }`                          | Auth submit         |
| POST   | `/api/v1/form/{id}/public-submit`            | ❌         | `{ data: Record<string, any> }`                                          | `{ response_id }`                          | Public submit       |
| GET    | `/api/v1/form/{id}/responses`                | ✅         | `?page=&limit=`                                                          | `PaginatedResponse<IFormResponse>`         | List responses      |
| GET    | `/api/v1/form/{id}/responses/{rid}`        | ✅         | -                                                                        | `IFormResponse`                            | Detail              |
| POST   | `/api/v1/form/{id}/files/{qid}`              | ✅ (cond.) | `multipart/form-data`                                                    | `{ filename, filepath, size }`             | File upload         |
| GET    | `/api/v1/form/{id}/files/{qid}/{filename}`   | ✅ (cond.) | -                                                                        | File stream                                | Download            |
| GET    | `/api/v1/approvals/pending`                  | ✅         | -                                                                        | `IFormResponse[]`                          | Pending approvals   |
| POST   | `/api/v1/approvals/{responseId}/action`      | ✅         | `{ action, comment, step_id }`                                           | `{ message }`                              | Approve/Reject      |
| GET    | `/api/v1/approvals/{responseId}/history`     | ✅         | -                                                                        | `IApprovalAction[]`                        | History             |
| GET    | `/api/v1/form/{id}/export/csv`               | ✅         | -                                                                        | `text/csv`                                 | CSV export          |
| GET    | `/api/v1/form/{id}/export/json`              | ✅         | -                                                                        | `application/json`                         | JSON export         |
| GET    | `/api/v1/form/{id}/analytics`                | ✅         | -                                                                        | `{ total_responses, latest_submission }`   | Dashboard stats     |"""

path = '/home/programmer/Desktop/backend/future_plans/COMBINED_FRONTEND_SRS.md'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = lines[:365] + [l + '\n' for l in table_content.split('\n')] + lines[391:]

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
