# Dashboard API Quick Reference

**Last Updated**: February 11, 2026
**Developer**: Marcus Torres, Senior Backend Engineer

---

## Base URL

```
http://localhost:5000/form/api/v1/dashboards
```

---

## Endpoints Summary

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| POST | `/` | ✅ | Admin | Create dashboard |
| GET | `/` | ✅ | Any | List accessible dashboards |
| GET | `/{slug}` | ✅ | Role-based | Get dashboard with data |
| PUT | `/{id}` | ✅ | Admin | Update dashboard |

---

## 1. Create Dashboard

### Request

```http
POST /form/api/v1/dashboards/
Authorization: Bearer {ADMIN_TOKEN}
Content-Type: application/json
```

```json
{
  "title": "DEO Dashboard",
  "slug": "deo-home",
  "description": "Main dashboard for DEOs",
  "roles": ["deo"],
  "layout": "grid",
  "widgets": [
    {
      "title": "Total Submissions",
      "type": "counter",
      "form_id": "65abc123...",
      "size": "medium",
      "refresh_interval": 300
    },
    {
      "title": "Recent Entries",
      "type": "list_view",
      "form_id": "65abc123...",
      "size": "large",
      "display_columns": ["id", "submitted_at"]
    },
    {
      "title": "Create Form",
      "type": "shortcut",
      "target_link": "/forms/create",
      "size": "small"
    }
  ]
}
```

### Response (201 Created)

```json
{
  "message": "Dashboard created",
  "id": "65def456..."
}
```

### Errors

- `400`: Missing required fields
- `409`: Slug already exists
- `403`: Not admin/superadmin

---

## 2. List Dashboards

### Request

```http
GET /form/api/v1/dashboards/
Authorization: Bearer {TOKEN}
```

### Response (200 OK)

```json
[
  {
    "id": "65abc123...",
    "title": "DEO Dashboard",
    "slug": "deo-home",
    "description": "Main dashboard for DEOs",
    "role_count": 1
  },
  {
    "id": "65def456...",
    "title": "Admin Dashboard",
    "slug": "admin-dashboard",
    "description": "Admin overview",
    "role_count": 2
  }
]
```

### Access Rules

- **Admin/Superadmin**: See ALL dashboards
- **Other Users**: See only dashboards where their role ∈ dashboard.roles

---

## 3. Get Dashboard Data

### Request

```http
GET /form/api/v1/dashboards/{slug}
Authorization: Bearer {TOKEN}
```

**Example**:
```http
GET /form/api/v1/dashboards/deo-home
Authorization: Bearer eyJhbGc...
```

### Response (200 OK)

```json
{
  "id": "65abc123...",
  "title": "DEO Dashboard",
  "layout": "grid",
  "widgets": [
    {
      "id": "widget_1",
      "title": "Total Submissions",
      "type": "counter",
      "size": "medium",
      "config": {},
      "data": 142,
      "layout_props": {
        "cols": []
      }
    },
    {
      "id": "widget_2",
      "title": "Recent Entries",
      "type": "list_view",
      "size": "large",
      "config": {},
      "data": [
        {
          "id": "resp_1",
          "submitted_at": "2026-02-11T10:00:00Z",
          "data": {
            "field_1": "value_1"
          }
        }
      ],
      "layout_props": {
        "cols": ["id", "submitted_at"]
      }
    },
    {
      "id": "widget_3",
      "title": "Create Form",
      "type": "shortcut",
      "size": "small",
      "config": {},
      "data": null,
      "layout_props": {
        "cols": []
      }
    }
  ]
}
```

### Widget Data Formats

#### Counter Widget
```json
{
  "type": "counter",
  "data": 142
}
```

#### List View Widget
```json
{
  "type": "list_view",
  "data": [
    {
      "id": "response_id",
      "submitted_at": "ISO8601_timestamp",
      "data": {...}
    }
  ]
}
```

#### Shortcut Widget
```json
{
  "type": "shortcut",
  "data": null
}
```

### Errors

- `404`: Dashboard slug not found
- `403`: User role not in dashboard.roles

---

## 4. Update Dashboard

### Request

```http
PUT /form/api/v1/dashboards/{id}
Authorization: Bearer {ADMIN_TOKEN}
Content-Type: application/json
```

**Example**:
```http
PUT /form/api/v1/dashboards/65abc123...
Authorization: Bearer eyJhbGc...
```

### Request Body (All Optional)

```json
{
  "title": "Updated Dashboard Title",
  "description": "New description",
  "roles": ["admin", "deo", "editor"],
  "layout": "grid",
  "widgets": [
    {
      "title": "New Widget",
      "type": "counter",
      "form_id": "65xyz789..."
    }
  ]
}
```

### Response (200 OK)

```json
{
  "message": "Dashboard updated"
}
```

### Errors

- `404`: Dashboard ID not found
- `403`: Not admin/superadmin

### Important Notes

- ⚠️ Updating `widgets` replaces the ENTIRE widget array
- Partial widget updates not supported (must send full array)

---

## Widget Types

### Counter

**Purpose**: Display count of responses

```json
{
  "type": "counter",
  "form_id": "form_id_here",
  "aggregation_field": null
}
```

**Data**: Integer count

---

### List View

**Purpose**: Display recent submissions

```json
{
  "type": "list_view",
  "form_id": "form_id_here",
  "display_columns": ["id", "submitted_at", "data"]
}
```

**Data**: Array of response objects (max 5)

---

### Chart Bar/Pie

**Purpose**: Data visualization

```json
{
  "type": "chart_bar",
  "form_id": "form_id_here",
  "config": {
    "x_axis": "field_name",
    "y_axis": "count"
  }
}
```

**Status**: 🚧 Data fetching not yet implemented

---

### Shortcut

**Purpose**: Quick navigation

```json
{
  "type": "shortcut",
  "target_link": "/forms/create"
}
```

**Data**: null (frontend handles navigation)

---

## Widget Sizes

| Size | Description |
|------|-------------|
| `small` | 1/4 width |
| `medium` | 1/2 width (default) |
| `large` | 3/4 width |
| `full_width` | Full width |

---

## Role-Based Access Examples

### Admin Creates Dashboard for DEOs

```bash
curl -X POST http://localhost:5000/form/api/v1/dashboards/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "DEO Dashboard",
    "slug": "deo-home",
    "roles": ["deo"],
    "widgets": [...]
  }'
```

### DEO Views Dashboard

```bash
curl -X GET http://localhost:5000/form/api/v1/dashboards/deo-home \
  -H "Authorization: Bearer DEO_TOKEN"
```

**Result**: ✅ Access granted (DEO role in dashboard.roles)

### User Views Dashboard

```bash
curl -X GET http://localhost:5000/form/api/v1/dashboards/deo-home \
  -H "Authorization: Bearer USER_TOKEN"
```

**Result**: ❌ 403 Forbidden (User role not in dashboard.roles)

---

## Common Use Cases

### 1. Create Multi-Role Dashboard

```json
{
  "title": "Management Dashboard",
  "slug": "management",
  "roles": ["admin", "editor", "publisher"],
  "widgets": [...]
}
```

All users with admin, editor, OR publisher roles can access.

---

### 2. Create Personal Dashboard

```json
{
  "title": "My Dashboard",
  "slug": "user-{user_id}",
  "roles": ["user"],
  "widgets": [...]
}
```

All authenticated users can access (everyone has "user" role).

---

### 3. Admin-Only Dashboard

```json
{
  "title": "System Admin Dashboard",
  "slug": "system-admin",
  "roles": ["superadmin"],
  "widgets": [...]
}
```

Only superadmins can access.

---

## Testing

### Quick Test Script

```bash
# 1. Get admin token
ADMIN_TOKEN=$(curl -s -X POST http://localhost:5000/form/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"Admin123!"}' \
  | jq -r '.access_token')

# 2. Create dashboard
curl -X POST http://localhost:5000/form/api/v1/dashboards/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Dashboard",
    "slug": "test-dash",
    "roles": ["admin"]
  }'

# 3. List dashboards
curl -X GET http://localhost:5000/form/api/v1/dashboards/ \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# 4. Get dashboard data
curl -X GET http://localhost:5000/form/api/v1/dashboards/test-dash \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## Integration Test

Full integration test available at:
```
/home/programmer/Desktop/backend/test_dashboard_integration.py
```

**Run**:
```bash
cd /home/programmer/Desktop/backend
python3 test_dashboard_integration.py
```

---

## Status

| Endpoint | Status | Tests |
|----------|--------|-------|
| POST / | ✅ Complete | ✅ Passing |
| GET / | ✅ Complete | ✅ Passing |
| GET /{slug} | ✅ Complete | ✅ Passing |
| PUT /{id} | ✅ Complete | ✅ Passing |

**Module Status**: ✅ **Production Ready**

---

## Related Documentation

- **Full Documentation**: `/home/programmer/Desktop/backend/DASHBOARD_MODULE_DOCUMENTATION.md`
- **SRS Requirements**: `/home/programmer/Desktop/backend/SRS.md` (FR-DASH-001, FR-DASH-002)
- **Model Definition**: `/home/programmer/Desktop/backend/app/models/Dashboard.py`
- **Route Implementation**: `/home/programmer/Desktop/backend/app/routes/v1/dashboard_route.py`
- **Unit Tests**: `/home/programmer/Desktop/backend/tests/test_dashboard.py`

---

**End of Quick Reference**
