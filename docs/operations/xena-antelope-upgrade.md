# CHI-in-a-box Antelope/2023.1 Release

Welcome to the Antelope/2023.1 Release of CHI-in-a-Box! This release rolls up a lot of bug fixes, quality of life improvements, and some new features.

## New Features

* Support for python3.10 and Ubuntu 22.04 as a controller node host OS.
* cc-ansible now uses git submodules to pin the version of kolla-ansible. This helps ensure that the dependencies and ansible roles are at a known working version, and makes it easier to manage backwards compatibility during changes.
* Dev-in-a-box deployment allows both development and CI/CD workflows to execise the baremetal codepaths, network booting VMs instead of real nodes. In particular, this allows testing of networking-generic-switch with vlan-based networks, not just flat networks as in upstream's tenks.
* Tempest test framework can now be installed via chi-in-a-box, this will allow using tempest to run end-to-end acceptance tests on a site after deployment.


### Some things now unblocked and on the roadmap:

* networking-generic-switch: support for "port groups" to enable port bonding depending on switch operating system
* Neutron and networking-generic-switch: support for vlan trunk ports with baremetal nodes

### Selected features from Kolla-Ansible

#### [2023.2 backports](https://docs.openstack.org/releasenotes/kolla-ansible/2023.2.html#):
* (Replaced our fork) Add Lets Encrypt TLS certificate service integration into Openstack deployment. Enables trusted TLS certificate generation option for secure communcation with OpenStack HAProxy instances using letsencrypt_email, kolla_internal_fqdn and/or kolla_external_fqdn is required. One container runs an Apache ACME client webserver and one runs Lego for certificate retrieval and renewal. The Lego container starts a cron job which attempts to renew certificates every 12 hours.
* (Replaced our fork) Adds support for deploying the ironic-prometheus-exporter, ‘a Tool to expose hardware sensor data in the Prometheus format through an HTTP endpoint’. See https://opendev.org/openstack/ironic-prometheus-exporter for more details about the exporter.

#### [2023.1](https://docs.openstack.org/releasenotes/kolla-ansible/2023.1.html#)
* Add skyline ansible role
* Adds support for container state control through systemd in kolla_docker. Every container logs only to journald and has it’s own unit file in /etc/systemd/system named `kolla-<container name>-container.service`. Systemd control is implemented in new file `ansible/module_utils/kolla_systemd_worker.py`.
* If credentials are updated in passwords.yml kolla-ansible is now able to update these credentials in the keystone database and in the on disk config files. 
  The changes to passwords.yml are applied once kolla-ansible -i INVENTORY reconfigure has been run.

#### [Zed](https://docs.openstack.org/releasenotes/kolla-ansible/zed.html#)
* Enables configuring firewalld for external API services. Extracts the required services and checks the external port, then adds the ports to a firewalld zone. Assumes that firewalld has been installed and configured beforehand. The variable disable_firewall, is disabled by default to preserve backwards compatibility. But its good practice to have the system firewall configured.
* (Replaced our fork) Adds possibility for inlcuding custom alert notification templates with Prometheus Alertmanager.
* (Replaced our fork) Adds variables to configure whether monitoring services should be exposed externally: `enable_grafana_external`,`enable_kibana_external`,`enable_prometheus_alertmanager_external`
* Adds the prometheus_scrape_interval configuration option. The default is set to 60s. This configures the default scrape interval for all jobs.
* Adds support for managing resource providers via [config files](https://docs.openstack.org/nova/latest/admin/managing-resource-providers.html).
* Adds support for configuring a coordination backend for Ironic Inspector via the ironic_coordination_backend variable. Possible values are redis or etcd.
* Networking Generic Switch: support for `SONiC` switch operating system

#### [Yoga](https://docs.openstack.org/releasenotes/kolla-ansible/yoga.html#)
* Adds support for deploying OpenSearch and OpenSearch dashboards. These services directly replace ElasticSearch and Kibana which are now end-of-life. Support for sending logs to a remote ElasticSearch (or OpenSearch) cluster is maintained.
* Horizon themes can now be customized at deploy-time, rather than at build-time. 
* Healthchecks added to ironic-neutron-agent service
* Support for both PXE and iPXE enabled in Ironic at the same time.
* Upgrades of Ironic will now wait for nodes in wait states to change their state. This is to improve the user experience by avoiding breaking processes being waited on. This can be disabled by setting `ironic_upgrade_skip_wait_check` to `yes`.

## Upgrade Notes

### Host OS: 
* Interface name changes during release-upgrade: Dependng on the network card driver in use, the "stable interface name" may change unexpectly after the upgrade, potentially breaking remote acess to the controller node. To avoid this, ensure each interface in netplan has a `match` stanza, like the following:
    ```
    dataplane1:
      match:
        macaddress: 04:3f:72:ff:9b:33
        driver: mlx5_core
    set-name: dataplane1
    ```
    This will ensure that even if the “stable interface name” reported by udev changes, the interface will still be configured as expected. Both macaddress AND driver must be specified, as otherwise vlan interfaces may also match the macaddress.

### Nova:
* nova hypervisors with uuid!=hypervisor_hostname
* Nova-compute-ironic version on upgrade

### Ironic:

* Boot mode default changed from BIOS -> UEFI: To prevent breakage, please ensure all nodes have the `boot_mode` capability set prior to upgrading.

    Detection: list ironic nodes and exclude any that have the `boot_mode` capability set"
    ```
    baremetal node list --fields name properties -f value | grep -v "boot_mode"
    # P3-CPU-017 {'capabilities': 'cpu_arch': 'x86_64', 'vendor': 'dell inc'}
    ```
    fix: while still on the xena release, for each node identified above, execute:
    ```
    openstack baremetal node set --property capabilities="boot_mode:bios" $node_name_or_uuid
    ```

### Keystone:

* the `admin` keystone endpoint has been deprecated. Existing users of this endpoint should use the internal endpoint instead. To remove the now unused admin endpoints, run the following:
    ```
    openstack endpoint list --interface admin -f value | \
    awk '!/keystone/ {print $1}' | xargs openstack endpoint delete
    ```

* default user role changed from `_member_` to `member`. This was a transitional role during prior keystone database migrations, and has been deprecated for several openstack releases. It has now been fully removed, which will break any consumers that depend on it. To fix this, those consumers should use the `member` role instead.

### Networking-Generic-Switch:
* Dell OS10 switch port names": We are now targeting the upstream release of networking-generic-switch. For compatiblity, all nodes with an ironic port connected to a Dell OS10-based switch will need to change the switchport name from the format `1/2/3:4` to `ethernet 1/2/3:4`.

### RabbitMQ

* RabbitMQ migration to durable queues
* RabbitMQ feature flags on upgrade

### Letsencrypt/Haproxy

We have replaced our custom letsencrypt integration with the one [that was introduced upstream, including backports of features from 2023.2](https://github.com/ChameleonCloud/kolla-ansible/commit/fee63ec239eb42a80b196b5c5676120ac1ebd715).

All 3 of the following configuration lines in `defaults.yml` are necessary to enable the new feature.
```
kolla_enable_tls_external: true
enable_letsencrypt: true
letsencrypt_email: <email_for_letsencrypt>
```

If Chameleon's customized variant was enabled before the upgrade, you will need to manually shut down and remove their containers:
```
docker container stop letsencrypt_certbot
docker container stop letsencrypt_acme
docker container rm letsencrypt_certbot
docker container rm letsencrypt_acme
```
After deploying the new version, you will instead see containers named `letsencrypt_lego` and `letsencrypt_webserver`.


## Deprecation Notes

* `neutron_networks` configuration format
* usage of multiple different ssh keypairs for baremetal switches

## Bug Fixes

* LetsEncrypt: The new deployment mechansim for LetsEncrypt uses ssh to copy certs into the haproxy container, as well as to access the admin socket. This improves reliability of the certificate reload mechanism, and no longer requires the letsencrypt container to run on the same host as haproxy.
* Fluentd now parses logs from ironic-neutron-agent. These were missing from the match rules, preventing such logs from appearing in centralized logging.
* heat_encryption_key length is now properly set to 32 characters

# Detailed Upgrade Procedure

## Prior to beginning upgrade

1. Set boot_mode capability for all ironic nodes
   * in xena: if boot mode not set, then set it to BIOS
   * `baremetal node list --fields properties -f json | jq '.[] | .Properties.capabilities'`
   * for each node, `baremetal node set  --property capabilities="boot_mode:bios"`
1. Set cpu_arch capability for all ironic nodes (minor, avoids a warning)
1. Ensure all ironic ports for dell os10 switches have the switchport renamed from (1/2/3:4) to (ethernet 1/2/3:4), using `openstack baremetal port set --fields uuid node_uuid local_link_connection`
1. fix for any nova compute hosts with uuid!=hypervisor_hostname
   1. find hosts affected by the issue
      ```
      use nova;
      select hypervisor_hostname,uuid from compute_nodes WHERE hypervisor_type='ironic' AND isnull(deleted_at)  AND uuid!=hypervisor_hostname limit 100;
      ```
   1. for each host found with the issue, set reservation=disabled. the `hypervisor_hostname` is the ironic node uuid, and so it can be used for the lease.
   1. Once the host is not in an active reservation:
      1. delete it from blazar
      1. delete it from ironic
      1. run `openstack hardware sync` to have Doni re-create the node's entries, without the conflicts this time.
   






1. Ensure remote access to the management node:
    1. Ipmi serial console can be accessed
    1. Root password works
    1. Root login works EVEN IF NETWORK IS DOWN (I’m looking at you, PAM)
1. CEPH RGW: update configuration to reference:
    1. Keystone internal API endpoint, as admin endpoint will be deprecated
    1. Ceph service username and password, not keystone superadmin
1. Update known problematic node firmware:
    1. For skylake nodes with firmware: “Intel(R) Ethernet 10G 4P X710/I350 rNDC - 24:6E:96:7E:1F:BE	18.0.17”: Update firmware to version 22.xx
    1. Set boot mode from bios -> uefi

## During Upgrade

### Prepare:

1. Verify above pre-tasks
1. Make a backup of:
    1. Deploy host: chi-in-a-box and site-config directories
    1. Control node: move /etc/kolla directory out of the way
       ```
       mv /etc/kolla /etc/kolla.bak
       ```
1. Use ./cc-ansible mariadb_backup to create a full DB backup
1. Copy DB backup from mariadb_backup container to somewhere else

### Execute:

#### On target control node:
1. Get to the latest stable package versions and clean up old kernels:
    1. `apt-get update && apt-get dist-upgrade`
    1. Reboot, then `apt-get autoremove`
1. ensure netplan interfaces have a `match` stanza
1. `do-release-upgrade` to move from 20.04 -> 22.04
1. Reboot
1. Check on interface definitions and any apt sources that need updating
1. Delete kolla virtualenv from `/etc/ansible/venv`
1. shut down containers which have had their names changed:
    ```
    docker stop letsencrypt_certbot
    docker stop letsencrypt_acme
    docker stop ironic_pxe
    docker stop ironic_ipxe
    ```

#### On deploy host:
1. Delete chi-in-a-box venv from `chi-in-a-box/venv`
1. Delete any tools venv from site-config
1. Delete any venv from `/etc/ansible/venv`
1. Update chi-in-a-box via:
   ```
   git checkout stable/2023.1
   git pull
   git submodule update --init
   ```
1. Install new tools into venv via:
    1. `cc-ansible install_deps` # this doesn’t need a site-config
    1. Source the new venv:
       `source venv/bin/activate`
1. Update site-config/inventory/hosts by:
    1. mv inventory/hosts inventory/hosts.bak
    1. cp chi-in-a-box/site-config.example/inventory/hosts site-config/inventory/hosts
1. Manually apply any customizations to the new file (primarily where your controller and kvm compute nodes are listed in the first 5 entries)
1. Update site-config/passwords.yml by:
    1. Decrypt the file: ansible-vault … decrypt passwords.yml
    1. Mv passwords.yml passwords.yml.bak
1. Update pwds:
    1. Kolla-mergepwds –old site-config/passwords.yml.bak –new site-config.example/passwords.yml –final site-config/passwords.yml
    1. Kolla-genpwd site-config/passwords.yml
    1. Encrypt the file: Ansible-vault … encrypt passwords.yml
1. Apply migrations if necessary:
    1. If using ssh keys with NGS, only one key will be used going forward (instead of one per switch)
    1. Ensure neutron_ssh_key is added to all ngs managed switches, or set this keypair to an already added ones
    1. Regenerate heat_auth_password by setting it to the empty string. This works around an issue where it may be incorrectly set to != 32 characters in length
1. Cc-ansible bootstrap-servers
1. Cc-ansible prechecks
1. Cc-ansible pull
1. run `cc-ansible upgrade` (this will fail at nova, this is expected)
1. Manually edit nova compute service “version” in the db to 61, [the oldest allowed in the upgrade check](https://github.com/openstack/nova/commit/a1731927ccd17aeb634c4eed61dce16de16fa7b3#diff-c0b6a5928be3ac40200a2078b084341bb9187a12b1f959ad862e0038c9029193L233)
   ```
   USE nova;

   UPDATE services 
   SET version=61 
   WHERE services.deleted=0 
   AND services.topic="compute" 
   AND services.version < 61;
   ```
1. rerun `cc-ansible deploy --tags nova` to create service user
1. rerun `cc-ansible upgrade` this should now pass nova and continue.
1. Apply cleanups for keystone admin endpoints:
    1. Cc-ansible deploy –tags keystone
    ```
    openstack endpoint list --interface admin -f value | \
    awk '!/keystone/ {print $1}' | xargs openstack endpoint delete
    ```