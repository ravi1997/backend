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

*(No active issues reported yet.)*

---

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
```

---

## ✅ Resolved Issues
<!-- Example format:
### [Resolved #0] CORS Error
**Resolution:** Added `Flask-CORS` to `create_app`. Backend restarted.
-->
