# Ironic Flat Networking

{% hint style="danger" %}
This method carries security risks! Nodes all share the same L2 and L3 domain with the controller, so you must implement security methods outside the scope of Openstack.
{% endhint %}

To use a single network for API, provisioning, and tenant networking, you'll need the following configuration options in your defaults.yml

When configuring your network, make sure to set the network-type to 'flat'

```
  - name: physnet1
    bridge_name: br-physnet1
    external_interface: veth-internalb
    network_type: 'flat'
    sharednet:
      cidr: '172.40.0.0/24' # cidr of your netblock
      allocation_pools:
        - start: '172.40.0.129'
          end: '172.40.0.254'
          
```

You'll also need to override two defaults

```
ironic_provisioning_network: sharednet1
neutron_tenant_network_types: flat
```
