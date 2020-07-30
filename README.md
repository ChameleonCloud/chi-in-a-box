# chi-in-a-box

![chi-in-a-box](./chi-in-a-box.png)

CHI-in-a-box is a packaging of the implementation of the core services that together constitute the [Chameleon testbed](https://www.chameleoncloud.org/) for experimental Computer Science research. These services allow Chameleon users to discover information about Chameleon resources, allocate those resources for present and future use, configure them in various ways, and monitor various types of metrics.

### Currently included with CHI-in-a-Box:

- Custom OpenStack deployment optimized for bare metal reservations and provisioning, including the following OpenStack services by default:
  - Ironic (bare metal deployment)
  - Blazar (advanced reservation)
  - Nova (instance deployment in conjunction w/ Ironic)
    - Includes custom vendordata service for automatic experiment metrics collection
  - Neutron (networking)
  - Glance (disk image storage)
  - Gnocchi (timeseries storage for experiment metrics)
  - Keystone (authentication and authorization)
  - Heat (orchestration)
- [Experiment Precis](https://chameleoncloud.readthedocs.io/en/latest/technical/ep.html)
- [JupyterHub](https://jupyterhub.readthedocs.io/en/stable/) with Keystone integration
- [Prometheus](https://prometheus.io/) monitoring and custom operational alerts
- HA-ready setup using HAProxy/keepalived for redundancy (requires multi-node deployment)
- Centralized searchable system logs
- Automated backups of important data (Glance images, Gnocchi metrics, MySQL databases)

### Currently _not_ included:

- User/project management: user database integration with Keystone can be accomplished in a number of ways. It is left up to the implementor of the independent testbed how to set this up. Chameleon Associate sites will be directly integrated with the existing Chameleon user management portal by Chameleon operators.
  - **Note**: in the future, CHI-in-a-Box will ship with support for account federation, allowing deployments to leverage Chameleon's user and allocation system, or integrating with other providers.
- Usage enforcement: while Chameleon comes with usage reporting, the enforcement of usage based on allocations is something that is provided only at best-effort by CHI-in-a-Box. There is no permanent storage of allocations in CHI-in-a-Box, neither is there allocation management or the ability to renew or review allocation requests.
  - **Note**: similarly, CHI-in-a-Box has support planned for integrating against Chameleon's allocation system.

## Getting started

Please refer to the repo [Wiki](https://github.com/ChameleonCloud/ansible-playbooks/wiki) for detailed information on what CHI-in-a-Box is, how it might enable science at your institution, how it works, and how to get started.
