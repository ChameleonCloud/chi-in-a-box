# Neutron (networking)

### Fail to create new network (internal server error)

If you get an internal server error when creating a new network, it means that some aspect of provisioning the network (on switches in particular) has failed during the commit of the record to the database. This can be the result of a few problems, and you should examine the neutron-server logs to get more info. Putting Neutron into debug mode also can help diagnose.

#### Neutron is trying to re-allocate a particular VLAN segment

We have observed this problem, where Neutron tries to create another network on the same VLAN segment, which can be disallowed depending on how Neutron is trying to configure the switch/network. Normally only one network is tied to a single segment. You can check to see if this is a problem by inspecting the MariaDB `neutron` database:

```sql
use neutron;
select vlan_id,allocated,network_id from ml2_vlan_allocations left join networksegments on vlan_id=segmentation_id;
```

This should print something like the following:

```
+---------+-----------+--------------------------------------+
| vlan_id | allocated | network_id                           |
+---------+-----------+--------------------------------------+
|    3002 |         1 | 0185c55e-ce0e-4cc0-8dc1-d0e9812fcdb6 |
|    3009 |         1 | a37c3a1a-5753-4cc0-a7c0-877ed118249e |
|    3001 |         1 | 79f5d849-56ed-4e92-88a8-4450c4a774fe |
|    3000 |         1 | 9f4353a0-a96f-4b83-b913-3124689c8103 |
|    3294 |         1 | a72d1a9f-f9c8-4063-a6d7-0ec13160c4ba |
|    3003 |         0 | NULL                                 |
|    3004 |         0 | NULL                                 |
|    3005 |         0 | NULL                                 |
+---------+-----------+--------------------------------------+
```

You should look out for rows where allocated=0 and there is a network ID defined, or rows where allocated=1 and there is no network ID. In each case, the fix is to adjust the value of the allocated column:

```sql
--- for setting allocated=0, for example:
update ml2_vlan_allocations set allocated=0 where network_id=<id> limit 1;
```

#### Neutron is failing to SSH to the target switch

This should be apparent in the logs. Check that the switch IP/hostname, username, and password/identity file is properly configured. It can be helpful to check the value that is rendered to the final service configuration at /etc/kolla/neutron-server/ml2\_conf.ini on the node running the neutron-server service.
