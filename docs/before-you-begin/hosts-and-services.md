# Hosts and Services

## Types of Host

A Chameleon Site, deployed via CHI-in-a-box, consists of **`Control Nodes`**, which run the OpenStack services, and **`Compute Nodes`**, which host user workloads. Our primary configuration of  CHI-in-a-box currently only supports Baremetal Compute nodes, via OpenStack Ironic. For the rest of the document, we will refer to this variant of compute nodes as **`Baremetal Nodes`**.

{% hint style="warning" %}
This means that the smallest possible site **requires two machines**, one Controller Node to run all the services, and a second, dedicated Baremetal Compute node, which will be in use by a single user at a time.
{% endhint %}

You can also use an (optional) **`Deploy Host`**, which is only responsible for executing Ansible commands to configure other hosts. It makes upgrading and scaling larger configurations more convenient, but is unneeded in a monolithic installation.

It is possible to segregate services onto separate hosts more finely, for example to scale out network routing, monitoring, or database roles independently. Such customization is outside the scope of this guide, [refer to Kolla-Ansible's description of the host types for more detail](https://docs.openstack.org/kolla-ansible/latest/admin/production-architecture-guide.html#node-types-and-services-running-on-them).

## Overview of Services

A minimal CHI-in-a-Box deployment consists of:

* Dashboard: Horizon
* Identity: Keystone
* Networking: Neutron
* Compute: Nova
* Disk Images: Glance
* Baremetal: Ironic
* Reservation: Blazar
* Inventory: Doni

Optionally, an Object Store can be provided by Swift or Ceph RGW, and a Shared Filesystem provided by Manila



