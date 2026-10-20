# Rebind Neutron ports after an Ironic port's switch details change

When an Ironic port's `local_link_connection` changes, Neutron ports already bound through it keep the old values in
`binding:profile`, which NGS (networking-generic-switch) reads whenever Neutron binds or unbinds them. If the NIC was
recabled, it has no network now. If only the record changed, traffic is fine, but the next bind or unbind gives NGS
the old details. This guide copies the new values into those Neutron ports. Instances keep their IP and MAC
addresses. For background, see [Baremetal node configuration](../reference/multi-tenant-networking.md#baremetal-node-configuration).

## Before you start

- Each changed Ironic port already has the new `switch_id`, `port_id` and `switch_info` in its
  `local_link_connection`. This guide copies those values into Neutron, so they have to be right first.
- If `switch_info` changed, NGS has a config section for the new switch. This should list
  `[genericswitch:<switch_info>]`:

    ```shell
    docker exec neutron_server \
      grep '^\[genericswitch:' /etc/neutron/plugins/ml2/ml2_conf.ini
    ```

    If it doesn't, fix the switch's `name` or `ngs_config` (see
    [Ironic Multi-Tenant Networking](../reference/multi-tenant-networking.md)), then run
    `./cc-ansible reconfigure --tags neutron`.

- No Ironic port is in a port group (bond): `openstack baremetal portgroup list --node <node_uuid>` lists nothing.
  This guide doesn't cover bonds.
- You're on the deploy host, with `jq` installed and the
  [OpenStack client set up](../before-you-begin/command-line-interface.md).

## 1. Load admin credentials with the `service` role

Under Neutron's 2025.1 default policy, only the `service` role can change `binding:profile`; `admin` isn't enough.
Load the local admin user's credentials and list its roles:

```shell
source "$CC_ANSIBLE_SITE/admin-openrc.sh"
openstack role assignment list --names \
  --user "$OS_USERNAME" --user-domain "$OS_USER_DOMAIN_NAME" \
  --project "$OS_PROJECT_NAME" --project-domain "$OS_PROJECT_DOMAIN_NAME"
```

If there's no `service` row, add the role:

```shell
openstack role add service \
  --user "$OS_USERNAME" --user-domain "$OS_USER_DOMAIN_NAME" \
  --project "$OS_PROJECT_NAME" --project-domain "$OS_PROJECT_DOMAIN_NAME"
```

## 2. Generate the update commands

Ironic records each Neutron port bound through an Ironic port in `internal_info`, under a key ending in
`_vif_port_id`. This writes an `openstack port set` command for each of them to `~/update-commands.txt`:

```shell
for node in <node_uuid> <node_uuid> ...; do
  openstack baremetal port list --node "$node" \
    --fields uuid node_uuid local_link_connection internal_info -f json
done | jq -r '.[]
  | {local_link_information: [."Local Link Connection"]} as $profile
  | (."Internal Info" | to_entries[] | select(.key | endswith("_vif_port_id"))) as $vif
  | "# node \(."Node UUID")  ironic port \(.UUID)  \($vif.key)",
    "openstack port set --binding-profile \($profile | tojson | @sh) \($vif.value)"' \
  > ~/update-commands.txt
```

Each Neutron port gets two lines:

```text
# node <node_uuid>  ironic port <ironic_port_uuid>  tenant_vif_port_id
openstack port set --binding-profile '{"local_link_information":[{"switch_id":"<switch_id>","port_id":"<switchport>","switch_info":"<switch_info>"}]}' <neutron_port_uuid>
```

Check that the commands for the Ironic ports you changed have the new values. Commands for unchanged Ironic ports do
nothing, and the file is safe to run more than once.

## 3. Update one Neutron port and check it

Try one first, so that a problem breaks one node, not all of them.

1. Run one command for an Ironic port you changed. It can take a minute or more if the old switch is down.

2. Check the Neutron port, whose UUID is the command's last argument:

    ```shell
    openstack port show <neutron_port_uuid> \
      -c status -c binding_host_id -c binding_vif_type -c network_id -c device_id
    ```

    - `status` is `ACTIVE` and `binding_vif_type` is `other`: it worked.
    - `binding_host_id` is empty: the port isn't bound now (for example, during a rescue), and Ironic copies the new
      values when it next attaches it. Test with a different command.
    - Anything else: see [If something goes wrong](#if-something-goes-wrong).

3. Check the switches. The new switchport should carry the network's VLAN
   (`openstack network show <network_id> -c provider:segmentation_id`). The old one shouldn't, unless it's the same
   port renamed or its switch is unreachable.

4. If it's an instance's port (`tenant_vif_port_id`), check that the instance (`device_id`) answers on its floating
   IP address, if it has one.

## 4. Update the rest

`-e` stops at the first command that fails; fix the cause and run the file again:

```shell
bash -ex ~/update-commands.txt
```

Then check a few Neutron ports as in step 3.

## If something goes wrong

| What you see | Why | What to do |
|---|---|---|
| `403`, `... is disallowed by policy` | The admin user doesn't have the `service` role | Redo step 1. If you've just added the role, wait a minute: Keystone can cache role assignments |
| `No Port found for <neutron_port_uuid>` | The Ironic port records a deleted Neutron port | Delete its two lines and run the file again. For a `tenant_vif_port_id`, see [Ironic Node Orphan Nova Instance](../runbooks/IronicNodeOrphanInstance.md) |
| `binding_vif_type` is `binding_failed` | NGS couldn't configure the new switchport: usually it has no config section for the new switch, or the switch's `ngs_physical_networks` excludes the network's physical network | Find the Neutron port's UUID in the `neutron_server` log, fix the config, run `./cc-ansible reconfigure --tags neutron`, and run that command again |
| Commands for Neutron ports leaving one switch each take a minute or more | That switch is down but still in the NGS config | Slow, not harmful. To speed up step 4, remove the switch from the NGS config and run `./cc-ansible reconfigure --tags neutron` first |
| `Failed to unplug port` in the `neutron_server` log, or the old switchport still has the VLAN | NGS couldn't reach the old switch, or the old switchport no longer exists. It binds the new one anyway | If the old switchport exists, remove the VLAN by hand once its switch is reachable |
| `status` is `ACTIVE` and the VLAN is right, but the instance has no address | Its DHCP lease expired while it was disconnected | It gets an address at its next DHCP retry, or when it reboots |

## When you've finished

- If you added the `service` role in step 1, remove it:

    ```shell
    openstack role remove service \
      --user "$OS_USERNAME" --user-domain "$OS_USER_DOMAIN_NAME" \
      --project "$OS_PROJECT_NAME" --project-domain "$OS_PROJECT_DOMAIN_NAME"
    ```

- Delete `~/update-commands.txt`.
