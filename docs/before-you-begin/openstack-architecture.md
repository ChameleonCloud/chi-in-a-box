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

This network is used for loading an image onto a baremetal node, as well as optionally cleaning them between users. The node running the Ironic Conductor must either have an address in this network, or routing must be configured between the provisioning network and the internal network.

TODO: Diagram for ironic-provisioning -> mgmt traffic

Provisioned user instances should **not** be on this network, as its a security risk. However, this is unavoidable if baremetal nodes are used without a network supporting VLANs.

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

<figure><img src="../.gitbook/assets/Neutron Networking-Putting it all together.drawio.svg" alt=""><figcaption></figcaption></figure>

Putting it all together, you can see there are plenty of moving parts. For this diagram, we assume that the following networks are present as VLANs on the cluster's **dataplane switch**:

* Public API Network (Green)
* Internal API network (Red)
* Public Tenant network (Green), and reusing the same network as the public API
* Internal Tenant Networks (Blue)
* Ironic-Provisioning Network (A special case of the internal tenant networks)

If desired, the Public API and Tenant networks could be carried on a different switch entirely from the rest, and the Public Tenant Network could also be configured to use a separate public subnet and vlan.

A separate, **1G management switch** carries the following networks, either as vlans, or a single flat network if desired.

* Controler Node access to Baremetal Node IPMI
* Controller Node access to Dataplane Switch's SSH management interface
* Local administrative SSH access, if desired



