# Production Baremetal

This is our "Default" configuration for associate sites. It supports federated user login, baremetal provisioning, and isolated, multi-tenant networking to the nodes.

{% hint style="info" %}
This configuration is baremetal only, and does not support virtualized instances!
{% endhint %}

### Site-Requirements Checklist

Before you begin, ensure you have the following, and note which will be used in your `defaults.yml` Refer to the host networking configuration for details.

{% content-ref url="hostnetworking.md" %}
[hostnetworking.md](hostnetworking.md)
{% endcontent-ref %}

* [ ] A name for your site
  * [ ] Friendly name, such as `CHI@SITE`: `openstack_region_name`
  * [ ] A short name, such as `site` : `chameleon_site_name`
* [ ] one or more [Control Nodes](broken-reference)
  * [ ] The control node has a linux bridge named `public`: `kolla_external_vip_interface`
    * [ ] bridged to a physical interface
    * [ ] bridged to one half of a veth-pair
    * [ ] With an IP address assigned from a publicly routable subnet
    * [ ] in this subnet, a reserved (not bound) Public IP for HAProxy VIP: `kolla_external_vip_address`
      * [ ] Public DNS name for this address: `kolla_external_fqdn`
      * [ ] TLS Certificate for this address and name
    * [ ] in this subnet, reserved (not bound), one public IP per baremetal node and/or isolated network, minimum 1, 20+ recommended
  * [ ] The control node has a linux bridge named `internal`: `network_interface`
    * [ ] bridged to a physical interface with a vlan trunk to the dataplane switch
    * [ ] bridged to one half of a veth-pair
    * [ ] With an IP address assigned from a private subnet, referred to as the `internal_subnet`
    * [ ] with a spare (not bound) ip address in `internal_subnet` for the HAProxy VIP: `kolla_internal_vip_address`
* [ ] **at least** one [Baremetal Node](broken-reference)
  * [ ] the out of band interface must be accessible by the controller node
* [ ] [a managed switch with vlan capability](../../before-you-begin/hardware-requirements/dataplane-switches.md)
  * [ ] Reserved VLANs: 2 minimum, 10+ recommended
    * [ ] Ironic Provisioning
    * [ ] Shared neutron network
    * [ ] 1 per isolated tenant network
  * [ ] the PXE capable interface on the Baremetal compute nodes must be connected to this switch
  * [ ] the controller node must have a tagged interface, and be a member of the above VLANs

Refer to the above, and we can now follow the QuickStart!

{% content-ref url="quickstart.md" %}
[quickstart.md](quickstart.md)
{% endcontent-ref %}
