# Ironic Multi-Tenant Networking

### Overview

This is our default deployment method. To enable multi-tenant networking with Ironic, baremetal nodes must be connected to a vlan-capable switch, and those vlans managed by neutron.

### Baremetal Node Requirements

* Ensure that reservable nodes have an IPMI-capable out of band (OOB) baseboard management controller (BMC). E.g. Dell iDRAC
* Ensure that the private interface has connectivity to the BMC network interface of each node.
* Ensure that credentials and access are configured to allow IPMI management of the BMC settings.

### Controller Node Requirements

* Ensure that the private interface has connectivity to the out of band interface of any managed switches
* Ensure that SSH access is configured to administrate any managed switches
* Ensure that credentials and settings allow for the ssh user to manage switch vlans.
* Ensure that switches have been configured with a range of "Trunked VLANs" for usage by neutron.

### Configuration

#### networking-generic-switch

Here's an example for site-config/defaults.yml.

`device_type` refers to a neutron/networking-generic-switch "driver". [The full list can be found here](https://github.com/ChameleonCloud/networking-generic-switch/blob/98ddec1f11eab5197f1443207b13a16f364e5f10/setup.cfg#L31-L48).

Commonly used ones on chameleon include `netmiko_dell_os10` and `netmiko_dell_force10`

Refer to the `name` of each switch when configuring baremetal nodes.

```
# Physical Switch config for Neutron-ML2:
# Uncomment with info for neutron managed switch
switch_configs:
  - name: leafswitch1
    device_type: netmiko_dell_force10
    address: 10.0.0.10
    auth:
      username: chameleon
      password: "{{ dell_switch_password }}"
    snmp:
      community_string: "{{ dell_switch_community_string }}"
    ngs_config:
      persist_changes: False
      fast_cli: True
```

#### Baremetal node configuration

Each network interface on a node must have metadata about which switch and switchport it's connected to. A sample interface json looks like the following:

```json
"interfaces": [
    {
        "mac_address": "B8:CE:F6:32:C8:EE",
        "name": "<human_readable_name",
        "switch_id": "<switch_mgmt_iface_mac_addr>",
        "switch_info": "<name_of_switch>",
        "switch_port_id": "<switch_port_name>"
    },
    {
        "mac_address": "B8:CE:F6:32:C8:EF",
        "name": "NIC.Integrated.1-2-1:Mellanox ConnectX-5 EN 25GbE Dual-port SFP28 Adapter",
        "switch_id": "c0:3e:ba:df:3c:00",
        "switch_info": "chameleon-p3-tor2",
        "switch_port_id": "1/1/19:2"
    }
],

```

