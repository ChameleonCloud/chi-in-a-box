# Host Networking Configuration

Openstack, and CHI-in-a-Box, have very specific requirements of the host network configuration. Our default config seeks to provide the following logical network interfaces.

* [ ] Public API Interface: (Interface where haproxy public VIP is bound, must be reachable by all networking nodes)
* [ ] Public Neutron Interface: Interface where public IPs are bound, provides external connectivity to instances
* [ ] Internal API Interface: (Interface where haproxy private VIP is bound, must be reachable by all networking nodes)
* [ ] Internal Neutron Interface: interface that neutron will map tenant networks onto
* [ ] Admin SSH interface (optional): It can be useful to have an extra way in, especially if the other interfaces are shared.

{% hint style="warning" %}
Note that there are 4+ interfaces here! These can be separate physical interfaces, but must at least be separate logical interfaces.
{% endhint %}

## Handling ARP with Multiple Interfaces

For the public network in particular, issues can arise when multiple interfaces are connected to the same L2 segment. The default behavior in linux is to ARP from any interface on that segment, rather than only the interface with an assigned IP address.

This can be changed by setting the following in /etc/sysctl.conf

```
net.ipv4.conf.all.arp_ignore=1
net.ipv4.conf.all.arp_announce=2
```

## Separate Physical Interfaces

This has the most physical complexity, but least logical complexity. Assuming the host has 4 interfaces:

* eno1: connected to public network segment on external switch
  * Bind a public IP address to this interface, and set default gateway
* eno2: connected to public network segment on external switch
  * ensure it is not managed by the host (exclude from networkmanager, etc)
* eno3: connected to private network segment on a switch
  * Bind a private IP address to this interface
* eno4: connected to VLAN trunk on the dataplane switch
  * ensure it is not managed by the host (exclude from networkmanager, etc)

### Variables for use in site-configuration

With the above settings, you would set the following values in your site configuration

#### $CC\_ANSIBLE\_SITE/inventory/host\_vars/

```
kolla_external_vip_interface: eno1
network_interface: eno3
```

#### $CC\_ANSIBLE\_SITE/defaults.yml

`external_interface` is set to the other physical interfaces from above.

`bridge_name` is the name of the OVS bridge that will be created, and should be different from the linux bridges created above. We assume `br-ex` for the public bridge, and `br-internal` for the internal one.

```
...
neutron_networks:
  - name: public
    bridge_name: br-ex
    external_interface: eno2
    cidr: <public_ip_subnet/netmask> # cidr of your netblock
    gateway_ip: <gateway_ip> # define next hop IP
  - name: physnet1
    bridge_name: br-internal
    external_interface: eno4
    mtu: 9000
...
```

## Using Fewer Interfaces

It can be inconvenient to use so many physical interfaces. To economize here, we recommend the following logical -> physical mapping, again assuming interfaces `eno1` and `eno2`.

{% hint style="warning" %}
We strongly recommend having an extra interface to SSH to, or other way to recover access in the case of misconfiguration.
{% endhint %}

* eno1: Public Physical Interface
  * Public API interface
  * Neutron External Interface
* eno2: Private Physical Interface
  * Private API interface
  * Neutron physical networks

### Safely connecting the linux networks to neutron networks

{% hint style="warning" %}
Because the public and private interfaces are pulling double duty, care must be taken when attaching the neutron openvswitch bridge to the linux interface.
{% endhint %}

The specific method depends on what network configuration tool your host OS is using. In general, for each physical interface to be shared between usage on the host (including API addresses), and usage by a Neutron network, the following must be done:

1. Create a linux bridge on the host
2. Add the physical interface to that bridge
3. Create a pair of virtual ethernet interfaces (veth pair)
4. add one of the pair to the host bridge
5. use the other end of the pair as the neutron interface.

Example configurations are below for each supported OS, but you're free to use your preferred methods.

{% tabs %}
{% tab title="Ubuntu 18.04" %}
#### Create veth pairs

First, we'll make two pairs of virtual interfaces. These will be used to connect the host network to the neutron networks.

In `/etc/systemd/network/`, create two files:

`20-veth-public.netdev`

```
[NetDev]
Name=veth-publica
Kind=veth
[Peer]
Name=veth-publicb
```

`20-veth-private.netdev`

```
[NetDev]
Name=veth-privatea
Kind=veth
[Peer]
Name=veth-privateb
```

#### Create Linux Bridges

Ubuntu 18.04 is using Netplan for configuration. Your netplan config file should contain the following (although it can have more, of course.)

Adding the veth names to `ethernets` is required to make them usable in the rest of the netplan config, and the `{}` will keep netplan from otherwise configuring them.

{% hint style="warning" %}
Note the bridge names do not contain a `-` or `_`. There's an issue in how ansible renders strings containing these values, and it will cause prechecks to fail.
{% endhint %}

```
network:
  version: 2
  ethernets:
    eno1: {}
    eno2: {}
    veth-publica: {}
    veth-publicb: {}
    veth-privatea: {}
    veth-privateb: {}
  bridges:
    brpublic:
      interfaces:
        - eno1
        - veth-publica
      addresses:
        - <public_ip_address/netmask>
      gateway4: <gateway_on_public_subnet>
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
    brinternal:
      interfaces:
        - eno2
        - veth-privatea
      addresses:
        - 192.5.87.4/23
```
{% endtab %}

{% tab title="Centos8" %}
{% hint style="danger" %}
Warning, centos seems to have MANY edge cases here due to incomplete support for veths in NetworkManager or network-scripts. Use with caution.
{% endhint %}

#### /etc/NetworkManager/NetworkManager.conf

Networkmanager must have its default configuration modified to support autoconnection of veth devices. Add the following at the end of your NetworkManager.conf file

```
[device-veth-public]
match-device=interface-name:veth-public*
managed=1
keep-configuration=no

[device-veth-private]
match-device=interface-name:veth-private*
managed=1
keep-configuration=no
```

This overrides a udev rule that would otherwise prevent networkmanager from controlling these

#### Create Bridges

```
sudo nmcli connection add type bridge \
    con-name brpublic ifname brpublic \
    ipv4.method manual ipv4.dns 8.8.8.8 ipv4.gateway <gateway_ip> \
    ipv4.addresses <public_bind_address>
sudo nmcli connection add type bridge \
    con-name brinternal ifname brinternal \
    ipv4.method manual ipv4.addresses <internal_bind_address>
```

#### Create the veth connection profiles:

```
#Public Veth Pair
sudo nmcli connection add type veth \
    connection.master brpublic connection.slave-type bridge \
    ipv4.method disabled ipv6.method disabled \
    con-name veth-publica  ifname veth-publica veth.peer veth-publicb
sudo nmcli connection add type veth \
    ipv4.method disabled ipv6.method disabled \
    con-name veth-publicb  ifname veth-publicb veth.peer veth-publica
```

```
#Private Veth Pair
sudo nmcli connection add type veth \
    connection.master brinternal connection.slave-type bridge \
    ipv4.method disabled ipv6.method disabled \
    con-name veth-privatea  ifname veth-privatea veth.peer veth-privateb
sudo nmcli connection add type veth \
    ipv4.method disabled ipv6.method disabled \
    con-name veth-privateb  ifname veth-privateb veth.peer veth-privatea 
```
{% endtab %}
{% endtabs %}

### Variables for use in site-configuration

With the above settings, you would set the following values in your site configuration

#### $CC\_ANSIBLE\_SITE/inventory/host\_vars/

```
kolla_external_vip_interface: brpublic
network_interface: brinternal
```

#### $CC\_ANSIBLE\_SITE/defaults.yml

`external_interface` is set to the other end of the veth pair from above.

`bridge_name` is the name of the OVS bridge that will be created, and should be different from the linux bridges created above. We assume `br-ex` for the public bridge, and `br-internal` for the internal one.

```
...
neutron_networks:
  - name: public
    bridge_name: br-ex
    external_interface: veth-publicb
    cidr: <public_ip_subnet/netmask> # cidr of your netblock
    gateway_ip: <gateway_ip> # define next hop IP
  - name: physnet1
    bridge_name: br-internal
    external_interface: veth-internalb
    mtu: 9000
...
```

###
