# Dashboards API

## Overview

The Dashboards API provides a dynamic configuration layer for building and rendering administrative visualizations within the AIOS system. It allows administrators to define **Dashboard documents** containing ordered lists of **Widgets**, such as counters, list views, and aggregated charts. Each widget can be linked to a specific form or a "Saved Search" filter, enabling real-time monitoring of form responses and system health. The module automates the fetching of data for all widgets in a single call, ensuring a responsive and unified experience for managers monitoring multiple data streams. Access is strictly controlled through **Role-Based Access Control (RBAC)**, ensuring users only see dashboards relevant to their permissions.

## Base URL

`/form/api/v1/dashboards`

## Endpoints

### POST /

**Description**: Creates a new dashboard configuration with a title, slug, and a defined set of widgets.
**Auth Required**: Yes (Admin/Superadmin only)
**Request Body**:

```json
{
  "title": "Operation Overview",
  "slug": "op-overview",
  "description": "Daily monitoring dashboard",
  "roles": ["admin", "creator"],
  "layout": "grid",
  "widgets": [
    {
      "title": "Total Submissions",
      "type": "counter",
      "form_id": "60d5f...",
      "size": "small"
    }
  ]
}
```

**Examples**:

1. **New Dashboard**: Successfully creating a management view.
2. **Duplicate Slug**: Returns 409 Conflict error.
3. **Invalid Form ID**: Fails if the referenced form does not exist.

**Curl Command**:

```bash
curl -X POST http://localhost:5000/form/api/v1/dashboards/ \
     -H "Authorization: Bearer <admin_token>" \
     -H "Content-Type: application/json" \
     -d '{
           "title": "Feedback Stats",
           "slug": "feedback-stats",
           "widgets": [{"title": "Count", "type": "counter", "form_id": "607d..."}]
         }'
```

**Expected Output**:

```json
{
  "message": "Dashboard created",
  "id": "60d..."
}
```

---

### GET /

**Description**: Lists all dashboards accessible to the current user based on their roles.
**Auth Required**: Yes
**Examples**:

1. **Manager View**: Returns a list of assigned operational dashboards.
2. **Empty List**: Returns `[]` if no dashboards match user roles.
3. **Admin View**: Retrieves all system dashboards.

**Curl Command**:

```bash
curl -X GET http://localhost:5000/form/api/v1/dashboards/ \
     -H "Authorization: Bearer <token>"
```

**Expected Output**:

```json
[
  {
    "id": "60d...",
    "title": "Operation Overview",
    "slug": "op-overview",
    "description": "Daily monitoring dashboard",
    "role_count": 2
  }
]
```

---

### GET /<slug>

**Description**: Fetches the full configuration and current data for all widgets in the specified dashboard.
**Auth Required**: Yes
**Examples**:

1. **Dashboard Load**: Retrieves layout and widget data (e.g., current submission counts).
2. **Unauthorized**: Returns 403 if user lacks a required role for the dashboard.
3. **Not Found**: Returns 404 if the slug does not exist.

**Curl Command**:

```bash
curl -X GET http://localhost:5000/form/api/v1/dashboards/op-overview \
     -H "Authorization: Bearer <token>"
```

**Expected Output**:

```json
{
  "id": "60d...",
  "title": "Operation Overview",
  "layout": "grid",
  "widgets": [
    {
      "id": "...",
      "title": "Total Submissions",
      "type": "counter",
      "data": 150,
      "config": {}
    }
  ]
}
```

---
*Note: Counter widgets perform real-time count queries, while list views return the latest 5 records by default.*
