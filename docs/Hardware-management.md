# Hardware management

Chameleon sites can support a wide variety of hardware. Here's how to manage each type for a given site.

## Baremetal

Bare metal nodes can be registered via Doni, the registration and inventory service. Doni is enabled by default for all CHI-in-a-Box sites since 2021/04; if you have an older deployment, you can deploy Doni by checking out the latest version of CHI-in-a-Box and deploying it manually:

```shell
./cc-ansible pull --tags doni && ./cc-ansible deploy --tags doni
```

The client, `python-doniclient`, integrates with the openstack commandline interface. Some commands must be run as an admin user, due to the possibility of exposing sensitive information.

### Viewing Hardware

#### List Hardware

```shell-session
openstack hardware list --max-width=100
+------+------------------------+---------------+------------------------+-------------------------+
| name | project_id             | hardware_type | properties             | uuid                    |
+------+------------------------+---------------+------------------------+-------------------------+
| c14  | b735ed5531514429af940a | baremetal     | {}                     | d168805d-5aff-4ac6-a881 |
|      | b12cb1c51b             |               |                        | -31fac6be1912           |
| nc62 | b735ed5531514429af940a | baremetal     | {}                     | 8f03e084-a3c5-48a1-8719 |
|      | b12cb1c51b             |               |                        | -fc6ed050778d           |
| c01  | b735ed5531514429af940a | baremetal     | {}                     | 1aaeeb0d-3c49-4921-9c24 |
|      | b12cb1c51b             |               |                        | -d7b9f5bc2022           |
| c29  | e8ae724d28374d0fa15a0e | baremetal     | {'interfaces':         | 1537122b-d019-4075-9b07 |
|      | 16674b5c47             |               | [{'mac_address':       | -4e2b39e555a3           |
|      |                        |               | '44:a8:42:16:f9:ea',   |                         |
|      |                        |               | 'name': '5979c547-810d |                         |
|      |                        |               | -4876-b08d-81b48c33c71 |                         |
|      |                        |               | 5'}]}                  |                         |
| c39  | e8ae724d28374d0fa15a0e | baremetal     | {'interfaces':         | 5d6ff05d-b959-40a5-8869 |
|      | 16674b5c47             |               | [{'mac_address':       | -1994d37b5cb9           |
|      |                        |               | '44:a8:42:15:ca:44',   |                         |
|      |                        |               | 'name': '8270f468-aa2e |                         |
|      |                        |               | -4687-bf33-97a9412be4b |                         |
|      |                        |               | a'}, {'mac_address':   |                         |
|      |                        |               | '44:a8:42:15:ca:46',   |                         |
|      |                        |               | 'name': 'e023c3e4-b3bc |                         |
|      |                        |               | -48a1-aa21-a5761ff5abc |                         |
|      |                        |               | 7'}]}                  |                         |
+------+------------------------+---------------+------------------------+-------------------------+
```

Using the --all flag will print additional information.

```
+------+------------------------+---------------+------------------------+-------------------------+
| name | project_id             | hardware_type | properties             | uuid                    |
+------+------------------------+---------------+------------------------+-------------------------+
| c39  | e8ae724d28374d0fa15a0e | baremetal     | {'baremetal_driver':   | 5d6ff05d-b959-40a5-8869 |
|      | 16674b5c47             |               | 'ipmi', 'baremetal_res | -1994d37b5cb9           |
|      |                        |               | ource_class':          |                         |
|      |                        |               | 'baremetal',           |                         |
|      |                        |               | 'interfaces':          |                         |
|      |                        |               | [{'mac_address':       |                         |
|      |                        |               | '44:a8:42:15:ca:44',   |                         |
|      |                        |               | 'name': '8270f468-aa2e |                         |
|      |                        |               | -4687-bf33-97a9412be4b |                         |
|      |                        |               | a'}, {'mac_address':   |                         |
|      |                        |               | '44:a8:42:15:ca:46',   |                         |
|      |                        |               | 'name': 'e023c3e4-b3bc |                         |
|      |                        |               | -48a1-aa21-a5761ff5abc |                         |
|      |                        |               | 7'}], 'ipmi_password': |                         |
|      |                        |               | '************',        |                         |
|      |                        |               | 'ipmi_terminal_port':  |                         |
|      |                        |               | 30139,                 |                         |
|      |                        |               | 'ipmi_username':       |                         |
|      |                        |               | 'root',                |                         |
|      |                        |               | 'management_address':  |                         |
|      |                        |               | '172.29.0.139'}        |                         |
```

#### Show Hardware

View a single node by UUID

```
openstack hardware show --max-width=100 5d6ff05d-b959-40a5-8869-1994d37b5cb9
+---------------+----------------------------------------------------------------------------------+
| Field         | Value                                                                            |
+---------------+----------------------------------------------------------------------------------+
| name          | c39                                                                              |
| project_id    | e8ae724d28374d0fa15a0e16674b5c47                                                 |
| hardware_type | baremetal                                                                        |
| properties    | {'baremetal_driver': 'ipmi', 'baremetal_resource_class': 'baremetal',            |
|               | 'interfaces': [{'mac_address': '44:a8:42:15:ca:44', 'name':                      |
|               | '8270f468-aa2e-4687-bf33-97a9412be4ba'}, {'mac_address': '44:a8:42:15:ca:46',    |
|               | 'name': 'e023c3e4-b3bc-48a1-aa21-a5761ff5abc7'}], 'ipmi_password':               |
|               | '************', 'ipmi_terminal_port': 30139, 'ipmi_username': 'root',            |
|               | 'management_address': '172.29.0.139'}                                            |
| uuid          | 5d6ff05d-b959-40a5-8869-1994d37b5cb9                                             |
+---------------+----------------------------------------------------------------------------------+
```

### Enrolling a bare metal node

Enrolling a bare-metal node will:

1. Create an entry in Ironic for bare-metal provisioning
2. Create an entry in Blazar, so the node is reservable by users

```shell
openstack hardware create [--dry_run] \
--name=test_3 --hardware_type baremetal \
--mgmt_addr=$IPMI_ADDRESS \
--ipmi_username $IPMI_USERNAME --ipmi_password $IPMI_PASSWORD \
--interface "name=foo,mac_address=ff:ff:ff:ff:ff:ff" \
--interface "name=bar,mac_address=gg:gg:gg:gg:gg:gg"
```

#### Bulk imports

It's often more convenient to describe hardware to import as structured data, rather than shell wrangling. python-doniclient supports using `json` as input for creating one or more nodes.

To do so, use the `hardware import` command, and specify a json, structured as an array of objects.&#x20;

{% hint style="info" %}
In the example below, items enclosed in `<..>` should be replaced by your actual value.
{% endhint %}

```json
[
  {
    "name": "<node_name_1>",
    "hardware_type": "baremetal",
    "properties": {
      "cpu_arch": "<x86_64 or aarch64>",
      "baremetal_capabilities": {"boot_mode": "<bios or uefi>"},
      "node_type": "<class_for_node>",
      "interfaces": [
         { "name": "<eth0>", "mac_address": "<ff:ff:ff:ff:ff:ff>" },
         { "name": "<eth1>", "mac_address": "<aa:aa:aa:aa:aa:aa>" }
      ],
      "ipmi_username": "<USERNAME>",
      "ipmi_password": "<PASSWORD>",
      "ipmi_terminal_port": <unique_port_number>,
      "management_address": "<mgmt_ip_addr>",
      "baremetal_deploy_kernel_image": "<glance_uuid>",
      "baremetal_deploy_ramdisk_image": "<glance_uuid>"
    }
  },
  {
     #node 2 info...
  }
]
```

Then, run the command:

```
openstack hardware import \
    [--dry-run] \
    [--skip-existing] \
    --file <json_file>
```

`--dry-run` will print the configuration to your terminal, instead of sending the command

`--skip-existing` will, when adding multiple nodes, skip any that have already been enrolled. This allows re-running by appending to the same json file.

#### Watching Progress

After a node has been "enrolled", Doni will synchronize the state for Ironic and Blazar.

Get the UUID with `openstack hardware list`, then get the detailed info with `openstack hardware show <uuid>`. Each worker will eventually transition from `PENDING` to `IN Progress` to `STEADY`.

Afterwards, the node will be visible in the rest of the system.

* in the Horizon Web UI under `leases/host calendar`
* In the Admin Web UI under `admin/system/ironic-baremetal-provisioning`
* In the output of `openstack baremetal node list`
* In the output if `openstack reservation host list`

### Updating a node's availability

It's possible to "block out" a period of time for a bare metal node so that users cannot reserve it. This can be useful for performing maintenance or managing/accessing the hardware outside of Chameleon. You can update a node's availability by PATCHing its /availability subresource.

For each availability window, a maintenance lease is created in the reservation system. This lease will show up in the host calendar so that users can see when the node will be available once again.

> **Note**: avoid manually updating the maintenance leases or deleting them in Blazar! Instead, manage them via the inventory service.

```shell
# Note: obtain the hardware's $UUID by, e.g., openstack hardware list
openstack hardware set 4ea18b84-c182-48c5-ac23-3d6cdccd5ec1 \
  availability --add 2021-05-01T00:00:00Z 2021-06-01T00:00:00Z
```

To remove a previously-added window:

```shell
# Remove availability window at slot 0 (i.e., the first one in the list)
openstack hardware set 4ea18b84-c182-48c5-ac23-3d6cdccd5ec1 --delete 0
```

To update an existing window:

```shell
# Update availability window at slot 0 (i.e., the first one in the list)
openstack hardware set 4ea18b84-c182-48c5-ac23-3d6cdccd5ec1 \
  availability --update 0 2021-05-01T00:00:00Z 2021-07-01T00:00:00Z
```

## KVM

⏳ Coming soon!

## Edge Devices

⏳ Coming soon!
