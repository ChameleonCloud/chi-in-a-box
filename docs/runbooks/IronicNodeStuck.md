**Summary**: an Ironic node is in a failed state it will not leave by itself: `error`, `deploy failed` or `inspect failed`.

**Consequences**: every launch on the node fails, usually with `No valid host was found`. Blazar can still hand the node out in a lease, so a user may hold a lease on hardware that cannot deploy.

For any state not covered here, or if a fix fails: park the node (below) and open a ticket. Do not retry in a loop. For the single `error` alert, see also [Ironic Node Error State](IronicNodeInErrorState.md).

### Before you act on any node

Use admin credentials. A non-admin cannot see other projects' servers and will wrongly report "not found".

```shell
node=<node name or uuid>
openstack baremetal node show $node \
  -c uuid -c provision_state -c power_state -c maintenance -c maintenance_reason \
  -c fault -c last_error -c instance_uuid -c reservation
```

1. **Nova server.** If the node has an `instance_uuid`, check the server:
   ```shell
   openstack server show <instance_uuid>
   openstack server list --all-projects --deleted -c ID -c Status -f value | grep <instance_uuid>
   ```
   The server is gone only if the first command says not found **and** the second shows the id as `DELETED`. A server in `ERROR` still counts as a server.
1. **Tenant ports bound to the node.** Both should be empty if there is no server:
   ```shell
   openstack baremetal node vif list $node
   openstack port list --host <node uuid> --device-owner compute:nova
   ```
1. **Blazar lease.** Find the node's Blazar host (`openstack reservation host list`, match `hypervisor_hostname` to the node uuid) and note any lease on it that is running or about to start. Tell the owner of a running lease what you are doing.

Rules:

- **Never undeploy a node whose Nova server is alive** (`ACTIVE`, `BUILD`, `REBOOT`, ...). Undeploy destroys the instance.
- A Nova "not found" on its own is not proof the server is gone. Use the `--deleted` check above.
- Do not clear a maintenance flag that Ironic set (the node shows a `fault`, such as `power failure`) until the cause is fixed.

### Parking a node

If you cannot fix a node now, put it in maintenance with a reason that names the ticket:

```shell
openstack baremetal node maintenance set $node --reason "<ticket>: <what is wrong>"
```

A maintenance flag with no reason, or no ticket, loses the node. To list parked nodes:

```shell
openstack baremetal node list --maintenance --fields uuid name provision_state maintenance_reason
```

### Error or deploy failed

**What it means**: a teardown (an instance delete, or cleanup after a failed deploy) did not finish. `last_error` usually names the step, such as clearing a Neutron port binding or a lock held by a conductor. Nothing retries it.

A common cause is a user deleting a server while it is still deploying. The same fix applies to a node that is `active` but holds the `instance_uuid` of a server Nova has deleted.

**Decide using the checks above**:

| Nova server | Tenant port bound | Action |
|---|---|---|
| gone (`DELETED`) or no `instance_uuid` | no | undeploy |
| `ERROR`, node still holds its uuid | any | delete the server (your site's user policy permitting); Nova then drives the teardown |
| alive | any | do not undeploy; find out why Ironic and Nova disagree |
| gone | yes | park; check Neutron |

**Fix**:

```shell
openstack baremetal node undeploy $node
```

If `last_error` names a Neutron timeout (for example a 504), check Neutron is healthy first, then retry once.

**Post-check**: once the node leaves `deleting`/`cleaning`, it should be `available` with no `instance_uuid`, no `last_error` and an empty `vif list`. If it comes back to `error` or `deploy failed`, park it.

### Inspect failed

**What it means**: inspection timed out or failed. The node is not scheduled.

**Check before acting**: is it in maintenance with a ticket? Is someone working on it? Can Ironic read the power state (`openstack baremetal node validate $node`)?

**Fix**: retry inspection once, then release the node:

```shell
openstack baremetal node inspect $node
# wait for provision_state manageable
openstack baremetal node provide $node
```

**Post-check**: `available`, and not `inspect failed` again.

**Park when**: inspection fails twice. Repeated timeouts ("ramdisk never calls back") usually mean BMC, boot order or provisioning network problems, not Ironic.
