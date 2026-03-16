# audit_tables

Deploys MySQL audit tables and triggers in the `openstack_audit` database.
Each audit table captures state-change snapshots from a source OpenStack table,
enabling accurate interval-based capacity reporting.

## Configuration

Each audit table has a boolean toggle and a list entry:

```yaml
audit_blazar_computehosts: true

audit_tables:
  - name: blazar_computehosts
    source_db: blazar
    source_table: computehosts
    enabled: "{{ audit_blazar_computehosts }}"
```

An operator sets `audit_blazar_computehosts: false` in site-config to disable.

## Disabling triggers

Set the boolean to `false` and re-run the playbook. This drops all three
triggers (insert, update, delete). The audit table and its data are left
intact — audit history is never deleted by this role.

To re-enable, set back to `true` and re-run.

## Adding a new audit table

1. Write `files/audit_<name>.sql` containing the CREATE TABLE, GRANT, and
   trigger statements. Separate statements with `-- ---` (a SQL comment
   used as a delimiter). Schema changes to existing tables require a manual
   migration — `CREATE TABLE IF NOT EXISTS` does not alter existing columns.
2. Add a boolean toggle and list entry to `defaults/main.yml`.

Trigger naming convention: `trg_<source_table>_audit_{ins,upd,del}`.
