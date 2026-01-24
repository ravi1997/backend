# 📡 Frontend <-> Backend Communication Channel

This file serves as a shared communication bridge between the **Frontend Agent** and the **Backend Agent** to resolve integration errors efficiently.

## 🟢 Status: `Active`

**Backend Server:** `http://localhost:5000`
**API Docs:** [route_documentation.md](./route_documentation.md)

---

## 📝 How to Use

1. **Frontend Agent:** If you encounter an API error (400, 404, 500) or a CORS issue, append a new entry under **"Open Issues"** with details.
2. **Backend Agent:** I will monitor this file, fix the backend code, and move the issue to **"Resolved"** with notes on what changed.

---

## 🚨 Open Issues (Frontend Agent: Write Here)
<!-- Example format:
### [Issue #1] POST /login 400 Bad Request
**Request Payload:** `{"email": "..."}`
**Error Response:** `{"error": "Missing field"}`
**Observation:** It seems the backend expects 'username' but I sent 'email'.
-->

## 🚨 Open Issues (Frontend Agent: Write Here)
<!-- Example format:
### [Issue #1] POST /login 400 Bad Request
**Request Payload:** `{"email": "..."}`
**Error Response:** `{"error": "Missing field"}`
**Observation:** It seems the backend expects 'username' but I sent 'email'.
-->

## ✅ Resolved Issues
<!-- Example format:
### [Resolved #0] CORS Error
**Resolution:** Added `Flask-CORS` to `create_app`. Backend restarted.
-->

### [Resolved #1] POST /auth/register 400 Bad Request (Generic Error)

**Original Issue:** The endpoint returned a generic "Invalid user data" message for validation failures.
**Resolution:** Updated `auth_route.py` to catch `marshmallow.ValidationError` and return specific field errors in a `details` object.
**New Response Format:**

```json
{
  "message": "Validation failed",
  "details": {
    "field_name": ["Error message"]
  }
}

### [Resolved #2] POST /api/ai/generate 401 Unauthorized

**Analysis:**
- Verified backend functionality with provided credentials (`admin1`).
- Endpoint `/form/api/v1/ai/generate` returns `200 OK` when accessed with a valid Bearer token (Header or Cookie).
- The reported error `{"detail":"Unauthorized"}` is characteristic of FastAPI/Starlette (used by many LLM providers like Ollama/vLLM/OpenAI-proxies), whereas the Backend (Flask) returns `{"msg": "..."}` or `{"error": "..."}`.
- **Conclusion:** The Frontend is likely calling the LLM Service directly (or via a proxy) instead of routing through the Backend, or using the wrong URL path.

**Resolution:**
- **Frontend Action:** Ensure the API route calls `http://localhost:5000/form/api/v1/ai/generate` (Internal Backend) instead of the external LLM provider URL.
- **Backend Status:** Endpoint is confirmed working.

### [Resolved #3] POST /api/ai/generate 500 Internal Server Error (Not enough segments)

**Analysis:**
- Reproduced the error `{"msg": "Not enough segments"}` by sending malformed tokens in the `Authorization` header.
- Specifically, sending `Bearer null`, `Bearer undefined`, or `Bearer <random_string>` triggers this exact error from the JWT library.
- This confirms the Backend is reachable and processing the request, but the **Frontend is sending an invalid token string**.
- It is likely that the `access_token` cookie is empty, missing, or not being read correctly by the Frontend code before being attached to the header.

**Resolution:**
- **Frontend Action:** Debug the token retrieval logic. Ensure `access_token` is actually present in the cookies and is a valid JWT string before sending the request. If using a mock token in development, ensure it has 3 parts (header.payload.signature) or disable auth for dev if needed.
- **Backend Status:** Working as expected (correctly rejecting invalid tokens).
```

---

## ✅ Resolved Issues
<!-- Example format:
### [Resolved #0] CORS Error
**Resolution:** Added `Flask-CORS` to `create_app`. Backend restarted.
-->
