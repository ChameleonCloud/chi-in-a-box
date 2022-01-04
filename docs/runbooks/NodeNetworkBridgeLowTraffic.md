**Summary**: network traffic is unusually low on a particular bridge.

**Consequences**: This alert aims to detect issues with routing or OVS configuration for bridges; if traffic was detected in the past for this bridge, but not now (but it still exists!) then there may be an issue within OVS or somewhere else (like the NIC). Likely this affects tenant networking, but OpenStack APIs and other services may also be affected.

### Possible causes

**OVS misconfiguration**: if OVS or Neutron has recently been upgraded/reconfigured, there could be something that has changed. Examine logs on OVS: `docker logs openvswitch_db`, `docker logs openvswitch_vswitchd`. Rules _should_ be put in place by restarting most of the networking bits:

1. `docker restart openvswitch_db`
1. `docker restart openvswitch_vswitchd`
1. `docker restart neutron_openvswitch_agent`
1. A reconfiguration of OVS may also help: `./cc-ansible reconfigure --tags openvswitch`

**Hardware error**: it's possible the issue is with the NIC. Check `dmesg` for errors.