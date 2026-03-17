# audit_tables

Deploys MySQL audit tables and triggers in the `openstack_audit` database.
Each audit table captures state-change snapshots (as JSON) from a source
OpenStack table, enabling interval-based capacity reporting.

## Configuration

Each audit table has a boolean toggle and a list entry:

```yaml
audit_blazar_computehosts: true

audit_tables:
  - name: blazar_computehosts
    source_db: blazar
    source_table: computehosts
    grant_user: blazar
    enabled: "{{ audit_blazar_computehosts }}"
    columns:          # source columns to capture
      - id
      - status
      - reservable
      - ...
    watch_columns:    # only fire UPDATE trigger when these change
      - status
      - reservable
      - disabled
```

An operator sets `audit_blazar_computehosts: false` in site-config to disable.

## Disabling triggers

Set the boolean to `false` and re-run the playbook. This drops all three
triggers (insert, update, delete). The audit table and its data are left
intact — audit history is never deleted by this role.

To re-enable, set back to `true` and re-run.

**Before OpenStack upgrades**: disable all audit triggers, run the upgrade,
then review and re-enable. Triggers that reference dropped or renamed source
columns will cause transaction failures.

## Adding a new audit table

Add a boolean toggle and list entry to `defaults/main.yml` (or override in
site-config). The shared template (`audit_table.sql.j2`) generates the
schema and triggers from the config. No new files needed.

## Audit table schema

All audit tables share the same structure:

| Column | Type | Description |
|--------|------|-------------|
| `audit_id` | INT AUTO_INCREMENT | Primary key |
| `id` | VARCHAR(36) | Source entity ID (indexed) |
| `audit_event_type` | ENUM | INSERT, UPDATE, or DELETE |
| `audit_changed_by` | VARCHAR(255) | MySQL user that triggered the change |
| `audit_changed_at` | TIMESTAMP | When the audit row was created |
| `data` | JSON | Snapshot of configured `columns` at change time |
