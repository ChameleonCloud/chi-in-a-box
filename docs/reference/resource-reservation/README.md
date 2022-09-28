# Resource Reservation

## Overview



### Requirements

[You must have installed the chameleon fork of python-blazarclient.](https://chameleoncloud.readthedocs.io/en/latest/technical/cli.html#openstack-client-installation)

```
pip install \
git+https://github.com/chameleoncloud/python-blazarclient@chameleoncloud/xena
```

## Adding Resources

### Hosts

You shouldn't need to do this manually, as Doni will manage this for you.

If you need to, the command is

```shell-session
openstack reservation host create
```

### Devices

```
openstack reservation device create
```

### Networks

#### Create a Reservable Network

This creates an entry in Blazar, allowing a user to reserve a vlan on a physical network. When their lease starts, a neutron network will be created using that vlan and physnet.

Make sure that the segment ID + physnets you add here are **outside** the range of ad-hoc vlans defined for neutron (in your `defaults.yml` file). Otherwise, Blazar's reservable vlans and neutron's ad-hoc ones may conflict.\


Usage:

<pre data-overflow="wrap"><code>openstack reservation network create \
  --network-type &#x3C;NETWORK_TYPE> \
<strong>  --physical-network &#x3C;PHYSICAL_NETWORK> \
</strong><strong>  --segment &#x3C;SEGMENT_ID> \
</strong><strong>  --extra &#x3C;key>=&#x3C;value>
</strong>
options:
  --network-type NETWORK_TYPE
                        Type of physical mechanism associated with the network segment. For example: flat, geneve, gre, local, vlan, vxlan.
  --physical-network PHYSICAL_NETWORK
                        Name of the physical network in which the network segment is available, required for VLAN networks
  --segment SEGMENT_ID
                        VLAN ID for VLAN networks or Tunnel ID for GENEVE/GRE/VXLAN networks
  --extra &#x3C;key>=&#x3C;value>
                        Extra capabilities key/value pairs to add for the network</code></pre>

Example:

```shell-session
openstack reservation network create \
  --network-type vlan \
  --physical-network physnet1 \
  --segment 2000 \
  --extra mykey=myvalue
```

#### Add or update capability to a Reservable Network

```shell-session
openstack reservation network set --extra key=value NETWORK_ID
```

Example, change the physical network:

```
openstack reservation network set --extra physical_network=physnet1
```

#### Convention for Stitch-able Networks

To indicate that a network can be connected to other sites at L2, we use the key `stitch_provider`

For example, if you have plumbed VLANs from your dataplane switch to a FABRIC facility port, indicate these with:

```
openstack reservation network set --extra stitch_provider=fabric
```

### Floating IPs

Create a new reservable floating IP

```
openstack reservation floatingip create <NETWORK_ID> <FLOATING_IP_ADDRESS>
```
