---
description: An exciting menu of footguns
---

# Troublesome Hardware

The following hardware has known issues. Sometimes this is because the hardware or software is flaky, and sometimes it's because extensive use uncovers edge cases.

## Networking

### Dell OS10 Switches

#### Zero-touch-provisioning, and the case of the missing management IP

Dell switches running OS10 default to zero-touch-provisioning mode. Even if you don't send them a valid config, they will keep asking DHCP for one periodically. Mostly harmless, EXCEPT it will deactivate any static IP you have set on the management interface.

To check, run `show ztd-status`

\`\`

```
# The bad state
show ztd-status

-----------------------------------
ZTD Status     : enabled 
ZTD State      : cancelled
Protocol State : idle
Reason         : 
-----------------------------------

reload

# what you want to see after running reload
show ztd-status

-----------------------------------
ZTD Status     : disabled
ZTD State      : init
Protocol State : idle
Reason         : 
-----------------------------------
```

To disable it, after a factory install, you MUST run `reload`. Power cycling the switch will not exit ZTD boot mode.

#### Per-Vlan-Spanning tree, that sounded good, right?

Dell OS10 switches default to running a separate spanning-tree instance per vlan. This is great, until you have too many vlans, and everything falls over.

On the higher end switches, this threshold is 260 vlans.

You'll observe that, despite no useful logs, some ports are up but not passing traffic. Most ports will be fine, but newly configured ports or vlans will no longer add mac-addresses to the forwarding table.

You can check this by launching a known-good node, then running `show mac-address-table interface <node_port_interface>`

To check your current config, run `show spanning-tree`

As a workaround, set the switch to `RSTP` instead of `Rapid-PVST` mode.

```
# enter configure mode
configure
# set spanning tree to RSTP
spanning-tree mode rstp

# verify config
show running-config spanning-tree
!
spanning-tree mode rstp

# verify running status
show spanning-tree brief
Spanning tree enabled protocol rstp with force-version rstp
...
```

### Dell FX2 Chassis Switch

TODO

## GPUs

### nvidia-smi reports "no devices found" or "could not communicate with driver"

This is an idiosyncratic error which happens occasionally on GPU nodes. It can be fixed through software. It can usually be resolved by some combination of the following steps:

* If Ubuntu, run their driver installation utility and reboot
* Manually install the most recent nvidia drivers using the instance's package manager and reboot
* Install the `nvidia-dkms` module and reboot
* If Ubuntu, install the Ubuntu hardware enablement stack (`linux-generic-hwe-<version>`) and its recommended packages, and reboot
* Install the appropriate linux kernel headers and image and reboot
* Check the kernel module blacklist to see if the nvidia drivers got blacklisted somehow
* Check `dmesg` logs for "nvidia." See if there were any obvious errors that may indicate a hardware issue
