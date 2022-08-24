# Ironic Multi-Tenant Networking

## Overview

This is our default deployment method. To enable multi-tenant networking with Ironic, baremetal nodes must be connected to a vlan-capable switch, and those vlans managed by neutron.

## Prerequisites

### Baremetal node:

Ensure that reservable nodes have an IPMI-capable out of band (OOB) baseboard management controller (BMC). E.g. Dell iDRAC

* Ensure that the private interface has connectivity to the BMC network interface of each node.
* Ensure that credentials and access are configured to allow IPMI management of the BMC settings.

### Controller Node:

* Ensure that the private interface has connectivity to the out of band interface of any managed switches
* Ensure that SSH access is configured to administrate any managed switches
* Ensure that credentials and settings allow for the ssh user to manage switch vlans.
* Ensure that switches have been configured with a range of "Trunked VLANs" for usage by neutron.

## Configuration

To enable this feature, both the network service, and each baremetal node need some extra configuration.

### Neutron / Networking-Generic-Switch

Add an entry to the `switch_configs` array in `site-config/defaults.yml` for each dataplane switch that Neutron will manage. This is not needed for out-of-band switches.

#### Example:

```yaml
# Physical Switch config for Neutron-ML2:
# Uncomment with info for neutron managed switch
switch_configs:
  - name: leafswitch1
    device_type: <ngs_driver>
    address: <switch_mgmt_ip>
    auth:
      username: <switch_ssh_user>
      password: "{{ <name_of_entry_in_passwords_file> }}"
    snmp:
      community_string: "{{ snmp_community_string }}"
    ngs_config:
      fast_cli: True
```

#### Explanation of fields:

* `name`: Label for the switch, will be used in baremetal node configuration.
* `device_type`: Which "driver" to use to communicate with the switch. This will depend on the switch's vendor and operating system. [The list of supported values can be found here.](https://github.com/ChameleonCloud/networking-generic-switch/blob/8f9f9edb9a2974b4084297643f1fe07213ecebf6/setup.cfg#L33-L51) If you're not sure, `netmiko_cisco_ios` can be tried as a default.
* `address`: IP address of the switch's management interface.
* auth: How to authenticate to the switch. A dict of two fields. These credentials must be manually set up on the switch before neutron can connect.
  * `username`: SSH username.
  * `password`: SSH password. We recommend using `cc-ansible edit_passwords` to add this password to the encrypted `passwords.yml` file. It can be accessed in your config file as `"{{ <name_of_entry_in_passwords_file> }}"`. This avoids having the password stored in cleartext in your site-config.
* `snmp`: (optional) Used to get performance data from the switch via SNMP
  * `snmp_community_string:` (optional) snmp read-only community string
* `ngs_config`: (optional) A dictionary of custom settings to pass to the switch.&#x20;
  * `fast_cli`: Speeds up config changes. Set to true if you switch seems compatible.
  * `persist_changes`: Save running config to startup after each change. Recommended to leave enabled, but can be disabled for a speedup.
  * `ngs_manage_vlans`: Whether to have neutron create/delete vlans, if your `device_type` supports it. Recommended to disable, and configure static vlan trunks.

### Baremetal node configuration

To dynamically configure vlans for a node, Neutron needs to know what switch and switchport is connected to each interface on that node.

This is expressed with the following parameters:

* `mac_address`: Required, used to configure DHCP
* `name`: (optional), human readable label for the network interface.
* `switch_id`: unique identifier for the switch, in mac-address format. Recommend setting it to the mac-address of the switch's management interface.
* `switch_info`: human readable label for the switch. Recommend setting it to the hostname of the switch's management interface.
* `switch_port_id`: Name of the switch port connected to the node. The syntax will depend on the switch vendor and operating system.\
  If you were to configure an interface using the CLI on the switch, e.g. `interface ethernet 1/1/2`, this `switch_port_id` would be `1/1/2`

When importing a node using `Doni`, your json file would have the following values under `properties`

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

## Troubleshooting and Performance Issues

### Networking Generic Switch

### Ironic

When you have many nodes connected to a single switch, you may observe operations timing out.

For each switch, port operations are queued, and this delay can become excessive.

As a workaround, we provide "knobs" for two parameters in Ironic.

`ironic_neutron_status_code_retries`: Defaults to 10, Ironic will retry failed requests to neutron up to 10 times, with exponential backoff between each request. This serves to apply backpressure and keep ironic from overloading the slow switch configuration process.

If the exponential backoff is not sufficient, a fixed  `status_code_retry_delay` can be set.

