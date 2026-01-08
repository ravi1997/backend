# Workflow: Database Migrations

**Purpose:** Handle database migration issues (Alembic, Flask-Migrate, etc.)
**When to use:** When migrations fail, conflict, or need rollback
**Prerequisites:** Database access, migration tool installed
**Estimated time:** 20-40 minutes
**Outputs:** Successful migration, updated schema

---

## Prerequisites

- [ ] Database connection working
- [ ] Migration tool installed (Alembic/Flask-Migrate)
- [ ] Backup exists (production only)
- [ ] Environment detected
- [ ] If production → `policy/PRODUCTION_POLICY.md`

---

## Step 1: Diagnose the Issue

### Check Migration Status
```bash
# Alembic
alembic current
alembic history

# Flask-Migrate
flask db current
flask db history
```

### Common Issues

**A) Migration Conflict**
```bash
# Multiple heads detected
alembic heads
# Fix: Merge heads
alembic merge heads -m "merge migrations"
```

**B) Schema Drift**
```bash
# Database doesn't match migrations
alembic check
# Fix: Create new migration or manual SQL
```

**C) Failed Migration**
```bash
# Check logs for error
# Common: constraint violation, type mismatch
```

---

## Step 2: Apply Fix

### For New Migration
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Review generated file
cat alembic/versions/xxxxx_description.py

# Test upgrade
alembic upgrade head

# Test downgrade
alembic downgrade -1
alembic upgrade head
```

### For Failed Migration
```bash
# Rollback to previous
alembic downgrade -1

# Fix the migration file
# ... edit ...

# Try again
alembic upgrade head
```

---

## Step 3: Verify

```bash
# Check current version
alembic current

# Verify schema
# Connect to DB and check tables

# Run application tests
pytest tests/
```

---

## Completion Criteria

- ✅ Migration completes successfully
- ✅ Database schema matches expected
- ✅ Application starts without errors
- ✅ Tests pass

---

## Rollback Plan

```bash
# Downgrade one version
alembic downgrade -1

# Or to specific version
alembic downgrade <revision>

# Restore from backup (production)
# ... restore commands ...
```

---

## See Also

- [`../checklists/MIGRATION_FAIL_EVIDENCE.md`](../checklists/MIGRATION_FAIL_EVIDENCE.md)
- [`../skills/alembic_migrations.md`](../skills/alembic_migrations.md)
