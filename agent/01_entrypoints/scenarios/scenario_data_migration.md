# Scenario: Data Migration & Schema Evolution

## Purpose

Safely evolving database schemas or data formats without losing existing data or breaking production systems.

## Inputs

- Proposed schema change (new column, renamed table, data type change).
- Existing production database or data files.

## Planning Phase (Adopt `profile_architect.md`)

1. **Impact Analysis**:
   - Identify all queries, ORM models, and API endpoints that reference the affected schema.
   - Estimate the volume of data to be migrated.
2. **Migration Strategy Selection**:
   - **Additive**: Add new columns/tables without removing old ones (safest).
   - **Dual-Write**: Write to both old and new schemas during transition.
   - **Big-Bang**: One-time migration (highest risk).
3. **Rollback Plan**: Define how to revert if the migration fails mid-execution.

## Implementation Phase (Adopt `profile_implementer.md`)

1. **Backup First**: Create a full database backup or snapshot.
2. **Migration Script**: Write idempotent SQL/migration code (can be run multiple times safely).
3. **Staging Test**: Run the migration on a copy of production data in a staging environment.
4. **Validation Queries**: Write SQL queries to verify data integrity post-migration.

## Execution Phase (Adopt `profile_security_auditor.md`)

1. **Maintenance Window**: Schedule the migration during low-traffic periods.
2. **Monitoring**: Watch for errors, slow queries, and data corruption.
3. **Incremental Rollout**: If possible, migrate data in batches rather than all at once.

## Verification Phase (Adopt `profile_tester.md`)

1. **Data Integrity Check**: Run checksums or row counts to ensure no data loss.
2. **Application Testing**: Run the full test suite against the new schema.
3. **Performance Audit**: Ensure queries are not slower after migration.

## STOP Condition

- Migration is complete, all tests pass, and the rollback plan is documented.

## Related Files

- `agent/05_gates/global/gate_global_quality.md`
- `agent/10_security/data_classification.md`
