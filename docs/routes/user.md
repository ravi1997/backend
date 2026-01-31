# User Management API

## Overview

The User Management module provides essential administrative and self-service capabilities for governing user accounts and their security settings. It encompasses a full set of **CRUD (Create, Read, Update, Delete)** operations reserved for administrators, as well as critical security endpoints for **password rotation**, **account unlocking**, and **session status verification**. This module ensures that user profiles are kept up-to-date, permissions are correctly assigned via roles, and account security is maintained through policy-driven controls like password expiration and OTP resend limits. It acts as the central directory for all personnel interacting with the AIOS platform.

## Base URL

`/form/api/v1/user`

## Endpoints

### POST /change-password

**Description**: Allows an authenticated user to update their current password.
**Auth Required**: Yes
**Request Body**:

```json
{
  "current_password": "OldPassword123!",
  "new_password": "NewSecurePassword456!"
}
```

**Examples**:

1. **Correct Change**: Password updated successfully.
2. **Incorrect Current Password**: Returns 400 error.
3. **Weak New Password**: Returns error if failing internal complexity (inferred).

**Curl Command**:

```bash
curl -X POST http://localhost:5000/form/api/v1/user/change-password \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"current_password": "123", "new_password": "456"}'
```

**Expected Output**:

```json
{
  "message": "Password changed"
}
```

---

### GET /users

**Description**: Lists all users in the system.
**Auth Required**: Yes (Admin/Superadmin only)
**Examples**:

1. **Admin View**: Retrieves full list of users with details.
2. **Regular User View**: Returns 403 Forbidden.
3. **Filter Search**: Potentially filtrable list.

**Curl Command**:

```bash
curl -X GET http://localhost:5000/form/api/v1/user/users \
     -H "Authorization: Bearer <admin_token>"
```

**Expected Output**:

```json
[
  {
    "id": "60d...",
    "username": "admin",
    "email": "admin@example.com",
    "roles": ["admin"]
  },
  ...
]
```

---

### POST /unlock

**Description**: Unlocks a user account that was previously locked due to too many failed login attempts.
**Auth Required**: Yes (Admin/Superadmin only)
**Request Body**:

```json
{
  "user_id": "60d5f..."
}
```

**Examples**:

1. **Successful Unlock**: User can now attempt login again.
2. **User Not Found**: Returns 404 error.
3. **Already Unlocked**: Operates successfully but has no effect.

**Curl Command**:

```bash
curl -X POST http://localhost:5000/form/api/v1/user/unlock \
     -H "Authorization: Bearer <admin_token>" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "607d..."}'
```

**Expected Output**:

```json
{
  "message": "User 607d... unlocked"
}
```

---

### GET /status

**Description**: Returns the profile of the currently authenticated user.
**Auth Required**: Yes
**Examples**:

1. **Profile Refresh**: Frontend fetches latest user data.
2. **Role Verification**: Checking if user is still an admin.
3. **Token Validation**: Indirectly validates token validity.

**Curl Command**:

```bash
curl -X GET http://localhost:5000/form/api/v1/user/status \
     -H "Authorization: Bearer <token>"
```

**Expected Output**:

```json
{
  "user": {
    "id": "...",
    "username": "jdoe",
    "roles": ["creator"],
    "is_active": true
  }
}
```
