# Nova (KVM)

### **Can't rename a Nova hypervisor node**

If the hostname on a Nova compute node changes, it can be very difficult to figure out how to "flush out" the old hostname. The system will cache it in some unexpected places. The following procedures should wipe it out. Importantly, existing service containers **must** be stopped and removed in order to prompt a recreate; otherwise the container will still have the hostname it was originally created with, which will be stale.

{% hint style="warning" %}
Ensure you have already set the hostname to its new value.
{% endhint %}

Run the following on the compute node:

```shell
for c in $(sudo docker container ls -a --filter name=nova --format "{{.Names}}"); do
  sudo docker stop $c && sudo docker rm $c
done
```

Run the following on the control node:

```shell
export OS_COMPUTE_API_VERSION=2.53
for uuid in $(openstack compute service list --service nova-compute -f value -c ID); do
  openstack compute service delete $uuid
  openstack resource provider delete $uuid
done
```

Finally, run the following on the deploy node:

```shell
./cc-ansible upgrade --tags nova
```
