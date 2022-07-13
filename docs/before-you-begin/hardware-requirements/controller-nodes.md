# Controller Nodes

### Supported Operating Systems

The Controller Node should have **Ubuntu 20.04** installed.

Centos Stream8 is on our roadmap, but not yet supported.

### OS Configuration

OS packages installed

* Python3 (3.6 or higher)
* virtualenv

### Minimum Hardware Specifications

We strongly suggest that a management node used to run CHI-in-a-box meet or exceed the following specifications. Individual requirements can be worked around for a dev setup, but will cause significant operational issues in practice.

* 8Gb of RAM
* 40GB of disk space (scaling to more, depending on the number of user images created)
* 2 separate network interfaces (can be VLANS)

### Recommended Hardware Specifications

* 16Gb of RAM (adds support for centralized logging, and other monitoring features)
* 2TB of disk space (allowing for growth of user images)
* 3 separate network interfaces

### Networks, Interfaces, and Subnets

* Management (Optional): This interface allows SSH access to manage the _controller node_
  * If using a separate _deploy host_, configuration will take place over this interface.
* Internal: This network handles traffic towards the _compute_ and _baremetal_ nodes.
  * The following services use this interface: RabbitMQ, MariaDB, OpenStack internals, Neutron, IPMI
  * 10G or faster is recommended
  * Assign a private IP to this interface.
  * Ensure that at least 2 free IPv4 addresses are available in the same subnet as this assigned private IP.
* Public:
  * This interface provides access to the public openstack APIs, as well as routing traffic between private networks and the internet.
  * The following services use this interface: OpenStack APIs via HTTPS proxy, Horizon, Neutron external bridge
  * 10G or faster is recommended
  * Choose an address and subnet that allows for communication with your upstream gateway.
  * The hostname of the _controller node_ should resolve to this address.
  * Ensure that at least 2 free IPv4 addresses are available in the same subnet as this assigned Public IP. In production, many more are desired.
