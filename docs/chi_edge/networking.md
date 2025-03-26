# CHI@Edge Networking

CHI@Edge makes different assumptions than "normal" openstack when it comes to networking.

While Neutron is still running, it is only used for floating IPs, and end-users don't create/delete networks, subnets, ports, or routers themselves.

Instead, the Calico CNI plugin for kubernetes is managing most networking, and all container -> container networking, and neutron and zun are configured to provide a minimal "shim" around this.



## Network Architecture

```mermaid
flowchart LR

    neutron-router((Neutron \n Router))

    subgraph public network
        public-subnet[public subnet: \n 172.18.200.0/24]
    end

    subgraph caliconet network
        direction TB
        
        subgraph calico-subnet[calico subnet: 192.168.0.0/16]
            calico-node((calico bgp \n routing))
            calico-node-- 192.168.1.1/24 --- node1-cidr[192.168.1.0/24]
            calico-node-- 192.168.2.1/24 --- node2-cidr[192.168.2.0/24]
            calico-node-- 192.168.N.1/24 --- node3-cidr[192.168.N.0/24]
        end
        
    end

    public-subnet-- 172.18.200.2/24 --- neutron-router
    neutron-router-- N:192.168.0.1/16 \n C:192.168.0.2/16 --- calico-node
```

All neutron "sees" is that some addresses in the "calico-subnet" send traffic, respond to messages, and so on.
Calico's BGP routing handles getting ipv4 traffic from neutron to the actual destination, which may traverse multiple kubnernetes nodes before reaching a container.

## Configuration


To start with, we need to know/define the kubernetes cluster CIDR.
We specified this either during installation, or it can be found by running:
`kubectl get installations default -o json  | jq '.spec.calicoNetwork.ipPools'`

Which will output something like:
```
[
  {
    "allowedUses": [
      "Workload",
      "Tunnel"
    ],
    "blockSize": 26,
    "cidr": "192.168.0.0/16",
    "disableBGPExport": false,
    "disableNewAllocations": false,
    "encapsulation": "VXLANCrossSubnet",
    "name": "default-ipv4-ippool",
    "natOutgoing": "Enabled",
    "nodeSelector": "all()"
  }
]
```

So in our example, the cluster CIDR is `192.168.0.0/16`

We also are concerned with the subnet used for Openstack API traffic, corresponding to the subnet for `kolla_internal_vip_address` in our kolla-ansible config. Here, that is `172.18.200.0/24`

Finally, we need to know what CIDR we'll use for Neutron-managed floating IPs. Here, we've chosen the same CIDR as the API, also `172.18.200.0/24`. We'll need to be careful not to select overlapping ranges.


We now have our minimum necessary networks to get things working:

- ClusterCIDR: `192.168.0.0/16`
- Neutron Public CIDR: `172.18.200.0/24`

We'll set up some neutron networks corresponding to these. On our networking node, the "public" subnet/network/cider is present with no vlan tags, in the host namespace, so we'll use provider-network-type "flat"

```
openstack network create \
    --provider-physical-network physnet1 \
    --provider-network-type flat \
    --external \
    --default \
    public

openstack subnet create \
    --network public \
    --subnet-range 172.18.200.0/24 \
    --no-dhcp \
    --gateway 172.18.200.1 \
    public
```

And again for our "internal" network, which will let us map floating IPs onto ones in the calico network.

```
openstack network create caliconet
openstack subnet create \
    --network caliconet \
    --subnet-range 192.168.0.0/16 \
    --no-dhcp \
    caliconet
```

And a neutron router to handle NAT from caliconet -> public
```
openstack router create --external-gateway public public
openstack router add subnet public caliconet
```

Finally, we need to do some fiddling to bridge the neutron router NS with the calico router NS

``` console
# create a veth pair
ip link add veth-cali0 type veth peer veth-caliN
ip link set veth-cali0 up
ip link set veth-caliN up

ip addr add 192.168.150.1/30 dev veth-cali0
ip addr add 192.168.150.2/30 dev veth-caliN
```

<!-- 192.168.233.64/26 via 172.19.0.4 -->

### Verifying L3 connectivity

now that we have both subnets and a router, lets verify a few things.

#### Reaching the router's public IP

The router should be reachable via the public IPv4 internet, or on a dev site, at least from your control/testing host.

Get the router's IP: 
ubuntu@ciablocal:~/chi-in-a-box$ openstack router show public -c external_gateway_info -f json

```json
{
  "external_gateway_info": {
    "network_id": "1ff8a6f2-5947-4921-b994-fd3d3cdeb160",
    "external_fixed_ips": [
      {
        "subnet_id": "fc8393c4-9f91-4c28-af6d-18eadd98c66d",
        "ip_address": "172.18.200.169"
      }
    ],
    "enable_snat": true
  }
}
``` 

```console
ubuntu@ciablocal:~/chi-in-a-box$ ping 172.18.200.169
PING 172.18.200.169 (172.18.200.169) 56(84) bytes of data.
64 bytes from 172.18.200.169: icmp_seq=1 ttl=64 time=0.598 ms
64 bytes from 172.18.200.169: icmp_seq=2 ttl=64 time=0.063 ms
```



1. ping the router's caliconet IP
1. ping a pod IP from the router
