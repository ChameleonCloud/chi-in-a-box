# defaults.yml

`inventory/defaults.yml` is the primary file you will use to configure your site.

Values set here will be set site-wide, and will override defaults set elsewhere. They will be overridden by values set in `host_vars` or `group_vars`.

The default configuration looks like the following:

```
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
```
