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
