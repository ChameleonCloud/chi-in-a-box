---
⚠️ **Warning!** The *edge computing* flavor of CHI-in-a-Box is in alpha preview and is not part of the standard offering yet. ⚠️ 

---

# Deploying a testbed for edge computing

CHI-in-a-Box supports deploying a "flavor" of the Chameleon testbed optimized for edge computing experimentation. This type of testbed provides the following capabilities:

* Central management of lease and container lifecycle across enrolled edge devices
* Support for automatically attaching pre-configured peripherals to containers at create time, including, e.g. NVIDIA TX2 GPUs or Raspberry Pi Camera Modules or GPIO devices
* Secure encrypted communication to enrolled devices over NAT and WAN--devices do not have to be colocated with the control plane
* Various container-focused interfaces such as interactive console, remote log access, bind mounts and snapshots

![](https://i.imgur.com/kMcTVJL.png)

### Pre-deployment

> **Note**: Setup of encrypted Wireguard tunnels is a manual step currently. Future versions of CHI-in-a-Box will improve this.

The following guide uses `wireguard-tools` to simplify some steps of the tunnel setup and configuration, but this is not strictly required. To install this package:
 
```shell
apt-get install wireguard-tools
```

**Create the management tunnel.** This tunnel will carry management/system traffic between the control plane and the enrolled devices.

```shell
ip link add dev wg0 type wireguard
# Pick any subnet that you wish; 10.1.10.0/24 is just an example
ip addr add 10.1.10.1/24 dev wg1
wg set wg0 private-key $(wg genkey)
ip link set dev wg0 up
# Show the current status
wg show wg0
```

**Create the user tunnel.** This tunnel will carry user VxLAN traffic from the containers on the enrolled devices.

```shell
ip link add dev wg1 type wireguard
# Pick any subnet that you wish; just ensure it doesn't conflict with the other tunnel(s).
ip addr add 10.1.11.1./24 dev wg1
wg set wg1 private-key $(wg genkey)
ip link set dev wg1 up
# Show the current status
wg show wg1
```

## Site configuration

Here is a minimum viable configuration for an edge deployment:

### `defaults.yml`

```yaml
# Associate Site Name (MANDATORY)
openstack_region_name: Edge@YourInstitution
# Site name, similar to region but used for out-of-band inventory management
chameleon_site_name: edge_your_institution

# HAProxy Config (MANDATORY)
enable_haproxy: yes
# Provide a full TLS chain in /etc/kolla/haproxy/certs.d/
kolla_enable_tls_external: yes
# Set to a "spare" address in the "internal" subnet
kolla_internal_vip_address: x.x.x.1
# Set to a "spare" address in the "public" subnet
kolla_external_vip_address: y.y.y.1
# This should resolve to the external_vip and match the TLS Cert
kolla_external_fqdn: edge.your-institution.edu

# Neutron
neutron_type_drivers: flat,vxlan
neutron_tenant_network_types: vxlan

# Configure two physical networks; one for tenant segment traffic
# (via VxLAN segments) and one for traffic to the WAN/internet.
neutron_networks:
  - name: physnet1
    network_type: vxlan
    on_demand_vlan_ranges:
      - 200:250
    bridge_name: br-eno1
    external_interface: eno1
  - name: public
    bridge_name: br-ex
    external_interface: eno2
    # This should be your public IP block assigned to your deployment.
    cidr: x.x.x.x/24
    gateway_ip: x.x.x.1

# Edge services
# etcd provides coordination for the Docker daemon(s) exposed on the enrolled edge devices.
enable_etcd: yes
# kuryr provides last-mile networking from Neutron to the Docker containers
enable_kuryr: yes
# zun is the main container orchestration system
enable_zun: yes
# cyborg provides integration with pre-defined sets of peripherals, which can be discovered on the edge devices
# and then requested by users at container create time, to, e.g., access an attached camera within a container.
enable_cyborg: yes

# Disable Nova virtualization service (enabled by default)
enable_nova: no

# Disable Ironic baremetal service (enabled by default)
enable_ironic: no

# NOTE: Wireguard integration is in early preview! You can leave it enabled in preparation for the
# future, but currently Wireguard tunnels must be manually configured.
# Wireguard agent provides automatic management of the Wireguard tunnels that encrypt communications
# b/w the control plane and the enrolled devices. 
enable_neutron_wireguard: yes
```

### `host_vars/<control>`

The main control node should have interfaces set up in its host_vars file like this:

```yaml
# The default interface for most traffic
# (Should match the name of the interface on the "physnet1" physical network)
network_interface: br_eno1

# Public APIs will be served on this interface via haproxy
# (Should match the name of the interface on the "public" physical network)
kolla_external_vip_interface: br_ex

# User VxLAN traffic will be served on this interface
# (See notes on Wireguard in post-deployment; this should match the name of the "user" tunnel interface.)
tunnel_interface: wg1
```

## Device enrollment

> **Note**: currently devices must be enrolled by site operators via a not-very-streamlined process. The [Chameleon Edge SDK](https://github.com/chameleoncloud/python-chi-edge) is under active development and will be 100% responsible for device enrollment in the future, both ensuring that the devices have all required software installed and are securely connected to the central control plane.

If you've gotten this far, ask the Chameleon operators about the current state-of-the-art for device enrollment as it's rapidly evolving.