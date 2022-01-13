**Summary**: The MySQL process is no longer reporting metrics. This can mean the process has failed, it no longer has networking, or the monitoring is misconfigured.

**Consequences**: If the MySQL process is indeed down or unreachable, then most of the system will not be operational. If this is the case, other alerts will likely fire around OpenStack APIs being down, amongst others. If no other alerts are firing, it's possible it is only a monitoring misconfiguration. Restoring a down or unreachable MySQL process should be a high-priority item in the event of an outage as most systems rely on it.

### Possible causes

**The MySQL process has failed**:

1. Log in to the MySQL host and check either the systemd service (`systemctl status mariadb`) or the Docker container `docker inspect mariadb`.
1. If it is down, investigate the logs (`/var/log/mariadb/mariadb.log` or `docker logs mariadb`) for hints. If it is up, check out the other possible causes.

**Routing to MySQL has failed**: It is possible that the service is up, but HAProxy is failing to route traffic.

1. Check HAProxy logs (`/var/log/kolla/haproxy`) for errors.
1. See if MySQL responds to a local IP, but not the VIP assigned by keepalive (the value of `kolla_internal_vip_address`); if that is the case, the issue could be HAProxy; it could be missing configuration instructing it to route traffic to MySQL (this might happen during an upgrade).

**Monitoring has failed**: If everything seems fine, yet the alert is firing, the issue is likely with the monitoring.

1. Check if the `mysqld_exporter` container is running, and if any errors are logged. If the username/password for the monitoring user has changed, or if the bind address changes, the Prometheus exporter will be unable to connect.
1. Re-run the Prometheus playbook `./cc-ansible --playbook playbooks/prometheus.yml` to re-deploy the monitoring infrastructure.