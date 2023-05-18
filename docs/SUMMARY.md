# Table of contents

* [What is CHI-in-a-Box?](README.md)

## Before You Begin

* [Assumed Knowledge](before-you-begin/upstream-docs.md)
* [Hosts and Services](before-you-begin/hosts-and-services.md)
* [Network Overview](before-you-begin/openstack-architecture.md)
* [CC-Ansible](before-you-begin/command-line-interface.md)
* [The site configuration](before-you-begin/the-site-configuration/README.md)
  * [inventory](before-you-begin/the-site-configuration/inventory.md)
  * [defaults.yml](before-you-begin/the-site-configuration/defaults.yml.md)
  * [passwords.yml](before-you-begin/the-site-configuration/passwords.yml.md)
  * [certificates/](before-you-begin/the-site-configuration/certificates.md)
  * [node\_custom\_config/ (optional)](before-you-begin/the-site-configuration/node\_custom\_config.md)
  * [post-deploy.yml (optional)](before-you-begin/the-site-configuration/post-deploy.yml.md)
* [How Deployment Works](before-you-begin/how-deployment-works.md)
* [Security considerations](before-you-begin/security-considerations.md)

## Setup Guides

* [Evaluation Site](setup-guides/evaluation-site/README.md)
  * [Bring up the Control Plane](setup-guides/evaluation-site/bring-up-the-control-plane.md)
* [Production Baremetal](setup-guides/production-baremetal/README.md)
  * [Baremetal QuickStart](setup-guides/production-baremetal/quickstart.md)
  * [Host Networking Configuration](setup-guides/production-baremetal/hostnetworking.md)
* [Troubleshooting](setup-guides/troubleshooting/README.md)
  * [Networking](setup-guides/troubleshooting/networking.md)
* [Verification Checklist](setup-guides/verification-checklist.md)
* [Dev-in-a-Box](setup-guides/dev-in-a-box.md)

## Reference

* [Chameleon Identity Federation](reference/chameleon-identity-federation.md)
* [Ironic Flat Networking](reference/ironic-flat-networking.md)
* [Ironic Multi-Tenant Networking](reference/multi-tenant-networking.md)
* [Glance Image Storage](reference/glance-image-storage.md)
* [Resource Reservation](reference/resource-reservation/README.md)
  * [Default Resource Properties](reference/resource-reservation/default-resource-properties.md)
* [Monitoring](reference/monitoring/README.md)
  * [IPMI Metrics](reference/monitoring/ipmi-metrics.md)
  * [SNMP Metrics](reference/monitoring/snmp-metrics.md)

## Example Deployments

* [ARM/x86 mixed architecture](ARM-and-x86-mixed-architecture.md)
* [Edge computing/container testbed](Edge-computing-container-testbed.md)

## Operations

* [Hardware management](Hardware-management.md)
* [Certificate management](Certificate-management.md)
* [Chameleon tools](operations/chameleon-tools/README.md)
  * [Hammers 🔨](operations/chameleon-tools/hammers/README.md)
    * [maintenance\_reservation](operations/chameleon-tools/hammers/maintenance\_reservation.md)
  * [Disk image subscription](operations/chameleon-tools/image-tools.md)
  * [Usage reporting](operations/chameleon-tools/usage-reporting.md)
* [Troubleshooting](operations/troubleshooting/README.md)
  * [Known issues](operations/troubleshooting/known-issues/README.md)
    * [Neutron (networking)](operations/troubleshooting/known-issues/neutron-networking.md)
    * [Nova (KVM)](operations/troubleshooting/known-issues/nova-kvm.md)
    * [Ironic (bare metal)](operations/troubleshooting/known-issues/ironic-bare-metal.md)
  * [Instance networking diagnostics](operations/troubleshooting/instance-networking-diagnostics.md)
  * [Security incident triage](operations/troubleshooting/security-incident-triage.md)
  * [Troublesome Hardware](operations/troubleshooting/troublesome-hardware.md)
* [Alert runbooks](runbooks/README.md)
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
* [User support guide](operations/user-support-guide.md)
* [Upgrading to a new Release](operations/upgrading-to-a-new-release.md)

## Development

* [Developing OpenStack Services](Developing-Openstack-Services.md)
* [Dev-in-a-box](development/dev-in-a-box.md)
