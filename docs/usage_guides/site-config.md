# The site configuration

Every CHI-in-a-Box deployment is highly configurable, though many settings are defaulted to what Chameleon considers the most useful or likely scenario. Some configuration values like hostnames or private IP addresses do not have defaults and must be specified by the operator. These settings are specified as part of a _site configuration_, which is a folder containing a few important files:

```text
site-config/
├─ certificates/        # used for manual TLS certs
├─ inventory/           # an ansible inventory
   ├─ group_vars/           # per-group overrides
   ├─ host_vars/            # per-host overrides
   ├─ hosts                 # defines ansible hosts and groups
├─ node_custom_config/  # used to manually override per-service config
├─ defaults.yml         # most config will be put here
├─ passwords.yml        # passwords for all deployed services
├─ vault-password       # password file used for ansible-vault
```

## defaults.yml

`inventory/defaults.yml` is the primary file you will use to configure your site.

Values set here will be set site-wide, and will override defaults set elsewhere. They will be overridden by values set in `host_vars` or `group_vars`.

The default configuration looks like the following:

```yaml
---
# This file contains an example site configuration.
# To enable features, each section MUST be customized to you needs.

# Associate Site Name (MANDATORY)
openstack_region_name: CHI@XYZ
# Site name, similar to region but used for out-of-band inventory management
chameleon_site_name: xyz

# HAProxy Config (MANDATORY)
enable_haproxy: yes
# Provide a full TLS chain in /etc/kolla/haproxy/certs.d/
kolla_enable_tls_external: yes
# Set to a "spare" address in the "internal" subnet
kolla_internal_vip_address: 10.0.0.1
# Set to a "spare" address in the "public" subnet
kolla_external_vip_address: 100.0.0.1
# This should resolve to the external_vip and match the TLS Cert
kolla_external_fqdn: chi.example.com

#Uncomment to Disable Federated Auth
# enable_keystone_federation: no
# enable_keystone_federation_openid: no
keystone_idp_client_id: null

# This is used for glance file backend
# ref: https://docs.openstack.org/kolla-ansible/train/reference/shared-services/glance-guide.html#file-backend
glance_file_datadir_volume: /var/lib/glance
```

## inventory

### Ansible Hosts File

`inventory/hosts` is an ini formatted file. It defines the hosts and groups that cc-ansible will operate on. The majority of this file can be left as-is, and should only be customized by advanced users.

```ini
# These initial groups are the only groups required to be modified. The
# additional groups are for more control of the environment.
[control]
<host>

[network]
<host>

[compute]
# No compute node; this is a baremetal-only cluster.

[monitoring]
<host>

[storage]
<host>

[deployment]
localhost ansible_connection=local

[baremetal:children]
control
network
compute
storage
monitoring
```

The hostname of your control node will be added to the groups `control`, `network`, `monitoring`, and `storage`.

### Host Vars

Files in the `inventory/host_vars` directory set variables scoped to a given host. You will likely only have one host here, so there should be a file named after the hostname of your control node.

By default, it will look like the following:

```yml
# Initial assumption is that this is also the deployment node,
# therefore any provisioning can be done locally.
ansible_connection: local

#network_interface: eth1
#kolla_external_vip_interface: eth2
```

* `network_interface`: the network interface name that will be used for all internal traffic, and where the haproxy internal vip will be bound.
* `kolla_external_vip_interface`: the network interface name to be used for the external API endpoint.

### Group Vars

This is not used by default, but allows you to set variables per group, rather than per host.

## passwords.yml

`passwords.yml` contains encrypted passwords for your site, with the encryption password stored in the file `vault_password`. Make sure not to add `vault_password` to source control!

Entries of the form `password_name:` will have passwords auto-generated on save.

View passwords with `cc-ansible view_passwords`, and edit them with `cc-ansible edit_passwords`

## post-deploy.yml (optional)

This file is optional, but allows for the configuration of extra, site-specific tasks to run during post-deploy.
