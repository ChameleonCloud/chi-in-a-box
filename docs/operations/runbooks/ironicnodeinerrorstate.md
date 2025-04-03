**Summary**: an Ironic node has entered the `error` [provision state](https://docs.openstack.org/ironic/latest/contributor/states.html). Per the docs:

> This is the state a node will move into when deleting an active deployment fails.

**Consequences**: users will not be able to launch instances on these Ironic nodes. However, they will still be able to reserve the nodes, which can lead to confusion when trying to utilize the reservation.

### Possible causes

**Temporary IPMI connectivity disruption**: In some cases, the power status of the node cannot be synced during a deployment or undeployment, and the node can enter an error state as a precaution. There is a [hammer](https://github.com/ChameleonCloud/hammers/blob/master/hammers/scripts/ironic_error_resetter.py) that should attempt to "reset" this state, as it can and does happen periodically simply due to network contention or interruption on the provisioning network.

1. Check the "extra" field on the node: `openstack baremetal node show $node -f json | jq .extra`. A node that has been reset by the hammer will have a "hammer_error_resets" key with timestamps for each time a reset was performed.
1. If there are more than [`max_attempts`](https://github.com/ChameleonCloud/hammers/blob/master/hammers/scripts/ironic_error_resetter.py#L146) (3 at time of writing), then this node could have an issue with its IPMI interface and should be put into maintenance.

**Temporary API connectivity disruption**: Many OpenStack services are involved in instance tear-down (e.g., Keystone, Nova, Ironic, Neutron)--if any of those cannot be reached, the instance can fail to tear down.

**IPMI interface failure**: If the node has a pattern of issues with IPMI, there could be an issue with the BMC, the IPMI NIC, or even the physical cable or connection on the switch that provides IPMI connectivity. All of these issues require maintenance of the node.

### Clearing the error state

To put the node back into the `available` state, you can trigger an `undeploy` of the node. This works even if the node doesn't have an instance; it essentially performs a `clean` and then `delete` if there is an instance, then resets the state.

```shell
openstack baremetal node undeploy $node
```