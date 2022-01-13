CHI-in-a-Box comes with several automated periodic tasks called "hammers", which are intended to "whack" (technical term) precise parts of the system back in to place, typically to resolve issues of state disagreements between some of the distributed services. Hammers also are and can be used for policy enforcement, e.g., terminating leases that are made but then never utilized.

The [hammers](https://github.com/chameleoncloud/hammers) repository goes into more detail about what each of these hammers does, and why they exist.

## Listing all hammers

Hammers are by default installed onto the `control` node in the site configuration Ansible inventory. This is usually the node that runs the bulk of the services. You can list all the installed hammers by enumerating the systemd [timers](https://wiki.archlinux.org/index.php/Systemd/Timers).

```shell
systemctl list-timers 'hammer_*'
```
```
NEXT                         LEFT          LAST                         PASSED   UNIT                                        ACTIVATES
Thu 2020-10-08 20:02:09 CDT  47min left    Thu 2020-10-08 19:08:34 CDT  5min ago hammer_unutilized_leases.timer              hammer_unutilized_leases.service
Thu 2020-10-08 20:14:42 CDT  1h 0min left  n/a                          n/a      hammer_ironic_error_resetter.timer          hammer_ironic_error_resetter.service
Fri 2020-10-09 00:16:17 CDT  5h 2min left  n/a                          n/a      hammer_orphan_resource_providers.timer      hammer_orphan_resource_providers.service
Fri 2020-10-09 00:17:18 CDT  5h 3min left  n/a                          n/a      hammer_reservation_usage_notification.timer hammer_reservation_usage_notification.service
Fri 2020-10-09 00:37:31 CDT  5h 23min left n/a                          n/a      hammer_orphans_detector.timer               hammer_orphans_detector.service
Fri 2020-10-09 00:38:04 CDT  5h 23min left n/a                          n/a      hammer_clean_old_aggregates.timer           hammer_clean_old_aggregates.service
Fri 2020-10-09 01:03:47 CDT  5h 49min left n/a                          n/a      hammer_dirty_ports.timer                    hammer_dirty_ports.service
Fri 2020-10-09 01:44:43 CDT  6h left       n/a                          n/a      hammer_floating_ip_reaper.timer             hammer_floating_ip_reaper.service
Fri 2020-10-09 01:45:51 CDT  6h left       n/a                          n/a      hammer_conflict_macs.timer                  hammer_conflict_macs.service
Fri 2020-10-09 02:13:57 CDT  6h left       n/a                          n/a      hammer_undead_instances.timer               hammer_undead_instances.service
Fri 2020-10-09 02:39:30 CDT  7h left       n/a                          n/a      hammer_lease_stacking.timer                 hammer_lease_stacking.service
Fri 2020-10-09 02:57:16 CDT  7h left       n/a                          n/a      hammer_enforce_node_retirement.timer        hammer_enforce_node_retirement.service
```

## Inspecting hammer output

The hammers will generally output information about what they have done to stdout. This is captured by the systemd journal, so you can track down events that may be of interest.

```shell
# Inspect output for the "clean old aggregates" hammer
journalctl -u hammer_clean_old_aggregates
```