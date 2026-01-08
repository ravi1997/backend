# Skill: Alembic Migrations

**Purpose:** Work with Alembic database migrations
**When to use:** Creating, applying, or troubleshooting database migrations
**Prerequisites:** Alembic installed, database configured
**Estimated time:** 10-30 minutes

---

## Common Operations

### Create New Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description of changes"

# Create empty migration
alembic revision -m "description"

# Review generated migration
cat alembic/versions/xxxxx_description.py
```

**Always review auto-generated migrations!** They may miss:
- Data migrations
- Index changes
- Constraint changes

---

### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Upgrade to specific version
alembic upgrade abc123

# Check current version
alembic current

# Show migration history
alembic history
```

---

### Rollback Migrations

```bash
# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade abc123

# Downgrade to base (all down)
alembic downgrade base
```

---

## Common Issues

### Issue 1: Multiple Heads

**Symptom:** `Multiple heads detected`

**Cause:** Conflicting migrations from different branches

**Fix:**
```bash
# Show heads
alembic heads

# Merge heads
alembic merge heads -m "merge migrations"

# Apply merge
alembic upgrade head
```

---

### Issue 2: Schema Drift

**Symptom:** Database doesn't match migrations

**Diagnosis:**
```bash
# Check for drift
alembic check

# Show current version
alembic current

# Compare with database
```

**Fix:**
```bash
# Option 1: Create migration to fix drift
alembic revision --autogenerate -m "fix schema drift"

# Option 2: Stamp database to current
alembic stamp head  # DANGEROUS - only if you're sure
```

---

### Issue 3: Migration Fails

**Symptom:** `alembic upgrade` fails with error

**Common Causes:**
- Constraint violation
- Data incompatibility
- Missing column
- Duplicate key

**Fix:**
```bash
# Rollback
alembic downgrade -1

# Fix migration file
nano alembic/versions/xxxxx_migration.py

# Try again
alembic upgrade head
```

---

### Issue 4: Can't Downgrade

**Symptom:** Downgrade fails or not implemented

**Cause:** Missing `downgrade()` function

**Fix:**
```python
# In migration file
def downgrade():
    # Add reverse operations
    op.drop_table('new_table')
    op.drop_column('users', 'new_column')
```

---

## Best Practices

### 1. Always Test Migrations

```bash
# Test upgrade
alembic upgrade head

# Test downgrade
alembic downgrade -1

# Test upgrade again
alembic upgrade head
```

### 2. Backup Before Migration

```bash
# PostgreSQL
pg_dump mydb > backup_before_migration.sql

# MySQL
mysqldump mydb > backup_before_migration.sql
```

### 3. Review Auto-Generated Migrations

Check for:
- Missing indexes
- Data migrations needed
- Constraint changes
- Default values

### 4. Use Transactions

```python
# In migration file
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Migrations run in transaction by default
    op.add_column('users', sa.Column('email', sa.String(255)))
```

---

## Migration File Structure

```python
"""description of changes

Revision ID: abc123
Revises: xyz789
Create Date: 2024-01-01 12:00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123'
down_revision = 'xyz789'
branch_labels = None
depends_on = None

def upgrade():
    # Add changes here
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(255), nullable=False)
    )

def downgrade():
    # Reverse changes here
    op.drop_table('users')
```

---

## Troubleshooting Checklist

- [ ] Check current version: `alembic current`
- [ ] Check for multiple heads: `alembic heads`
- [ ] Check migration history: `alembic history`
- [ ] Verify database connection
- [ ] Check for schema drift: `alembic check`
- [ ] Review migration file for errors
- [ ] Test in development first
- [ ] Backup database before applying

---

## See Also

- [`../workflows/db_migrations.md`](../workflows/db_migrations.md)
- [`../checklists/MIGRATION_FAIL_EVIDENCE.md`](../checklists/MIGRATION_FAIL_EVIDENCE.md)
