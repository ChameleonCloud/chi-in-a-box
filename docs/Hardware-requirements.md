## Management Node(s)

We strongly suggest that a management node used to run CHI-in-a-box meet or exceed the following specifications.
Individual requirements can be worked around for a dev setup, but will cause significant operational issues in practice.

Specifications:
* CentOS8 Operating System, with python3 installed.
* 8Gb of Ram
* 40GB of disk space (scaling to more, depending on the number of user images created)
* A dedicated network interface, connected to a publicly routable subnet, with at least 2 available public IPs.
* A dedicated network interface, connected to the same l2 domain as any bare-metal nodes.
* A dedicated network interface used to administer the management node.

## Network fabric

Currently CHI-in-a-Box has built-in support for a variety of physical switches, including:

* Cisco 300-series
* Corsa DP2000-series (**official support**)
* Dell Force10 (**official support**)
* Dell PowerConnect
* Juniper Junos

(**official support** denotes switches that are regularly tested by the Chameleon team)

A full list is available [here](https://docs.openstack.org/networking-generic-switch/latest/supported-devices.html). The network switches must be remotely manageable, typically with SSH (though some vendors have different interfaces, which should be supported if they are the primary interface.) For security, those interfaces should only be exposed on an internal network isolated from tenant networks controllable by users.

Switch login credentials will be templated out as plain text into several root-owned files on the CHI-in-a-Box management nodes responsible for orchestrating the network topology. The credentials themselves are encouraged to be stored encrypted in the `passwords.yml` file of your [site configuration](./The-site-configuration).

## Bare metal nodes

Bare metal provisioning on Chameleon, at a high level, requires access to IPMI for power/boot order management and the ability to PXE boot or accept remote virtual media. Typically a baseboard management controller's out-of-band Ethernet interface is used for IPMI operations, and this network is physically separated from the node's network interfaces. The full range of supported hardware is described in the documentation for [Ironic](https://docs.openstack.org/ironic/latest/admin/drivers.html), the provisioning engine used by CHI-in-a-Box. A typical bare metal provisioning workflow works like the following (see if your hardware can support something similar):

1. Set boot device to PXE
2. Stage a ramdisk image over TFTP
3. Configure network fabric to logically connect node's primary NIC to network segment dedicated to provisioning
4. IPMI power on the node; node boots from Ironic ramdisk image delivered via TFTP over provisioning network
5. Ramdisk image creates iSCSI target on node
6. User disk image is transferred via iSCSI over provisioning network
7. Set boot device to local disk
8. Disconnect node NIC from provisioning network; logically connect to user tenant network instead
9. Restart the node via IPMI
10. Node boots from local image and is assigned layer-3 addresses via DHCP on user's tenant network

### Optional capabilities

While not required, the following capabilities can be supported for a better user experience:

* Serial console over LAN/VNC
* Boot option (BIOS, UEFI) setting adjustment

### Not enough support?

These requirements are not set in stone; anything technically possible can be made a reality with some elbow grease and Python hacking. Let us know what you think.

