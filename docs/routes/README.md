# API Routes Documentation

This section provides a comprehensive reference for all available API routes in the AIOS Backend. Each module is documented in its own file to ensure clarity and depth.

## Modules

### Core Services

- **[Authentication](./auth.md)**: User registration, login, OTP generation, and logout.
- **[User Management](./user.md)**: Profile management, password reset, and administrative user CRUD operations.
- **[Dashboards](./dashboards.md)**: Configuration and data retrieval for administrative dashboards and widgets.
- **[Workflows](./workflows.md)**: Management of form approval cycles, states, and transition logic.

### Form Engine

- **[Form Management](./form/form.md)**: CRUD operations for form schemas, versioning, and status control.
- **[Responses](./form/responses.md)**: Submission handling, draft management, and response updates.
- **[AI Capabilities](./form/ai.md)**: Generation, analysis, and moderation powered by Large Language Models.
- **[Analytics & Export](./form/analytics.md)**: Data aggregation, summary statistics, and CSV/Excel exports.
- **[Validation Rules](./form/validation.md)**: Advanced data integrity checks and complex validation logic.

## Common Standards

### Success Response Format

Standard JSON responses follow this pattern:

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### Error Response Format

When an error occurs, the API returns an appropriate HTTP status code and a JSON error body:

```json
{
  "success": false,
  "error": "Short error code",
  "message": "Human-readable explanation of what went wrong",
  "details": { ... }
}
```

### HTTP Status Codes

- `200 OK`: Request succeeded.
- `201 Created`: Resource successfully created.
- `400 Bad Request`: Validation failure or malformed request.
- `401 Unauthorized`: Authentication token missing or invalid.
- `403 Forbidden`: Authenticated user lacks sufficient permissions.
- `404 Not Found`: Requested resource does not exist.
- `409 Conflict`: Conflict with current state (e.g., duplicate slug).
- `500 Internal Server Error`: An unexpected error occurred on the server.
