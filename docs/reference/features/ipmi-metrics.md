# IPMI Metrics

### Prometheus-IPMI-Exporter

We've added the ability to export metrics from the IPMI interface of your systems. This uses the existing prometheus-ipmi-exporter project. For now, the configuration is somewhat manual, and will be more integrated in the future.

Example defaults.yml snippet:

```
prometheus_ipmi_exporter_modules:
  - name: default
    user: <IPMI_USER>
    password: <IPMI_PASSWORD>
    collectors:
      - bmc
      - ipmi
      - chassis
    endpoints:
      - <node1_bmc_ip_address>
      - <node2_bmc_ip_address>
      - ...
```
