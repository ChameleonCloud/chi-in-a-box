Nova can fail to launch instances inside a reservation that clearly still has free nodes. It fails with the error “No valid host found”. 

This can be caused by multiple reasons:

1. get the list of baremetal nodes in the lease.
   ```
   chameleon lease resource list <lease_id>
   ```
1. If a subset of these nodes are failing, then check the specific node:
   ```
   openstack baremetal node show <uuid>
   ```
1. Check if its in maintenance mode
   1. If yes, check the reason
1. Check to see if it still has an associated instance ID. If so, run:
   ```
   openstack baremetal node undeploy <uuid>
   ```

If these don't show an issue, its time to look at the logs. They can seen in `/var/log/kolla` on your admin node,
or via kibana at `<site_url>:5601`
The credentials can be found in your site's ansible-vault

If you see a conflict, reference https://github.com/ChameleonCloud/chi-in-a-box/wiki/%5BRunbook%5D-provider-conflict


There are also some commands to check the health of all nodes at a site:

List all baremetal nodes in maintenance: 
```
openstack baremetal node list --maintenance
```

Ironic thinks nodes are active, but doesn’t know about a specific instance
```
openstack baremetal node list --provision-state active --unassociated
```


