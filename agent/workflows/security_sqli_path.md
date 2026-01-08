# Workflow: SQL Injection & Path Traversal

**Purpose:** Detect and fix SQL injection and path traversal vulnerabilities
**When to use:** Security audit, suspicious activity, or preventive hardening
**Prerequisites:** Access to codebase, security tools
**Estimated time:** 30-60 minutes
**Outputs:** Secured code, test cases

---

## Prerequisites

- [ ] Access to codebase
- [ ] Can run tests
- [ ] Security scanner available (optional)

---

## Step 1: Detect Vulnerabilities

### Scan for SQL Injection
```bash
# Search for string concatenation in SQL
grep -r "f\"SELECT\|f'SELECT" app/
grep -r '+ "SELECT' app/
grep -r ".format(" app/ | grep -i "select\|insert\|update"

# Look for execute without parameters
grep -r ".execute(f\"\|.execute(\".*%s" app/
```

### Scan for Path Traversal
```bash
# Search for file operations with user input
grep -r "open(.*request\|open(.*input" app/
grep -r "os.path.join.*request" app/
grep -r "\.\./" app/

# Check file upload handlers
grep -r "save.*filename" app/
```

---

## Step 2: Fix SQL Injection

### Use Parameterized Queries
```python
# ❌ VULNERABLE
user_id = request.args.get('id')
query = f"SELECT * FROM users WHERE id = {user_id}"
result = db.execute(query)

# ✅ SAFE
user_id = request.args.get('id')
query = "SELECT * FROM users WHERE id = %s"
result = db.execute(query, (user_id,))
```

### Use ORM
```python
# ✅ SAFE (SQLAlchemy)
user = User.query.filter_by(id=user_id).first()
```

---

## Step 3: Fix Path Traversal

### Validate and Sanitize Paths
```python
# ❌ VULNERABLE
filename = request.args.get('file')
with open(f'/uploads/{filename}') as f:
    content = f.read()

# ✅ SAFE
import os
filename = request.args.get('file')
# Remove any path components
filename = os.path.basename(filename)
# Build safe path
filepath = os.path.join('/uploads', filename)
# Verify it's still in uploads directory
if not os.path.abspath(filepath).startswith('/uploads'):
    raise ValueError("Invalid file path")
with open(filepath) as f:
    content = f.read()
```

### Use Allowlist
```python
# ✅ SAFE
ALLOWED_FILES = {'report.pdf', 'data.csv'}
filename = request.args.get('file')
if filename not in ALLOWED_FILES:
    raise ValueError("File not allowed")
```

---

## Step 4: Add Tests

### Test SQL Injection Prevention
```python
def test_sql_injection_prevented():
    """Ensure SQL injection is blocked"""
    malicious_input = "1 OR 1=1"
    response = client.get(f'/api/user?id={malicious_input}')
    # Should not return all users
    assert response.status_code in [400, 404]
```

### Test Path Traversal Prevention
```python
def test_path_traversal_prevented():
    """Ensure path traversal is blocked"""
    malicious_path = "../../../etc/passwd"
    response = client.get(f'/files?name={malicious_path}')
    assert response.status_code in [400, 403, 404]
```

---

## Step 5: Verify

```bash
# Run tests
pytest tests/security/ -v

# Run security scanner (if available)
bandit -r app/
# or
safety check
```

---

## Completion Criteria

- ✅ All SQL queries use parameterization or ORM
- ✅ All file operations validate paths
- ✅ Security tests added and passing
- ✅ Code review completed

---

## See Also

- [`../workflows/security_incident.md`](security_incident.md)
- [`../workflows/feature_delivery.md`](feature_delivery.md)
