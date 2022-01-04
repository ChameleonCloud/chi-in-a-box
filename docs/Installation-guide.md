# Installing CHI-in-a-Box

## Definitions

- Deploy Host (Optional): This is the host where the ansible deployment scripts are generated and run from, as well as storing the site configuration files. It's recommended to have this be a separate machine or VM, to make it easier to re-deploy the ansible managed hosts.
- Controller Node: In a monolithic installation, the _controller node_ runs all of the openstack and chameleon services. If needed, services can be distributed across multiple controller nodes for high availability or scaling purposes.
- Compute Node: A compute node runs Openstack Nova, and runs virtualized instances, managed by a controller node.
- Baremetal Node: A baremetal node is externally managed by Openstack Ironic, and the entire machine is provided as an instance to a user.
- Managed Switch: Network switch under the control of Openstack services to provide multi-tenant networking.

## Installation Assumptions

This will be an all-in-one installation. All services and endpoints will reside on one node, called the _controller node_. This node will not be reservable by users. The controller node should be configured to meet the following criteria:

### Operating System

Provision the _controller node(s)_ with a fresh install of CentOS 8, Ubuntu 18.04 (Bionic), or 20.04 (Focal).
This install is currently tested on CentOS 8 only. Some additional packages are required for each node:

- Python 3. *Note*: please try to install using the most "normal" method for your OS. Ansible has some assumptions about where it can find the Python executable during initial bootstrapping of a controller node.

### Networks, Interfaces, and Subnets

- Management (Optional): This interface allows SSH access to manage the _controller node_
  - If using a separate _deploy host_, configuration will take place over this interface.
- Private: This network handles traffic towards the _compute_ and _baremetal_ nodes.
  - The following services use this interface: RabbitMQ, MariaDB, OpenStack internals, Neutron, IPMI
  - 10G or faster is recommended
  - Assign a private IP to this interface.
  - Ensure that at least 2 free IPv4 addresses are available in the same subnet as this assigned private IP.
- Public:
  - This interface provides access to the public openstack APIs, as well as routing traffic between private networks and the internet.
  - The following services use this interface: OpenStack APIs via HTTPS proxy, Horizon, Neutron external bridge
  - 10G or faster is recommended
  - Choose an address and subnet that allows for communication with your upstream gateway.
  - The hostname of the _controller node_ should resolve to this address.
  - Ensure that at least 2 free IPv4 addresses are available in the same subnet as this assigned Public IP. In production, many more are desired.

### Certificates

Ensure that a certificate is available for the hostname on the public interface. This can be obtained via LetsEncrypt or other public CAs, or you can use a self-signed cert. Make sure you have the full chain available.

### Additional Requirements for Multi-Tenant Networking

- Ensure that the private interface has connectivity to the out of band interface of any managed switches
- Ensure that SSH access is configured to administrate any managed switches
- Ensure that credentials and settings allow for the ssh user to manage switch vlans.
- Ensure that switches have been configured with a range of "Trunked VLANs" for usage by neutron.

### Additional Requirements for Bare-Metal Provisioning

- Ensure that reservable nodes have an IPMI-capable out of band (OOB) baseboard management controller (BMC). E.g. Dell iDRAC
- Ensure that the private interface has connectivity to the BMC network interface of each node.
- Ensure that credentials and access are configured to allow IPMI management of the BMC settings.

## Next Steps

Refer to the [Quick Start Guide](./QuickStart) to see these considerations in use.
