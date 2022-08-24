# Instance networking diagnostics

### Instance unreachable over floating IP

1. **Check connectivity over the private IP**. Get the network(s) associated with the instance, then try to ping or otherwise test that a port (like SSH) is open from within the namespace.

```shell
# Get list of ports for instance
instance=<instance_id>
ports=$(openstack port list --server $instance -f value -c ID)

# Get static IP assignments (and Neutron network IDs)
networks_and_ips=$(for port in $ports; \
do openstack port show -f json -c network_id -c fixed_ips $port \
  | jq -r '.network_id + "\t" + (.fixed_ips|sub("ip_address='\''(?<ip>[0-9\\.]+)'\''.+$"; "\(.ip)"))'; \
done)

# Test each static IP over the Neutron network namespace
xargs sh -c 'ip netns exec qdhcp-$0 nc -z -w2 $1 22 || echo $1 unreachable' <<<"$networks_and_ips"
```

If connectivity works over the private IP, then the problem likely exists somewhere in Neutron's IPTables, or in OpenVSwitch.

1. **Check IPTables rules on public network router**. This router is usually called "admin-router" and is owned by the `opentstack` admin project.

```shell
public_router_id=$(openstack router show admin-router -f value -c id)
ip netns exec qrouter-$public_router_id iptables -t nat -vnL
```

You should see rules like this:

```
Chain neutron-l3-agent-PREROUTING (1 references)
 pkts bytes target     prot opt in     out     source               destination
    0     0 REDIRECT   tcp  --  qr-+   *       0.0.0.0/0            169.254.169.254      tcp dpt:80 redir ports 9697
 3267  154K DNAT       all  --  *      *       0.0.0.0/0            192.5.87.143         to:10.100.100.14

Chain neutron-l3-agent-float-snat (1 references)
 pkts bytes target     prot opt in     out     source               destination
 134K 8083K SNAT       all  --  *      *       10.100.100.14        0.0.0.0/0            to:192.5.87.143
```

If there are no rules here for your floating IP or for your static IP assignment, it may help to restart the neutron-l3-agent via `docker restart neutron_l3_agent`. This agent takes a while to restart; you will have to be patient while it re-syncs the state of all the IPTables rules in all the network namespaces maintained by Neutron.

### Instance unreachable over private IP

1. **Check the node console**. It could be that the node failed to boot (this is the most likely culprit). If the node console cannot be read via the web interface, then you can try attaching via `ipmiconsole` from a control node on the provisioning network.

```shell
# Get the bare metal node ID for the instance
node_id=$(openstack server show -f value -c 'OS-EXT-SRV-ATTR:hypervisor_hostname' $instance)

# Get the IPMI address of the node
ipmi_address=$(openstack baremetal node show -f json $node_id | jq -r .driver_info.ipmi_address)

# Attach an IPMI console to the node (this will kill Nova's serial console; only one console can be attached.)
ipmiconsole -h $ipmi_address -u root -P
```

Try logging in to the node via the console and seeing its IP address assignments using `ip addr`. If it does not have the static IP assigned, it is likely that DHCP failed when the node was booting. Check the Neutron DHCP agent for errors. It may also help to simply kill the dnsmasq process for the network in question (they typically have the network UUID as part of their `ps` entry), or restart the entire DHCP agent, which should kill and restart all dnsmasq processes. To check that the node is able to network at all, you can try manually assigning an IP address using `ip addr add <ip> dev <interface>` with an IP address that is unused. The IP should be in the same subnet as the one assigned to the instance by neutron. You can find the interface to use by looking at the output of `ip addr`.

1. **Check that the node's switch port has the right VLAN assigned.** If the instance hasn't been deleted, any switch configurations related to the instance should still be active. You will first need to figure out which switch the instance's node is physically connected to, and on which switchport. This can be figured out via Ironic. Once you know the switch port, you can check the switch to see if the Neutron network's VLAN is assigned to that switch port. If this is not the case, it is likely that the node has no connectivity.

```shell
# Find all ports registered on node
node_ports=$(openstack baremetal port list --node $node_id -f value -c UUID)

# Get physical switch information for each port
for port in $node_ports; do 
  openstack baremetal port show $port -f json \
    | jq -r '.local_link_connection | (.switch_info + "\t" + .port_id)'
done
```

Once you know which switch the node is connected to, you can log in to the node and examine its configuration. You will need the credentials for the switch to do this. Run the following on the node that has Neutron running:

```shell
# Print switch configuration for switch name
# (for Corsa switches, look for 'switchIP' and 'token', for Dell switches, look for 'ip' and 'password')
crudini --get --format=lines /etc/kolla/neutron-server/ml2_conf.ini genericswitch:$switch_name

# Get VLAN tag for the network
vlan=$(openstack network show $network_name_or_id -f value -c provider:segmentation_id)
```

#### Dell switches

Chameleon Dell switches (S6000 model) are configured over remote SSH sessions currently. You can log in to the switch from a node that has access to the switch's out-of-band interface (such as the Neutron node.)

```shell
# Enter 'password' interactively
ssh $switch_user@$switch_ip
```

Interact with the prompt to show which ports are assigned to which VLAN tag.

```
SWITCH_NAME# conf
SWITCH_NAME(conf)# interface vlan <VLAN>
SWITCH_NAME(conf-if-vl-<VLAN>)# show config
```

You should see the node's switchport ID listed as 'untagged' on this VLAN. If you do not see this, adding it manually might fix things temporarily. **Note**: this applies immediately! There is no confirm or save flow. Be advised.

```
# e.g. 'untagged Te 1/2/3'
SWITCH_NAME(conf-if-vl-<VLAN>)# untagged <PORT_ID>
```

#### Corsa switches

Corsa switches can be queried over a remote HTTP API using an authentication token.

```shell
# View tunnel configuration for bridge associated with VLAN.
# This first fetches a list of all bridges, filters the list for only our VLAN, then
# follows a link to see the tunnels for that bridge.
curl -k -H"authorization: $token" https://172.30.0.4/api/v1/bridges?list=1 \
  | jq '.list | map(select(.["bridge-descr"] | contains("<VLAN>")))[0].links.tunnels.href' \
  | xargs -I{} curl -k -H"authorization: $token" {}?list=1 \
  | jq .

# View controller configurations for bridge associated with VLAN.
# This first fetches all bridges, filters for our VLAN, then requests all data
# for the controller associated with the bridge.
curl -k -H"authorization: $token" https://172.30.0.4/api/v1/bridges?list=1 \
  | jq -r '.list | map(select(.["bridge-descr"] | contains("<VLAN>")))[0].links.controllers.href' \
  | xargs curl -k -H"authorization: $token" \
  | jq -r '.links | to_entries[].value.href' \
  | xargs -L1 curl -k -H"authorization: $token" \
  | jq .
```

**TODO**: from this point onward, you may need to consult with a member of the team familiar with Corsa switches. In particular, looking at OpenFlow flow rules requires logging on to the switch via an interactive SSH session.
