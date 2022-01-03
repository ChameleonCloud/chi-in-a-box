# chi-in-a-box

![chi-in-a-box](./chi-in-a-box.png)

CHI-in-a-box is a packaging of the implementation of the core services that together constitute the [Chameleon testbed](https://www.chameleoncloud.org/) for experimental Computer Science research. These services allow Chameleon users to discover information about Chameleon resources, allocate those resources for present and future use, configure them in various ways, and monitor various types of metrics.

### Currently included with CHI-in-a-Box:

**For users**:
A full-featured cloud deployment optimized for bare metal reservations and provisioning, including the following OpenStack services by default:

- Ironic (bare metal deployment)
  - Including support for bare metal snapshots (not yet an OpenStack-provided capability)
- Blazar (advanced reservation for resources such as bare metal nodes and public IP addresses or layer-2 circuits)
- Nova (instance deployment in conjunction w/ Ironic)
  - Including custom vendordata service for automatic experiment metrics collection
- Neutron (networking)
- Glance (disk image storage)
- Gnocchi (timeseries storage for experiment metrics)
- Keystone (authentication and authorization)
- Heat (orchestration)

Chameleon additionally provides a few useful extra pieces for all users of CHI-in-a-Box associate sites:

- Integration with the [Chameleon shared Jupyter environment](https://chameleoncloud.readthedocs.io/en/latest/technical/jupyter.html), to allow orchestrating experiments via Jupyter notebooks.
- [Experiment Precis](https://chameleoncloud.readthedocs.io/en/latest/technical/ep.html) provides automatic environment capture for documentation and reproducibility.
- Login with existing host credential accounts--no need to create another account or password to access Chameleon infrastructure. Take one account and use it on any Chameleon site.


**For operators**:
A suite of additional tools to help you administer your testbed with confidence "as cheaply as possible."

- [Prometheus](https://prometheus.io/) monitoring and custom operational alerts, for insight into overall system health.
- [Centralized searchable system logs](https://docs.openstack.org/kolla-ansible/latest/reference/logging-and-monitoring/central-logging-guide.html) with Kibana visualizations, for when you need to find something specific.
- [Hammers](https://github.com/chameleoncloud/hammers): automated sanity checks and maintenance scripts, for those inevitable yet easily fixable issues.
- HA-ready setup using HAProxy/keepalived for redundancy, for when uptime is a primary concern (requires multi-node deployment).
- Automated backups of important data (Glance images, MySQL databases), for a better night's rest.
- Integrate with Chameleon's existing user and allocation management system to remove the need to operate your own user workflow, authentication, and authorization systems.

### Currently _not_ included:

- ~Integration with Chameleon federated identity~ (**added February 2021!**)
- ~Track and limit usage of resources via Chameleon's allocation management system~ (**added February 2021!**)
- Support for deploying a KVM cloud or hybrid bare metal/KVM cloud infrastructure. While this is possible (and currently powers the [Chameleon KVM cloud](https://chameleoncloud.readthedocs.io/en/latest/technical/kvm.html)), this capability is still in early testing and not yet officially supported.
- Storage cluster provisioning. It's assumed that, if you desire integration with a storage system (e.g., Ceph), it is preconfigured. Such storage systems can however be integrated with a CHI-in-a-Box site to provide persistence for disk images and experiment metrics.
- Remote block storage integration for bare metal. All bare metal nodes will utilize local storage only. See the [Hardware requirements](https://github.com/ChameleonCloud/chi-in-a-box/wiki/Hardware-requirements) page for more information on what kinds of bare metal hardware configurations are currently supported.

We hope the above list continues to shrink ;)

## Getting started

Please refer to the repo [Wiki](https://github.com/ChameleonCloud/chi-in-a-box/wiki) for detailed information on what CHI-in-a-Box is, how it might enable science at your institution, how it works, and how to get started.
