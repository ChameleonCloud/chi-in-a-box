# Overview

Openstack, and this chi-in-a-box, have very specific requirements of the host network configuration.
Our default config seeks to provide the following logical networks.

## Network purpose

- Public API interface: (Interface where haproxy public VIP is bound, must be reachable by all networking nodes)
- Private API interface: (Interface where haproxy private VIP is bound, must be reachable by all networking nodes)
- Neutron External Interface: Interface where public IPs are bound, provides external connectivity to instances
- Neutron physical networks: interface that neutron will map tenant vlans onto
- Storage Interface: Connectivity between controller node and external storage providers
- Tunnel Interface: Connectivity between VM compute hosts

## Default physical configuration

To use fewer physical interfaces, we default to the following logical -> physical mapping:

- Public Interface
  - Public API interface
  - Neutron External Interface
- Private Interface
  - Private API interface
  - Neutron physical networks

## Safely connecting the linux networks to neutron networks

!Important!

Because the public and private interfaces are pulling double duty, care must be taken when attaching the neutron openvswitch bridge to the linux interface. Therefore, the following method is recommended:

Assume we have two interfaces available, eth0 connected to a public network segment, and eth1 connected to the managed switch dedicated for chi-in-a-box tenant networks.

### Public Network Configuration

1. Configure a bridge, br-public, with eth0 as a member.
2. configure the system's public IP, and kolla_external_vip to use this bridge as the interface, not eth0
3. Create a veth pair, named veth-publica and veth-publicb.
  1. Add veth-publica as a member of bridge br-public.
  2. Specify veth-publicb as the external interface for neutron network "public"

### Private Network Configuration

1. Configure a bridge, br-internal, with eth1 as a member.
2. configure the system's private IP, and kolla_internal_vip to use this bridge as the interface, not eth1
3. Create a veth pair, named veth-internala and veth-internalb.
  1. Add veth-internala as a member of bridge br-internal.
  2. Specify veth-internalb as the external interface for neutron network "physnet1"