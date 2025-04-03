**Summary**: A periodic task has not had a successful run recently.

**Consequences**: Periodic tasks serve many purposes so the impact depends on the task, though typically is limited in user impact. Most tasks are responsible for cleaning up testbed state; over time if these jobs are left failing, users may experience nodes that cannot be provisioned. Tasks are also involved in creating backups of data, and if they stop working, the ability to restore from backups diminishes.

### Possible causes

**Authentication errors**: Many jobs interface with OpenStack APIs, and user a special user for this. If this user is changed or disabled, jobs can fail.

1. Try running the failing job manually (see its entry via `systemctl show <task>`) to see what type of error is generated. If it is an authentication error, see if the user (defined as the `hammers_openstack_user` var) is disabled/missing.

**Runtime error**: A job may encounter input is unfamiliar with. The code for the job will have to be fixed; an issue should be raised for this.

### Task-specific runbooks

#### `keycloak_tas_sync`

If the sync is running for a while but then encounters a 401 unauthorized error, it can be because the service account's token has too short of an expiration. The current configured TTL is in the configuration for the "user-group-import" client in the master Keycloak realm as an advanced setting (Access Token Lifespan).