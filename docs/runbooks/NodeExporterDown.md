**Summary**: A metrics exporter can no longer be scraped.

**Consequences**: When exporters are no longer scraped, the amount of metrics available to monitoring decrease; this creates a blind spot with respect to failures. Sometimes this alert can indicate the entire host has lost connectivity, as Prometheus exporters communicate via HTTP interfaces.

### Possible causes

If the exporter was explicitly removed or its scrape job in Prometheus was renamed, then the alert is expected, and benign. However, there are two other primary causes:

**The exporter failed**: Check to see if the exporter process (usually a Docker container named `*_exporter`, but in the case of `node_exporter`, a systemd service) has failed or is logging errors.

**The host has lost connectivity**: Check if the host running the exporter has lost connectivity. The `hostname` label should indicate which host the exporter was running on.