# Monitoring

## Sending metrics, logs and alerts to Chameleon

A site can send its metrics, logs and alerts to Chameleon's central services. Each is off by default and is turned on separately in `site-config/defaults.yml`.

| Variable | Default | Effect when `true` |
|---|---|---|
| `upload_metrics_chameleon` | `false` | Prometheus sends all metrics to `prometheus_remote_write_url`. |
| `upload_logs_chameleon` | `false` | Fluentd sends all logs to `loki_url`. |
| `upload_alerts_chameleon` | `false` | Kolla-Ansible doesn't deploy a local Alertmanager. The site's Prometheus still evaluates the alert rules and sends alerts to `prometheus_alertmanager_remote_url`. |

With `upload_alerts_chameleon` on, the notification settings in `prometheus-alertmanager.yml` and `slack.tmpl` aren't used. Routing and notifications are configured on the central Alertmanager.

### Endpoints and credentials

| Variable | Default |
|---|---|
| `mimir_url` | `https://metrics.chameleoncloud.org` |
| `prometheus_remote_write_url` | `{{ mimir_url }}/api/v1/push` |
| `prometheus_alertmanager_remote_url` | `{{ mimir_url }}/alertmanager` |
| `loki_url` | `https://logs.chameleoncloud.org` |
| `prometheus_remote_write_username` | `{{ keystone_idp_client_id }}` |
| `prometheus_remote_write_password` | No default. Set it in `site-config/passwords.yml`. |

Metrics, logs and alerts all use the same username and password. To point metrics and alerts at a different Mimir, change `mimir_url`; overriding only `prometheus_remote_write_url` moves metrics but not alerts.

### Site labels

Every metric and alert from a site carries these labels, set from the variables of the same name:

- `kolla_external_fqdn`
- `keystone_idp_client_id`
- `openstack_region_name`
- `chameleon_site_name`

Logs sent to Loki carry the same labels.
