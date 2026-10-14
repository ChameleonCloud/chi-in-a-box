**Summary**: an Ironic node still holds the `instance_uuid` of a server that Nova cannot find. The node can be in any state: `active`, `deploy failed` or `error`. A common cause is a user deleting a server while it is still deploying.

**Consequences**: Nova cannot place a new server on the node while Ironic holds the old one. An `active` orphan looks healthy, so a lease on it is wasted until someone notices.

This page covers one decision: is the server gone, so it is safe to undeploy, or should you park the node? For anything it doesn't cover, park the node and escalate.

**Never undeploy a node whose Nova server is alive.** Undeploy destroys the instance.

### Check

Use admin credentials for the site (for example `admin-openrc.sh`). A non-admin cannot see other projects' servers and will wrongly report "not found". In the examples, `<node>` is the node name or uuid, `<node_uuid>`, `<instance_uuid>`, `<instance_name>` and `<port_uuid>` stand for real values, and only the rows that matter are shown.

```shell
openstack baremetal node show <node> \
   --fields uuid provision_state maintenance maintenance_reason last_error instance_uuid
openstack server show <instance_uuid> -c name -c id -c status -c OS-EXT-SRV-ATTR:hypervisor_hostname
```

If the server exists, `OS-EXT-SRV-ATTR:hypervisor_hostname` is the uuid of the node it is on. If it is empty, Nova has no node for the server.

Pass, the server is gone. Here a user deleted it while the node was still deploying:

```console
$ openstack baremetal node show <node> --fields provision_state last_error instance_uuid
| instance_uuid   | <instance_uuid>                                                       |
| last_error      | Deploy step deploy.switch_to_tenant_network failed: ... No Port found |
|                 | for <port_uuid>: ... Port <port_uuid> could not be found.             |
| provision_state | deploy failed                                                         |
$ openstack server show <instance_uuid> -c name -c id -c status -c OS-EXT-SRV-ATTR:hypervisor_hostname
No server with a name or ID of '<instance_uuid>' exists.
```

Fail, the server still exists. Here it is `ERROR`:

```console
$ openstack server show <instance_uuid> -c name -c id -c status -c OS-EXT-SRV-ATTR:hypervisor_hostname
| OS-EXT-SRV-ATTR:hypervisor_hostname | <node_uuid>     |
| id                                  | <instance_uuid> |
| name                                | <instance_name> |
| status                              | ERROR           |
```

Delete first, the server is `ERROR` but Nova has no node for it:

```console
$ openstack server show <instance_uuid> -c name -c id -c status -c OS-EXT-SRV-ATTR:hypervisor_hostname
| OS-EXT-SRV-ATTR:hypervisor_hostname | None            |
| id                                  | <instance_uuid> |
| name                                | <instance_name> |
| status                              | ERROR           |
```

### Decide

| What the check shows | Action |
|---|---|
| `server show` says not found | undeploy (below) |
| The server is `ERROR` and `OS-EXT-SRV-ATTR:hypervisor_hostname` is empty | (BE VERY CAREFUL HERE AND DOUBLE CHECK) delete the server with `openstack server delete <instance_uuid>`. With no node recorded, this only removes Nova's record and does not touch the node. Run the check again: it now says not found, so undeploy |
| The server exists in any other way (any other status, or a `hypervisor_hostname`) | do not undeploy; park the node and escalate with the node uuid, `instance_uuid`, `last_error` and the server's status |

### Undeploy

```shell
openstack baremetal node undeploy <node>
```

Once the node leaves `deleting`/`cleaning`, check it is `available` with no `instance_uuid` and no `last_error`. If it goes to `error`, `deploy failed` or `clean failed`, park it. Do not retry in a loop.

### Park

Put the node in maintenance with a reason that names a ticket in your site's issue tracker:

```shell
openstack baremetal node maintenance set <node> --reason "<ticket>: <what is wrong>"
```

A maintenance flag with no reason, or no ticket, loses the node. To list parked nodes:

```shell
openstack baremetal node list --maintenance --fields uuid name provision_state maintenance_reason
```
