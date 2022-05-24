# Ironic (bare metal)

### **Serial console doesn't work**

Check if all configured bitrates for serial console are consistent, including the Serial-Over-LAN (BMC), OS setting, and Ironic's configuration. Also try enabling the console in Ironic, if it is not already:

```shell
openstack baremetal node console enable <node>
```

If this still isn't working, check what IPMI console port is set in the inventory service (Doni); this is NOT the port is listening for IPMI on the BMC, it is the port that will be used to host a socat pipe on the control node. It is usually a high port (>50000).

### **Horizon displays “No valid host was found” error**

This can happen for _many_ reasons. Check a few things:

* Are there errors in the `/var/log/ironic/ironic-conductor.log`?
* Is the node in maintenance mode? (It must be set to the "available" status for Nova to consider it.)
* Does the node have enough space on the file system? It must have more than the space defined in the `baremetal` Nova flavor (we set this to a low value on purpose; 20Gb).
