**Summary**: an Ironic node is in a state it will not leave by itself: `error`, `deploy failed`, `clean failed`, `inspect failed`, a long-running `-ing` state, a node Ironic still holds for an instance Nova has deleted, or a node parked in maintenance.

**Consequences**: the node cannot be launched on. It can still be reserved in Blazar, so a user may hold a lease on hardware that cannot deploy.

This page has one section per group of states. Each gives what the state means, what to check before acting, the fix, a post-check, and when to park the node instead. For the single `error` alert see also [Ironic Node Error State](IronicNodeInErrorState.md).

### Before you act on any node

Run these first. Use admin credentials: a non-admin cannot see other projects' servers and will wrongly report "not found".

```shell
node=<node name or uuid>
openstack baremetal node show $node \
  -c uuid -c provision_state -c target_provision_state -c power_state \
  -c maintenance -c maintenance_reason -c fault -c last_error \
  -c instance_uuid -c reservation -c provision_updated_at
```

1. **Nova server, any status.** If the node has an `instance_uuid`:
   ```shell
   openstack server show <instance_uuid>
   openstack server list --all-projects --deleted -c ID -c Status -f value | grep <instance_uuid>
   ```
   A server in `ERROR` counts as a server. "Gone" means the first command says not found **and** the second shows the id as `DELETED`.
   Also look at what Placement holds against the node, because a server can exist without Ironic knowing it. The node's resource provider has the same uuid as the node:
   ```shell
   openstack resource provider show <node uuid> --allocations
   ```
   Each allocation consumer is a Nova server id. Expect none on a node with no server.
1. **Tenant ports bound to the node.**
   ```shell
   openstack baremetal node vif list $node
   openstack port list --host <node uuid> --device-owner compute:nova
   ```
   Expect both to be empty on a node with no server. `port list --host` without the owner filter also shows Ironic's own ports (`baremetal:none`); those do not count.
1. **Blazar lease.** Find the node's Blazar host (`openstack reservation host list`, match `hypervisor_hostname` to the node uuid) and run `openstack reservation allocation show host <host id>`. Note any lease that is running or about to start.

Warnings that apply everywhere:

- **Never undeploy a node whose Nova server is alive** (`ACTIVE`, `BUILD`, `REBOOT`, and so on). Undeploy destroys the instance. If Nova and Ironic disagree and the server is alive, stop and find out why.
- **A Nova "not found" on its own is not proof the server is gone.** Check that you are using admin credentials and that the server shows up in `openstack server list --all-projects --deleted`.
- `openstack server delete` frees the node only when the server has a host. Deleting an `ERROR` server that never got a host removes the record and leaves the node as it was. An `ERROR` server belongs to a user; follow your site's policy before deleting it.
- Do not delete a bound tenant port by hand while a Nova server still owns it.
- Undeploy and `provide` boot a cleaning ramdisk only if automated cleaning is on. The default chi-in-a-box config sets `automated_clean = False`, so an undeploy does not erase disks. If your site turns it on, do not undeploy a node whose lease is about to start.
- Do not clear a maintenance flag that Ironic set (the node shows a `fault`, such as `clean failure` or `power failure`) until the cause is fixed.
- A hammer can act before you do. The hourly `hammer_ironic_error_resetter` timer may undeploy an `error` node, and the `hammer_dirty_ports` and `periodic-inspector` timers also touch nodes. Check what is enabled with `systemctl list-timers` on the hammers host. To stop one while you work: `systemctl stop hammer_ironic_error_resetter.timer`, and start it again afterwards.

### Parking a node

If you cannot fix a node now, put it in maintenance with a reason that names the ticket and the problem, so nobody has to guess later:

```shell
openstack baremetal node maintenance set $node --reason "<ticket>: <what is wrong>"
```

A reason like `<ticket>: ipmi unreachable` is good. An empty reason, or one with no ticket, is not parking, it is losing the node. List parked nodes and their reasons with:

```shell
openstack baremetal node list --maintenance --fields uuid name provision_state maintenance_reason
```

A parked node still appears in Blazar. If it will stay parked, make sure users cannot reserve it (check the Blazar host's `reservable` setting, `openstack reservation host show <host>`), and tell the owner of any lease on it.

### Error or deploy failed after a teardown

**What it means**: a teardown (instance delete or a failed deploy) did not finish. `last_error` usually names the step, for example unbinding or clearing a Neutron port, or a lock held by a conductor. The node sits in `error` or `deploy failed` and nothing retries it.

**Check before acting**: the three checks above. The cases that matter:

- No Nova server and no tenant port bound: safe to undeploy.
- Node still holds the `instance_uuid` of a server Nova has deleted (not found in `server show`, `DELETED` in the deleted list), and no VIF or tenant port is bound: the server is gone, so this is safe to undeploy. This is common after a user deletes a server while it is still deploying.
- Nova server in `ERROR`, node still holds its `instance_uuid`: deleting the server (user policy permitting) lets Nova drive the teardown.
- Nova server alive: do not undeploy. Tell the owner.
- Tenant port still bound but no server: the teardown cannot finish while the port is bound. Find out why (Neutron health) and park if it persists.

**Fix**:

```shell
openstack baremetal node undeploy $node
```

If `last_error` points at a Neutron timeout (for example a 504 from Neutron when clearing a port binding), check Neutron is healthy first, then retry once.

**Post-check**: wait for the node to leave `deleting`/`cleaning`, then:

```shell
openstack baremetal node show $node -c provision_state -c power_state -c instance_uuid -c maintenance -c last_error
openstack baremetal node vif list $node
openstack port list --host <node uuid> --device-owner compute:nova
```

Expect `available`, power `power off`, no `instance_uuid`, no `last_error`, no VIF and no tenant port bound. Placement should show no allocation against the node's provider. If the node comes back to `error` or `deploy failed` with the same error, do not loop: park it.

**Park when**: undeploy fails twice with the same error, a tenant port cannot be unbound, or a live Nova server blocks the fix.

### Clean failed

**What it means**: a manual clean (or an automated one, if enabled) failed. Ironic usually sets maintenance and a `fault` of `clean failure`, so the node is out of scheduling.

**Check before acting**: `last_error` and the conductor log for the failed step. Check the BMC is reachable (`openstack baremetal node validate $node`). Run the Blazar check: cleaning boots a ramdisk, so do not start it close to a lease.

**Fix**: fix the cause first, then in this order:

```shell
openstack baremetal node manage $node
openstack baremetal node maintenance unset $node
openstack baremetal node provide $node
```

`manage` takes the node to `manageable`. Clear maintenance only after the cause is fixed. `provide` moves the node to `available` and runs cleaning if it is enabled.

**Post-check**: `provision_state` is `available`, `maintenance` is False, `last_error` is empty.

**Park when**: the cause is hardware (disk, BMC, NIC) or the clean fails again.

### Inspect failed and manageable

**What it means**: inspection timed out or failed (`inspect failed`), or the node is in `manageable`. A `manageable` node is not scheduled. An operator may be holding it there on purpose.

**Check before acting**: is the node in maintenance with a reason? Is power state readable? Is someone working on it (check the ticket in the maintenance reason, or ask)? Note the periodic inspector inspects and may then `provide` nodes, which would release a node an operator is holding. Check `systemctl list-timers` and its configuration before leaving a node in `manageable`.

**Fix**:

```shell
openstack baremetal node inspect $node
# wait for provision_state manageable
openstack baremetal node provide $node
```

Only run `provide` on a node you mean to release.

**Post-check**: `available`, `maintenance` False, not an `inspect failed` again. If inspection fails repeatedly with a timeout or "ramdisk never calls back", the cause is usually the BMC, boot order, or the provisioning network, not Ironic.

**Park when**: inspection fails twice, or the node needs hardware work. Use a reason like `<ticket>: inspection ramdisk never calls back`.

### Stuck -ing states

**What it means**: the node has sat in `deploying`, `cleaning`, `deleting`, `inspecting`, or in a wait state (`wait call-back`, `clean wait`, `inspect wait`) for much longer than a normal run. A non-empty `reservation` is the conductor that holds the lock.

**Check before acting**:

```shell
openstack baremetal node show $node -c provision_state -c reservation -c provision_updated_at
openstack baremetal conductor list
```

If `reservation` names a conductor that is not alive in the list, the node is held by a dead conductor. For `wait call-back`, check the Nova server: if it is still `BUILD`, the deploy is alive on the Nova side.

**Fix**: there is no safe generic fix.

- **Never undeploy a `wait call-back` node while its Nova build is alive.** It hangs the build. Let Nova time the build out first.
- `clean wait` and `inspect wait`: `openstack baremetal node abort $node` moves the node to the matching failed state, then use the section above.
- `deploying`, `cleaning`, `deleting` with a dead or stuck conductor: restarting the conductor that holds the lock moves the node to a failed state (from reading Ironic source, not tested here), but it also interrupts every other task on that conductor. Do it only in agreement with the site lead, one conductor at a time.

**Post-check**: the node reaches a failed or stable state and `reservation` clears. Then follow the section for that state.

**Park when**: the node returns to the same stuck state after one conductor restart.

### Undead: Ironic holds an instance Nova deleted

**What it means**: the node is `active` with an `instance_uuid`, but Nova has no such server. The delete reached Nova and not Ironic. Users cannot launch on the node, and a lease on it is wasted.

**Check before acting**: the three checks above, plus positive proof the server is gone:

```shell
openstack server show <instance_uuid>                      # not found
openstack server list --all-projects --deleted -c ID -c Status -f value | grep <instance_uuid>
```

You want the second command to show the id as `DELETED`, with admin credentials. A bare "not found" with no record in the deleted list is not proof: do not undeploy. Also compare with `openstack baremetal node list --provision-state active --unassociated`, which is the opposite case (Ironic is active but has no instance).

**Fix**:

```shell
openstack baremetal node undeploy $node
```

This is allowed under a lease because the instance is proven gone. Tell the lease owner if the lease was running.

**Post-check**: the node reaches `available`, `instance_uuid` empty, power off, `openstack baremetal node vif list $node` empty, and the Placement provider shows no allocation (`openstack resource provider show <node uuid> --allocations`).

**Park when**: undeploy fails, or you find a bound port or allocation you cannot explain.

### Maintenance parked

**What it means**: an operator or Ironic put the node in maintenance. It is out of scheduling until the flag is cleared.

**Check before acting**: read the reason and the `fault` field.

```shell
openstack baremetal node list --maintenance --fields uuid name provision_state maintenance_reason
openstack baremetal node show $node -c maintenance_reason -c fault
```

Group the nodes by what they wait on. A reason that names a ticket is fine. These need action:

- no reason, or a reason with no ticket;
- a ticket that is closed or does not exist;
- a node parked long ago whose hardware may have been fixed;
- a node in `active` that still has a running lease on it (the user is affected; say so in the ticket).

**Fix**: for a node with no reason, find out why, then set one:

```shell
openstack baremetal node maintenance set $node --reason "<ticket>: <what is wrong>"
```

For a node whose cause is fixed, clear it only after checking the state is stable:

```shell
openstack baremetal node maintenance unset $node
```

**Post-check**: `maintenance` is False and the node reaches or stays `available`; or the reason now starts with a ticket.

**Park when**: this is the parked state. Every parked node has a reason in the form `"<ticket>: <what>"`.
