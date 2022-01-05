# Table of contents

* [What is CHI-in-a-Box?](README.md)

## Setup Guides

* [Production Baremetal](setup-guides/production-baremetal/README.md)
  * [Host Networking Configuration](setup-guides/production-baremetal/hostnetworking.md)
  * [Baremetal QuickStart](setup-guides/production-baremetal/quickstart.md)

## Fundamentals

* [Hardware Requirements](fundamentals/definitions/README.md)
  * [Control Nodes](fundamentals/definitions/hardware-requirements.md)
  * [Deploy Host (Optional)](fundamentals/definitions/deploy-host-optional.md)
  * [Compute Nodes (beta)](fundamentals/definitions/compute-nodes-beta.md)
  * [Baremetal Nodes](fundamentals/definitions/baremetal-nodes.md)
  * [Dataplane Switches](fundamentals/definitions/dataplane-switches.md)
* [Security considerations](fundamentals/security-considerations.md)

## Reference

* [cc-ansible CLI](reference/command-line-interface.md)
* [The site configuration](reference/the-site-configuration/README.md)
  * [inventory](reference/the-site-configuration/inventory.md)
  * [defaults.yml](reference/the-site-configuration/defaults.yml.md)
  * [passwords.yml](reference/the-site-configuration/passwords.yml.md)
  * [node\_custom\_config](reference/the-site-configuration/node\_custom\_config.md)
  * [post-deploy.yml](reference/the-site-configuration/post-deploy.yml.md)
* [Features](reference/features/README.md)
  * [Chameleon Identity Federation](reference/features/chameleon-identity-federation.md)
  * [Baremetal Provisioning](reference/features/baremetal-provisioning.md)
  * [Multi-Tenant Networking](reference/features/multi-tenant-networking.md)
  * [Resource Reservation](reference/features/resource-reservation.md)
  * [SNMP Metrics](reference/features/snmp-metrics.md)
  * [IPMI Metrics](reference/features/ipmi-metrics.md)
* [Kolla-Ansible Docs](https://docs.openstack.org/kolla-ansible/train/)
* [Ansible Docs](https://docs.ansible.com/ansible/2.8/index.html)

## Example Deployments

* [ARM/x86 mixed architecture](ARM-and-x86-mixed-architecture.md)
* [Edge computing/container testbed](Edge-computing-container-testbed.md)

## Operations

* [Hardware management](Hardware-management.md)
* [Certificate management](Certificate-management.md)
* [Hammers 🔨](Hammers.md)
* [Runbooks](runbooks/README.md)
  * [Cron Job No Recent Success](runbooks/CronJobNoRecentSuccess.md)
  * [Instance Failure](runbooks/instance-failure.md)
  * [Image Cache Space](runbooks/IronicLowImageCacheSpace.md)
  * [Ironic Node Error State](runbooks/IronicNodeInErrorState.md)
  * [Jupyter Server Launch Failure](runbooks/JupyterServerLaunchFailure.md)
  * [MySQL Host Down](runbooks/MySQLHostDown.md)
  * [MySQL Replication Error](runbooks/MySQLReplicationError.md)
  * [Node Exporter Down](runbooks/NodeExporterDown.md)
  * [Node Network Bridge Down](runbooks/NodeNetworkBridgeDown.md)
  * [Node Network Bridge Low Traffic](runbooks/NodeNetworkBridgeLowTraffic.md)
  * [Nova Ironic Instance Launch Failure](runbooks/NovaIronicInstanceLaunchFailure.md)
  * [OpenStack API Down](runbooks/OpenStackAPIDown.md)
  * [PeriodicTask No Recent Success](runbooks/PeriodicTaskNoRecentSuccess.md)
  * [Portal Down](runbooks/PortalDown.md)
  * [Precis Parsed Events Low](runbooks/PrecisParsedEventsLow.md)
  * [Provider Conflict](runbooks/provider-conflict.md)
  * [Runbook Template](runbooks/Template.md)
* [Troubleshooting](operations/troubleshooting/README.md)
  * [Known issues](operations/troubleshooting/known-issues.md)
  * [Instance networking diagnostics](operations/troubleshooting/instance-networking-diagnostics.md)
  * [Security incident triage](operations/troubleshooting/security-incident-triage.md)

## Development

* [Developing Openstack Services](Developing-Openstack-Services.md)
* [Dev-in-a-box](development/dev-in-a-box.md)
