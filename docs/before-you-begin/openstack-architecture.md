# OpenStack Architecture

## Networking

![](<../.gitbook/assets/CiaB Network.drawio (1).svg>)

### Public network

The public network is used for several things. Each purpose can use a separate interface, or reuse the same one (with caveats)

#### Public IPs

You'll need a minimum of **3** public IP addresses: 1 for the public facing interface, 1 for the haproxy VIP, and one for the default neutron router.

However, each instance will need **1** for a floating IP, as will each private tenant network. 20 IPs would be a good starting place, allowing, for example, 15 instances and 2 private networks.

#### Admin SSH Interface access (optional)

{% hint style="info" %}
The same physical interface (e.g. eth0), can be used for admin SSH and the public API.
{% endhint %}

By default, assuming you haven't set up a separate way to get into your controller node, you'll ssh in over this network.

#### Public API Interface

HAProxy creates a /32 address, and binds it to an interface in the public subnet. This address is used for all the public facing API endpoints, as well as the web interface. DNS should resolve for this IP, as well as a valid SSL certificate.

{% hint style="danger" %}
You CANNOT directly use the same interface for the public API and the neutron external interface. They must either be two separate interfaces, connected to the same network, OR use a virtual interface (veth) pair to connect them internally.

Without doing this, external host networking will depend on the openvswitch container running, causing a circular dependency. Debugging this will likely lock you out of the system.
{% endhint %}

#### Neutron External Interface (Floating IPs + NAT)

Neutron is the Openstack Networking service. It provides external connectivity for instances by creating virtual routers, and managing public IPs and NAT to internal addresses. It will bind at least one public IP address as the external address for the default router, as well as all assigned floating IPs for instances.

The interface defined for this network is attached to an openvswitch bridge.

### Internal Network

The internal network is used for communication between Openstack services. With a single controller node, and no external storage or compute nodes, it's largely a loopback. However, some provisioning methods require communication between the baremetal pre-boot agent and this network.

Similar to the public network, this network requires both an interface IP, as well as a HAProxy VIP.

User instances should NOT have access to this network, this can be a security risk.

### Tenant Facing Networks

There are several "types" of network that may face user instances, depending on whether a flat or VLAN configuration is used. In the default VLAN configuration, the controller node will need a vlan trunk to have access to the following networks.

#### Ironic Provisioning / Cleaning Network

This network is used for loading an image onto a baremetal node, as well as optionally cleaning them between users. The node running the Ironic Conductor must either have an address in this network, or routing must be configured between the provisioning network and the internal network.

Provisioned user instances should not be on this network, again as its a security risk. However, this is unavoidable in the flat networking configuration.

#### Sharednet

A default shared network can be created, that all user instances are attached to. This is the simplest configuration, and is sufficient for users who only care about access to their instance. However, it does not provide isolation between user instances.

In a flat networking configuration, this is the only user-facing network, and also serves as the ironic network, with above caveats.

#### Isolated Tenant Networks

Users needing isolation can create a separate neutron network. This will provide L2 connectivity between nodes, and by default a subnet and dhcp is also provided. A router must be created manually to give external access, either via SNAT, or the use of floating IPs.

### Out of Band (IPMI) Network

The controller node (or node running ironic conductor service), must have L3 access to the out of band controller for all baremetal nodes. This can be routed access from one of the other interfaces, or a dedicated connection.

## Hosts

### Deploy Host (Optional)

This is the host where the ansible deployment scripts are generated and run from, as well as storing the site configuration files. It's recommended to have this be a separate machine or VM, to make it easier to re-deploy the ansible managed hosts.

### Controller Nodes

In a monolithic installation, the _control node_ runs all of the OpenStack and Chameleon services. If needed, services can be distributed across multiple controller nodes for high availability or scaling purposes.

For Details and Requirements, see the link below.

{% content-ref url="hardware-requirements/controller-nodes.md" %}
[controller-nodes.md](hardware-requirements/controller-nodes.md)
{% endcontent-ref %}

### Compute Nodes

Compute nodes run virtualized guest instances. These are not a part of our default configuration, but configurations with KVM and Container compute nodes are in beta.

{% content-ref url="hardware-requirements/compute-nodes.md" %}
[compute-nodes.md](hardware-requirements/compute-nodes.md)
{% endcontent-ref %}

### **Baremetal Nodes**

A Baremetal node is externally managed by Openstack Ironic, and the entire machine is provided as an instance to a user.

{% content-ref url="hardware-requirements/compute-nodes.md" %}
[compute-nodes.md](hardware-requirements/compute-nodes.md)
{% endcontent-ref %}
