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
  * [node\_custom\_config/ (optional)](before-you-begin/the-site-configuration/node_custom_config.md)
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
* [Edge-in-a-Box](setup-guides/edge-in-a-box.md)

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

* [ARM/x86 mixed architecture](example-deployments/arm-and-x86-mixed-architecture.md)
* [Edge computing/container testbed](example-deployments/edge-computing-container-testbed.md)

## Operations

* [Hardware management](operations/hardware-management.md)
* [Certificate management](operations/certificate-management.md)
* [Chameleon tools](operations/chameleon-tools/README.md)
  * [Hammers 🔨](operations/chameleon-tools/hammers/README.md)
    * [maintenance\_reservation](operations/chameleon-tools/hammers/maintenance_reservation.md)
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
* [Alert runbooks](operations/runbooks/README.md)
  * [Cron Job No Recent Success](operations/runbooks/cronjobnorecentsuccess.md)
  * [Instance Failure](operations/runbooks/instance-failure.md)
  * [Image Cache Space](operations/runbooks/ironiclowimagecachespace.md)
  * [Ironic Node Error State](operations/runbooks/ironicnodeinerrorstate.md)
  * [Jupyter Server Launch Failure](operations/runbooks/jupyterserverlaunchfailure.md)
  * [MySQL Host Down](operations/runbooks/mysqlhostdown.md)
  * [MySQL Replication Error](operations/runbooks/mysqlreplicationerror.md)
  * [Node Exporter Down](operations/runbooks/nodeexporterdown.md)
  * [Node Network Bridge Down](operations/runbooks/nodenetworkbridgedown.md)
  * [Node Network Bridge Low Traffic](operations/runbooks/nodenetworkbridgelowtraffic.md)
  * [Nova Ironic Instance Launch Failure](operations/runbooks/novaironicinstancelaunchfailure.md)
  * [OpenStack API Down](operations/runbooks/openstackapidown.md)
  * [PeriodicTask No Recent Success](operations/runbooks/periodictasknorecentsuccess.md)
  * [Portal Down](operations/runbooks/portaldown.md)
  * [Precis Parsed Events Low](operations/runbooks/precisparsedeventslow.md)
  * [Provider Conflict](operations/runbooks/provider-conflict.md)
  * [Runbook Template](operations/runbooks/template.md)
* [User support guide](operations/user-support-guide.md)
* [Upgrading to a new Release](operations/upgrading-to-a-new-release.md)

## Development

* [Developing OpenStack Services](development/developing-openstack-services.md)
* [Dev-in-a-box](development/dev-in-a-box.md)
