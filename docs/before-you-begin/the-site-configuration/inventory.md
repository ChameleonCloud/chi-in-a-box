# inventory

## Ansible Hosts File

`inventory/hosts` is an ini formatted file. It defines the hosts and groups that cc-ansible will operate on. The majority of this file can be left as-is, and should only be customized by advanced users.

```
# These initial groups are the only groups required to be modified. The
# additional groups are for more control of the environment.
[control]
<host>

[network]
<host>

[compute]
# No compute node; this is a baremetal-only cluster.

[monitoring]
<host>

[storage]
<host>

[deployment]
localhost ansible_connection=local

[baremetal:children]
control
network
compute
storage
monitoring
```

The hostname of your control node will be added to the groups `control`, `network`, `monitoring`, and `storage`.

### Host\_Vars

Files in the `inventory/host_vars` directory set variables scoped to a given host. You will likely only have one host here, so there should be a file named after the hostname of your control node.

By default, it will look like the following:

```
# Initial assumption is that this is also the deployment node,
# therefore any provisioning can be done locally.
ansible_connection: local

#network_interface: eth1
#kolla_external_vip_interface: eth2
```

* `network_interface`: the network interface name that will be used for all internal traffic, and where the haproxy internal vip will be bound.
* `kolla_external_vip_interface`: the network interface name to be used for the external API endpoint.

### Group\_Vars

This is not used by default, but allows you to set variables per group, rather than per host.
