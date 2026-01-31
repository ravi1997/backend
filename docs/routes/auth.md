# Authentication API

## Overview

The Authentication module provides the secure gateway for all users to access the AIOS system. It supports multiple authentication strategies, including traditional **Email/Password** login for administrative and creator roles, and **Mobile/OTP (One-Time Password)** login for field and general users. The module is built on industry-standard **JWT (JSON Web Token)** mechanisms, ensuring stateless, secure, and scalable session management. Security features such as automatic account locking after failed attempts, OTP expiration, and token blocklisting (for secure logout) are implemented out-of-the-box to protect sensitive form data and user information.

## Base URL

`/form/api/v1/auth`

## Endpoints

### POST /register

**Description**: Registers a new user in the system. Validates the input against the `UserSchema`, hashes the password, and creates a new user document.
**Auth Required**: No (Public)
**Request Body**:

```json
{
  "username": "jdoe",
  "email": "jdoe@example.com",
  "mobile": "9876543210",
  "password": "SecurePassword123!",
  "user_type": "internal",
  "roles": ["creator", "user"],
  "employee_id": "EMP123"
}
```

**Examples**:

1. **Successful Registration**: Registering a creator with all required fields.
2. **Duplicate Email Conflict**: Attempting to register with an email that already exists.
3. **Validation Error**: Missing required fields like `user_type` or `roles`.

**Curl Command**:

```bash
curl -X POST http://localhost:5000/form/api/v1/auth/register \
     -H "Content-Type: application/json" \
     -d '{
           "username": "tester",
           "email": "tester@example.com",
           "mobile": "1234567890",
           "password": "Password123",
           "user_type": "internal",
           "roles": ["user"]
         }'
```

**Expected Output**:

```json
{
  "message": "User registered"
}
```

---

### POST /login

**Description**: Authenticates a user and returns an access token. Supports login via `email`/`username`/`employee_id` with a `password`, or via `mobile` and `otp`.
**Auth Required**: No (Public)
**Request Body (Password)**:

```json
{
  "email": "jdoe@example.com",
  "password": "SecurePassword123!"
}
```

**Request Body (OTP)**:

```json
{
  "mobile": "9876543210",
  "otp": "123456"
}
```

**Examples**:

1. **Email Login**: Standard login for administrators.
2. **OTP Login**: Login for mobile users after generating an OTP.
3. **HTMX Response**: If `HX-Request` header is present, returns an HTML snippet for frontend integration.

**Curl Command**:

```bash
curl -X POST http://localhost:5000/form/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{
           "email": "tester@example.com",
           "password": "Password123"
         }'
```

**Expected Output**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "success": true
}
```

---

### POST /generate-otp

**Description**: Generates a 6-digit OTP for a given mobile number and sends it (currently logged for development). Valid for 5 minutes.
**Auth Required**: No (Public)
**Request Body**:

```json
{
  "mobile": "9876543210"
}
```

**Examples**:

1. **Existing User**: OTP generated successfully.
2. **Non-existent User**: Returns 404 error.
3. **Missing Mobile**: Returns 400 error.

**Curl Command**:

```bash
curl -X POST http://localhost:5000/form/api/v1/auth/generate-otp \
     -H "Content-Type: application/json" \
     -d '{
           "mobile": "9876543210"
         }'
```

**Expected Output**:

```json
{
  "msg": "OTP sent successfully",
  "success": true
}
```

---

### POST /logout

**Description**: Invalidates the current JWT by adding it to a blocklist and clears cookies.
**Auth Required**: Yes
**Request Body**: None (Uses Token from Header)
**Examples**:

1. **Successful Logout**: Token is invalid for future requests.
2. **Missing Token**: Returns 401 error.
3. **Expired Token**: Returns 401 error.

**Curl Command**:

```bash
curl -X POST http://localhost:5000/form/api/v1/auth/logout \
     -H "Authorization: Bearer <your_access_token>"
```

**Expected Output**:

```json
{
  "msg": "Successfully logged out"
}
```
