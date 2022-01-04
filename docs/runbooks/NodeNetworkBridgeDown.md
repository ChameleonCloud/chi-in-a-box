**Summary**: A Linux bridge is no longer reporting traffic.

**Consequences**: If the bridge is being used by processes to send/receive traffic, those processes are effectively cut off from the network. This ranges from fine to very bad, depending on the process/service.

### Possible causes

**A Docker network was deleted**: if a Docker network was deleted or recreated recently, this alert can fire, because Linux typically creates a bridge for each Docker network. The bridge name will include part of the Docker network ID if this is the case. Typically this is benign if this is the cause.

**Network is misconfigured**: it is likely that, if this is a major/primary network bridge, then all connectivity is down (though a [`NodeExporterDown`](./%5BRunbook%5D-NodeExporterDown) alert would be expected in that case, as the monitoring infrastructure likely wouldn't be able to get this information from the problem host at all!).

**OVS bridges were deleted**: this _can_ happen during an upgrade, but shouldn't persist for very long. It may be necessary to repair OVS state. Try running `./cc-ansible reconfigure --tags openvswitch` to fix.