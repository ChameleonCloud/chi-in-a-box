---
description: Where all the moving parts are
---

# Network Overview

This page describes the overall architecture for our "standard" deployment of OpenStack, and where applicable, calls out that a concept is a subset of the required Background Reading.

## OpenStack API Networking

There are two API networks to consider.&#x20;

First is the **internal api network**, used for internal communication between OpenStack services and Databases. We refer to this interface as the `api_interface` in configuration, as each OpenStack service binds to the system configured IP address on this interface. Exposing this either to users, or externally can be a security risk, so we require a dedicated network and subnet.&#x20;

The second is the **public api** network, which is how users and user instances communicate with the OpenStack services. We refer to this interface as the `kolla_external_vip_interface` in configuration.

Each of the above networks require an interface, subnet, and IP address configured on the controller node. HAProxy will then bind an **additional** IP address to each of the interfaces, and forward traffic as needed to the backend OpenStack services.

<figure><img src="../.gitbook/assets/Neutron Networking-API Networks.drawio (1).svg" alt=""><figcaption><p>Diagram of Public and Management API connectivity</p></figcaption></figure>

## OpenStack Neutron Networking

Independent from the API networking, OpenStack Neutron manages networking for tenants, connecting Baremetal Nodes to each other, as well as providing internet access via NAT, and Floating IPs.

<figure><img src="../.gitbook/assets/Neutron Networking-Neutron Networks.drawio (1).svg" alt=""><figcaption></figcaption></figure>

Here, `Tenant Public Network` refers to a network where tenants can request Floating IPs, and that their instances can use to reach the internet. So long as IP addresses do not overlap, this can be the same network as the Public API network above, but does not need to be.

{% hint style="danger" %}
You CANNOT directly use the **same interface** for the public API and the neutron external interface. They must either be two separate interfaces, connected to the same network, OR use a virtual interface (veth) pair to connect them internally.

Without doing this, external host networking will depend on the openvswitch container running, causing a circular dependency. Debugging this will likely lock you out of the system, and cause an outage.
{% endhint %}

The `Tenant Internal Network(s)` refers to the range of networks that tenants may allocate, local to the cluster.

As tenants can create an arbitrary amount of traffic, it is recommended that these interface(s) are kept independent from those used for API or administrative traffic.

### Physical Networks

Neutron creates and manages networks with namespaced sets of IPTables rules for routing, NAT, firewalling, etc, and connects these namespaces with OpenVSwitch bridges, either internally, or to external interfaces. Each interface + OVS Bridge can carry a set of networks corresponding to a range of Vlans + a single untagged vlan. Each of these sets of networks is referred to as a `Physical Network` in Neutron.

As shown in the above diagram, Neutron will create and manage Public, Floating IP addresses in such a router namespace, and NAT private IPs from tenant networks to this public network. User instances can reach the internet through this NAT, and can optionally bind a floating IP address to their private IP for 1-1 NAT.

Although the diagram shows two physical networks, the same could be accomplished with two Vlan IDs on one physical network, or a vlan ID + untagged network.

### Tenant Internal Networks

In addition to the tenant created and managed networks, two "special" networks are created by the administrative project in the same Physical Network.&#x20;

#### Ironic Provisioning / Cleaning Network

This network is used for loading an image onto a baremetal node, as well as optionally cleaning them between users. When an instance is launched, the baremetal node will be attached to this network, netboot an agent, download a new disk image, and finally be attached to a target tenant network.

{% hint style="info" %}
Provisioned user instances should **not** be on this network, as its a security risk. However, this is unavoidable if baremetal nodes are used without a network supporting VLANs.
{% endhint %}

Since the agent must communicate with the internal api interface on the controller node, the ironic provisioning network must be able to route to the internal api network. The simplest way to accomplish this is to route via an additional vlan interface on the controller node.

<figure><img src="../.gitbook/assets/Neutron Networking-Ironic Provisioning.drawio.svg" alt=""><figcaption></figcaption></figure>

#### Sharednet

A default "shared" network can be created, usable as an internal network by any tenant. This is the simplest configuration, and is sufficient for users who only care about access to their instance. However, it does not provide isolation between user instances.

In a flat networking configuration, this is the only user-facing network, and also serves as the ironic network, with above caveats.

## Additional System-level Networks

The following networks are optional, and may be combined depending on your local site's networking environment. They are outside the scope of CHI-in-a-box / Kolla-Ansible / OpenStack's configuration, and must be configured at the system level.

### Out of Band (IPMI) Network

The controller node (or node running ironic conductor service), must have L3 access to the out of band controller for all baremetal nodes. This can be routed access from one of the other interfaces, or a dedicated connection.

### Out of Band (Network Device) Network

If using vlans with baremetal nodes, Neutron must connect to the dataplane switches to customize the access Vlan on each instance launch. Neutron-server must have L3 access to the management IP for each switch. We highly recommend to use the dedicated management interface on each switch, rather than in-band connectivity.

### Administrative Access (SSH) Network

You will likely want to ssh into your controller nodes for administrative purposes. The internal api interface is commonly used for this purpose.

## Putting it all together

<figure><img src="../.gitbook/assets/Neutron Networking-Putting it all together.drawio (2).svg" alt=""><figcaption></figcaption></figure>

{% hint style="info" %}
Interface Names and Vlan IDs here are only examples, customize as needed
{% endhint %}

Putting it all together, you can see there are plenty of moving parts. We'll define the following network name -> vlan mapping:

* Public API Network (Green: **Vlan 1000**)
* Internal API network (Red: **Vlan 1001**)
* Public Tenant network (Green: **Vlan 1000**), and reusing the same network as the public API
* Internal Tenant Network Range (Blue: **Vlans 1002-1200**)
* Ironic-Provisioning Network (Orange: **Vlan 1002**, A special case of the internal tenant networks)

### Controller Node Interfaces

Here we show an example with three physical interfaces. On the host OS, the following configuration is needed:

* 3 vlan interfaces are attached to Eth0
  * Eth0.1000 used for the Public API interface, with an IP address assigned
  * Eth0.1001 used for the Internal API interface, with an IP address assigned
  * Eth0.1002 used for the Ironic Provisioning interface, with an IP address assigned
* Eth1 left unconfigured, it will be managed by Neutron as the external interface for the Physical Network Physnet1
* Eth2 is used to access the dataplane switch mgmt interface, as well as IPMI on the compute nodes. An IP address in should be assigned in the same subnet as those devices.

### Dataplane Switch Configuration

For this diagram, we assume that the above networks are all present on the cluster's **dataplane switch,** and the following ports configured:

* Uplink, access port with Vlan 1000
* Trunk for Controller API Interfaces, carrying vlans 1000,1001,1002
* Trunk for Neutron external interface, carrying vlans 1000,1002-1200
* Switchport connected to eth0 on each Baremetal Node, configured as an untagged, access port. The Neutron service will dynamically configure the access vlan on these ports, from the range 1002-1200.

{% hint style="info" %}
If needed, the Public API and Public Tenant networks can be provided via a separate switch and physical interface on the controller node.
{% endhint %}

The switch must be configured to allow SSH login via the separate, out-of-band management interface, and that interface and IP address reachable by the controller node.

### Out of Band Connections

A separate, **1G management switch** carries the following networks, either as vlans, or a single flat network.

* Controller Node access to Baremetal Node IPMI
* Controller Node access to Dataplane Switch's SSH management interface
* Local administrative SSH access, if desired

{% hint style="warning" %}
IP addresses and DHCP for IPMI, Switch Management, and administrative access are **NOT** managed by CHI-in-a-box. You'll need to configure static IPs, run your own DHCP server, or rely on an external service.
{% endhint %}



