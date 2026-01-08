# Checklist: Database Migration Failure Evidence

**Purpose:** Collect diagnostic evidence for database migration failures
**When to use:** When Alembic, Flask-Migrate, or other migration tools fail
**Prerequisites:** Database access, migration tool installed
**Estimated time:** 5-10 minutes

---

## CRITICAL: Collect ALL Evidence Before Fixing

Do NOT skip any section. Incomplete evidence leads to wrong diagnosis.

---

## Section A: Migration Status

### Commands to Run
```bash
# For Alembic
alembic current
alembic history
alembic heads

# For Flask-Migrate
flask db current
flask db history
flask db heads

# For Django
python manage.py showmigrations
```

### Expected Information
- [ ] Current migration version
- [ ] Target migration version
- [ ] Migration history
- [ ] Multiple heads (if any)

### Red Flags
- ❌ Multiple heads detected
- ❌ Current version not in history
- ❌ No migrations found

---

## Section B: Migration Error

### Commands to Run
```bash
# Try the migration and capture error
alembic upgrade head 2>&1 | tee migration_error.log

# Show last 50 lines
tail -n 50 migration_error.log

# Check migration file
cat alembic/versions/xxxxx_description.py
```

### Expected Information
- [ ] Exact error message
- [ ] Which migration failed
- [ ] SQL statement that failed (if any)
- [ ] Line number in migration file

### Common Errors
- `relation "table" already exists` → Table exists
- `column "col" does not exist` → Schema drift
- `violates foreign key constraint` → Data issue
- `violates not-null constraint` → Missing data
- `duplicate key value` → Unique constraint violation

---

## Section C: Database State

### Commands to Run
```bash
# Connect to database
psql mydb
# OR
mysql -u user -p mydb

# List tables
\dt
# OR
SHOW TABLES;

# Describe specific table
\d tablename
# OR
DESCRIBE tablename;

# Check migration table
SELECT * FROM alembic_version;
# OR
SELECT * FROM django_migrations;
```

### Expected Information
- [ ] Database is accessible
- [ ] Migration tracking table exists
- [ ] Current schema documented
- [ ] Tables that should/shouldn't exist

### Red Flags
- ❌ Can't connect to database
- ❌ Migration table missing
- ❌ Schema doesn't match migrations
- ❌ Tables exist that shouldn't

---

## Section D: Migration File Analysis

### Commands to Run
```bash
# Show the failing migration
cat alembic/versions/xxxxx_migration.py

# Check for syntax errors
python -m py_compile alembic/versions/xxxxx_migration.py

# Compare with previous migration
diff alembic/versions/xxxxx_prev.py alembic/versions/xxxxx_current.py
```

### Expected Information
- [ ] Migration file is valid Python
- [ ] upgrade() function exists
- [ ] downgrade() function exists
- [ ] SQL statements are valid

### Red Flags
- ❌ Syntax error in migration
- ❌ Missing upgrade() or downgrade()
- ❌ Invalid SQL
- ❌ Conflicting changes

---

## Section E: Data Integrity

### Commands to Run
```bash
# Check for data that would violate new constraints
# Example: Adding NOT NULL to column with nulls
SELECT COUNT(*) FROM users WHERE email IS NULL;

# Example: Adding unique constraint with duplicates
SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1;

# Example: Foreign key constraint
SELECT COUNT(*) FROM posts WHERE user_id NOT IN (SELECT id FROM users);
```

### Expected Information
- [ ] No data violates new constraints
- [ ] No orphaned foreign keys
- [ ] No duplicate values where unique needed
- [ ] No nulls where NOT NULL needed

### Red Flags
- ❌ Null values in column getting NOT NULL
- ❌ Duplicate values in column getting UNIQUE
- ❌ Orphaned foreign key references

---

## Section F: Dependencies and Conflicts

### Commands to Run
```bash
# Check for migration conflicts
alembic branches

# Check migration dependencies
grep "down_revision" alembic/versions/*.py

# Check for circular dependencies
alembic history --verbose
```

### Expected Information
- [ ] No conflicting migrations
- [ ] Dependencies are correct
- [ ] No circular dependencies
- [ ] Linear migration path

### Red Flags
- ❌ Multiple branches
- ❌ Circular dependencies
- ❌ Missing down_revision

---

## Section G: Environment and Permissions

### Commands to Run
```bash
# Check database user permissions
psql -c "\du"

# Test connection
psql -h localhost -U dbuser -d mydb -c "SELECT 1"

# Check if user can create tables
psql -c "CREATE TABLE test_permissions (id INT); DROP TABLE test_permissions;"
```

### Expected Information
- [ ] Database user has required permissions
- [ ] Can connect to database
- [ ] Can create/alter tables
- [ ] Can create/drop indexes

### Red Flags
- ❌ Permission denied
- ❌ Can't connect
- ❌ Can't create tables
- ❌ Can't alter schema

---

## Section H: Common Root Causes Checklist

Based on evidence, check which applies:

- [ ] **Multiple heads** (conflicting migrations)
- [ ] **Schema drift** (database doesn't match migrations)
- [ ] **Table already exists** (migration run twice)
- [ ] **Data constraint violation** (existing data violates new constraint)
- [ ] **Foreign key violation** (orphaned references)
- [ ] **Permission denied** (user can't alter schema)
- [ ] **Syntax error** (invalid SQL in migration)
- [ ] **Missing dependency** (migration depends on unapplied migration)
- [ ] **Circular dependency** (migrations reference each other)
- [ ] **Database locked** (another process holding lock)

---

## Output Summary

After collecting all evidence, write a 10-line summary:

```
DIAGNOSIS SUMMARY
=================
Migration Tool: [Alembic/Flask-Migrate/Django]
Failed Migration: [version/name]
Error Type: [constraint/syntax/permission/etc]

Root Cause (most likely): [specific cause]
Evidence: [key evidence]

Recommended Fix: [specific action]
Data Impact: [none/low/high]
Risk Level: [low/medium/high]
```

---

## Validation

Before proceeding to fix:
- [ ] All sections A-H completed
- [ ] Root cause identified
- [ ] Evidence supports diagnosis
- [ ] Backup created (production)
- [ ] Fix is clear

**If any checkbox is unchecked → Collect more evidence.**

---

## See Also

- [`../workflows/db_migrations.md`](../workflows/db_migrations.md) - Fix workflow
- [`../skills/alembic_migrations.md`](../skills/alembic_migrations.md) - Migration guide
- [`../policy/PRODUCTION_POLICY.md`](../policy/PRODUCTION_POLICY.md) - Safety rules
