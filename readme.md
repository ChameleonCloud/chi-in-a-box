# CHI@Edge Development Environment

## Overview
Simplified single-VM development environment for CHI@Edge

## Quick Start
1. Create and configure the VM
2. Deploy OpenStack services
3. Deploy K3s
4. Validate deployment

## What's Different from Production
- Single VM instead of bare metal
- Local auth instead of federation  
- [other simplifications as you discover them]

## Troubleshooting
[Build this as you go]


## outcome

This will test that the following can be deployed and interoperate

1. openstack control plane: mariadb, rabbitmq, haproxy, keystone, neutron
2. openstack container compute: zun
3. kubernetes: k3s worker + agent

Therefore, it primarily tests the zun - k3s integration.

Step 2 - add blazar reservations to the mix
Step 3 - ?
Step N - have doni + tunelo + balena working
Step N+1 - multiple k3s control
Step N+2 - multiple openstack control


## configure vm
### specifications
8 cores, 16 gb ram, 40gb disk
2 network interfaces
ubuntu 22.04

### steps
1. reserve an m1.xlarge instance
2. launch, connecting 1 interface to sharednet1
3. associate a floating IP


## Setup

Install chi-in-a-box tools

```
chown cc:cc /opt
cd /opt
git clone https://github.com/chameleoncloud/chi-in-a-box
git checkout stable/xena

./cc-ansible install_deps
./cc-ansible init --site /opt/site-config
export CC_ANSIBLE_SITE=/opt/site-config
```

Configure dummy network interfaces for testing.

```
sudo ip link add veth-publica type veth peer veth-publicb
sudo ip addr add 192.168.200.10/24 dev veth-publica
sudo ip link set veth-publica up
sudo ip link set veth-publicb up

sudo ip link add veth-inta type veth peer veth-intb
sudo ip addr add 10.10.10.10/24 dev veth-inta
sudo ip link set veth-inta up
sudo ip link set veth-intb up
```

You should see an output from `ip a` like the following:

```
3: veth-publicb@veth-publica: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 52:fb:11:e5:eb:e9 brd ff:ff:ff:ff:ff:ff
    inet6 fe80::50fb:11ff:fee5:ebe9/64 scope link 
       valid_lft forever preferred_lft forever
4: veth-publica@veth-publicb: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether de:d5:92:38:1e:a7 brd ff:ff:ff:ff:ff:ff
    inet 192.168.200.10/24 scope global veth-publica
       valid_lft forever preferred_lft forever
    inet6 fe80::dcd5:92ff:fe38:1ea7/64 scope link 
       valid_lft forever preferred_lft forever
5: veth-intb@veth-inta: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 0a:ac:00:48:f9:eb brd ff:ff:ff:ff:ff:ff
    inet6 fe80::8ac:ff:fe48:f9eb/64 scope link 
       valid_lft forever preferred_lft forever
6: veth-inta@veth-intb: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether a2:ad:cc:f3:1d:1d brd ff:ff:ff:ff:ff:ff
    inet 10.10.10.10/24 scope global veth-inta
       valid_lft forever preferred_lft forever
    inet6 fe80::a0ad:ccff:fef3:1d1d/64 scope link 
       valid_lft forever preferred_lft forever
```


Set the following in defaults.yml, based on the above interfaces and addresses

```
network_interface: veth-inta
kolla_internal_vip_address: 10.10.10.254
kolla_internal_fqdn: "{{ kolla_internal_vip_address }}"

kolla_external_vip_interface: veth-publica
kolla_external_vip_address: 192.168.200.254
kolla_external_fqdn: "{{ kolla_external_vip_address }}"
```
