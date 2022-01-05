# Baremetal Nodes

A Baremetal node is externally managed by Openstack Ironic, and the entire machine is provided as an instance to a user.

### Network Boot

All Baremetal nodes must be able to network boot from PXE or iPXE

### Out of Band Management

The following operations must be supported via an out of band mechanism:

* Set Power On
* Set Power Off
* Query Power Status
* Set temporary boot device

#### Minimum Supported: IPMI2.0

IPMI 2.0 implements a standardized mechanism for the above operations

#### Recommended: Redfish

Redfish adds support for out of band inventory collection.

### Provisioning Process

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

#### Optional capabilities

While not required, the following capabilities can be supported for a better user experience:

* Serial console over LAN/VNC
* Boot option (BIOS, UEFI) setting adjustment
