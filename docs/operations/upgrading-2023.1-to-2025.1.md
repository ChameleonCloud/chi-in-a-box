# Upgrading from 2023.1 to 2025.1

This guide upgrades a site from OpenStack 2023.1 on Ubuntu 22.04 to OpenStack 2025.1 on Ubuntu 24.04, in three stages: OpenStack 2023.1 to 2024.1, Ubuntu 22.04 to 24.04, then OpenStack 2024.1 to 2025.1. Do the pre-work first.

## Pre-Work

Ensure you have a consistent starting point on release 2023.1 and Ubuntu 22.04.

### Ensure the site is running the latest 2023.1 codebase

* Site-config: remove anything that pins the deployed version of OpenStack code, for example:
    * `openstack_release`
    * `openstack_tag`
    * `horizon_tag`, `blazar_tag`, `ironic_tag`
    * `horizon_image`
    * `horizon_image_full`
    * any `<service>_dev_mode`, e.g. `blazar_dev_mode`, `ironic_dev_mode`, `zun_dev_mode`, along with its `<service>_git_repository` and `<service>_source_version`. Dev mode bind-mounts `/opt/stack/<service>` over the installed package, so a missing or stale checkout there breaks the service.
* Site-config: clean duplicates from `node_custom_config`. Files in your site-config's custom config replace the ones in chi-in-a-box, so remove anything that duplicates a chi-in-a-box file with minor modifications. For example:
    * Not OK: `ironic.conf`, `nova.conf`, …
    * OK: non-overlapping files such as fluentd or haproxy drop-ins, ceph keyrings, …
* Ensure chi-in-a-box is clean and up to date:

```shell
cd chi-in-a-box
git checkout stable/2023.1
git fetch
git reset --hard origin/stable/2023.1
git submodule update --init
rm -rf venv/
./cc-ansible install_deps
```

* Ensure containers are clean and up to date:

```shell
./cc-ansible pull
./cc-ansible genconfig
./cc-ansible deploy
```

* Run `docker ps` and check that all containers are running tag `2023.1-ubuntu-jammy`.

### Switch to RabbitMQ quorum queues

OpenStack 2024.1 changes the default queue type to durable quorum queues, which requires a migration. See the [kolla-ansible docs](https://docs.openstack.org/kolla-ansible/2023.1/reference/message-queues/rabbitmq.html#high-availability).

Migrating requires stopping all services that talk to RabbitMQ, updating their config, clearing the old queues out of RabbitMQ, and then starting the services back up. If the services are active, they'll recreate the queues with the old settings and prevent the migration.

1. Identify all services that may talk to RabbitMQ. On the control node, as root, `cd /etc/kolla`, then:
    1. List them: `grep -Rl oslo_messaging_rabbit | cut -d "/" -f 1 | sort -u`
    2. Turn the list into kolla tags: `grep -Rl oslo_messaging_rabbit | cut -d "/" -f 1 | cut -d "-" -f 1 | sort -u | paste -s -d ","`

    For example, a CHI@Edge site gives `blazar,keystone,neutron,zun`. Keystone is in the list, so the APIs are down from step 2 until step 8.
2. Stop all services that talk to RabbitMQ. (Very important!)

    ```shell
    ./cc-ansible stop --yes-i-really-really-mean-it --tags <kolla tags from 1.2>
    ```
3. Verify the containers are stopped in `docker ps --all`.
    1. If any are not stopped, use `systemctl stop <kolla-service-unit-name>` to stop them:

        ```shell
        systemctl | egrep '^\s*kolla-' | tr -s ' ' | cut -d ' ' -f 2 | xargs systemctl stop
        ```
4. Set `om_enable_rabbitmq_quorum_queues: true` in `site-config/defaults.yml`.
5. `./cc-ansible genconfig`
6. `./cc-ansible reconfigure --tags rabbitmq`
7. `./cc-ansible rabbitmq-reset-state`
8. `./cc-ansible deploy --tags <kolla tags from 1.2>`
9. Verify that services start without errors about RabbitMQ in their logs, and that RabbitMQ does not log errors about durable queues. Check the queue types:

    ```shell
    docker exec rabbitmq rabbitmqctl list_queues -q type durable | sort | uniq -c
    ```

    Most queues should now be `quorum true`. `*_fanout_*` and `reply_*` queues stay `classic false` on 2023.1 and 2024.1, which is expected; they are migrated in the 2025.1 stage.

### Upgrade RabbitMQ versions

See the [kolla-ansible docs on SLURP upgrades](https://docs.openstack.org/kolla-ansible/2024.1/reference/message-queues/rabbitmq.html#slurp).

1. In `defaults.yml`, set:

    ```yaml
    rabbitmq_image: ghcr.io/chameleoncloud/kolla/rabbitmq-3-12
    ```
2. Run `./cc-ansible upgrade --tags rabbitmq`
3. In `defaults.yml`, set:

    ```yaml
    rabbitmq_image: ghcr.io/chameleoncloud/kolla/rabbitmq-3-13
    ```
4. Run `./cc-ansible upgrade --tags rabbitmq`

After each upgrade, verify the version with `docker exec rabbitmq rabbitmqctl version`, and check that services reconnect. Each restart causes a brief burst of `AMQP server ... is unreachable` errors in service logs, which should stop within a minute.

Remove the `rabbitmq_image` override before upgrading to 2024.1. The `rabbitmq-3-13` image is only published for 2023.1, so the 2024.1 `pull` would fail. The default 2024.1 `rabbitmq` image is already 3.13. (This differs from the 2025.1 stage below, where the override must stay set.)

### Prepare for the Ubuntu upgrade

#### Ensure netplan pins MAC addresses

The 22.04 to 24.04 upgrade may rename network interfaces. Ensure each interface has a `match: macaddress` stanza.

#### Ensure Mellanox OFED is not installed

The Mellanox apt repo may break `do-release-upgrade`. Ensure OFED is uninstalled before proceeding.

#### Set the ceph apt repo to debian-tentacle

Tentacle is the first release supporting both jammy and noble in its apt repos.

#### Ensure the system is fully updated

```shell
apt-get update
apt-get dist-upgrade
apt-get autoremove
```

Reboot to ensure the latest kernel is running.

#### Ensure out-of-band access

Ensure you can connect to serial-over-LAN and/or the HTML5 console, and that you can log in via the root shell! Both will be needed to recover if you break networking.

### Backup!

1. Make a copy of `/etc/kolla` from the controller node:

    ```shell
    tar -czvf /root/kolla-etc-2023-1.tgz /etc/kolla
    ```
2. Take a DB backup, then copy it out of the docker volume:

    ```shell
    ./cc-ansible mariadb_backup
    cp /var/lib/docker/volumes/mariadb_backup/_data/<todays_backup> \
      /root/kolla-db-2023-1
    ```
3. Make a copy of chi-in-a-box and site-config. This includes `vault_password` and `passwords.yml`, so restrict access to it:

    ```shell
    tar -czvf ciab-2023-1.tgz chi-in-a-box/ site-config/
    chmod 600 ciab-2023-1.tgz
    ```

## OpenStack 2023.1 -> 2024.1

### Update chi-in-a-box

```shell
git fetch
git checkout chameleoncloud/2024.1
git pull --ff-only
rm -rf venv
git submodule update --init --recursive
./cc-ansible install_deps
```

### Update site-config

The new chi-in-a-box contains an updated inventory and passwords template under `site-config.example`.

#### Update inventory

For convenience, the monolithic inventory file has been split into:

* [10-base-hosts](https://github.com/ChameleonCloud/chi-in-a-box/blob/chameleoncloud/2024.1/site-config.example/inventory/10-base-hosts)
* [50-kolla-hosts](https://github.com/ChameleonCloud/chi-in-a-box/blob/chameleoncloud/2024.1/site-config.example/inventory/50-kolla-hosts)
* [80-chi-hosts](https://github.com/ChameleonCloud/chi-in-a-box/blob/chameleoncloud/2024.1/site-config.example/inventory/80-chi-hosts)

Ansible merges these in alphabetical order, with later files overriding earlier ones in case of conflicts. Controller nodes are customized in `10-base-hosts`; `50-kolla-hosts` and `80-chi-hosts` can likely be left unmodified.

1. Diff your current `site-config/inventory/hosts` against the [2023.1 chi-in-a-box inventory](https://raw.githubusercontent.com/ChameleonCloud/chi-in-a-box/refs/heads/stable/2023.1/site-config.example/inventory/hosts), and check whether anything is surprising.
2. Copy the new inventory files:

    ```shell
    cp chi-in-a-box/site-config.example/inventory/10-base-hosts \
      $SITE_CONFIG/inventory/
    cp chi-in-a-box/site-config.example/inventory/50-kolla-hosts \
      $SITE_CONFIG/inventory/
    cp chi-in-a-box/site-config.example/inventory/80-chi-hosts \
      $SITE_CONFIG/inventory/
    ```
3. Most likely, customize `10-base-hosts` with your changes. If necessary, apply customizations to `50-kolla-hosts` or `80-chi-hosts` as well. Don't carry over groups for retired services, such as `[jupyterhub:children]`.
4. Move the old `inventory/hosts` out of the inventory directory. Ansible reads every file there, so leaving it in place merges it with the new files:

    ```shell
    mv $SITE_CONFIG/inventory/hosts $SITE_CONFIG/inventory-hosts-2023.1.bak
    ```

#### Update passwords

chi-in-a-box has a `cc-ansible update_passwords` command. Under the hood, it will:

* decrypt your passwords file;
* find any entries present in `site-config.example/passwords.yml` and missing from yours, and add them to your passwords file;
* populate passwords for empty entries;
* re-encrypt the file.

Run:

```shell
./cc-ansible update_passwords
```

### Perform the upgrade

1. Verify the above steps: `./cc-ansible prechecks`
2. Re-bootstrap with newer dependencies: `./cc-ansible bootstrap-servers`
3. Ensure all containers can be pulled: `./cc-ansible pull`
4. Ensure all config can be generated: `./cc-ansible genconfig`
5. Upgrade: `./cc-ansible upgrade`

### Verification

All containers are tagged `2024.1-ubuntu-jammy`, except containers that 2024.1 no longer manages, which keep running their 2023.1 image:

* `prometheus_ipmi_exporter`: once you've confirmed you don't need it, remove it on each host that runs it. Its kolla systemd unit restarts the container, so stop the unit rather than the container, then remove the unit file, the container, and its config:

    ```shell
    systemctl disable --now kolla-prometheus_ipmi_exporter-container.service
    rm /etc/systemd/system/kolla-prometheus_ipmi_exporter-container.service
    systemctl daemon-reload
    docker rm prometheus_ipmi_exporter
    rm -rf /etc/kolla/prometheus-ipmi-exporter
    ```

## Ubuntu 22.04 -> 24.04

### Upgrade the operating system

1. `do-release-upgrade`
2. Reboot once it has completed.

### Upgrade Kolla containers

1. In `defaults.yml`, set:

    ```yaml
    kolla_base_distro_version: noble
    distro_python_version: "3.12"
    ```
2. On control nodes and hypervisors, recreate the venv with Python 3.12:

    ```shell
    rm -rf /etc/ansible/venv
    python3 -m venv /etc/ansible/venv
    ```
3. Download the updated Docker and populate the venv:

    ```shell
    ./cc-ansible bootstrap-servers
    ```
4. Pull the 24.04 containers:

    ```shell
    ./cc-ansible pull
    ```
5. Deploy the 24.04 containers:

    ```shell
    ./cc-ansible deploy
    ```

### Verification

Check that all running containers are tagged `2024.1-ubuntu-noble`.

## OpenStack 2024.1 -> 2025.1

### Backup!

1. Make a copy of `/etc/kolla` from the controller node:

    ```shell
    tar -czvf /root/kolla-etc-2024-1.tgz /etc/kolla
    ```
2. Make a copy of the most recent DB backup:

    ```shell
    cp /var/lib/docker/volumes/mariadb_backup/_data/<todays_backup> \
      /root/kolla-db-2024-1
    ```
3. Make a copy of chi-in-a-box and site-config:

    ```shell
    tar -czvf ciab-2024-1.tgz chi-in-a-box/ site-config/
    ```

### RabbitMQ: more queue migration

See the [kolla-ansible docs](https://docs.openstack.org/kolla-ansible/2025.1/reference/message-queues/rabbitmq.html#high-availability).

In the Epoxy release of Kolla, the version of RabbitMQ is updated to 4.0. As a result, all queues must be migrated to a durable type before upgrading to Epoxy. Do this by setting the following options in `defaults.yml`, then following the migration procedure below.

```yaml
om_enable_queue_manager: true
om_enable_rabbitmq_quorum_queues: true
om_enable_rabbitmq_transient_quorum_queue: true
om_enable_rabbitmq_stream_fanout: true
```

1. `./cc-ansible genconfig`
2. Stop all services that talk to RabbitMQ. (Very important!)

    ```shell
    ./cc-ansible stop --yes-i-really-really-mean-it --tags blazar,glance,heat,ironic,keystone,neutron,nova
    ```
3. Update RabbitMQ settings:

    ```shell
    ./cc-ansible reconfigure --tags rabbitmq
    ```
4. Clear the old queues:

    ```shell
    ./cc-ansible rabbitmq-reset-state
    ```
5. Start the services back up with the new queue config:

    ```shell
    ./cc-ansible deploy --tags blazar,glance,heat,ironic,keystone,neutron,nova
    ```

Verification:

1. Run `./cc-ansible prechecks`. It will warn if old queues persist for a service. If so, repeat these steps:
    1. `./cc-ansible stop --yes-i-really-really-mean-it --tags <service>`, and wait for the containers to exit
    2. `./cc-ansible rabbitmq-reset-state`
    3. `./cc-ansible deploy --tags <service>`
    4. `./cc-ansible prechecks`

### RabbitMQ: upgrade 3.x to 4.x

See the [kolla-ansible docs](https://docs.openstack.org/kolla-ansible/2025.1/reference/message-queues/rabbitmq.html#rabbitmq-versions).

1. In `defaults.yml`, set:

    ```yaml
    rabbitmq_image: ghcr.io/chameleoncloud/kolla/rabbitmq-4-1
    ```
2. Run `./cc-ansible upgrade --tags rabbitmq`

Leave `rabbitmq_image` set for the 2025.1 upgrade below: the kolla-ansible docs say it must stay overridden, or the upgrade downgrades RabbitMQ to 4.0.

### Update chi-in-a-box

```shell
git checkout chameleoncloud/2025.1
rm -rf venv
git submodule update --init --recursive
./cc-ansible install_deps
```

### Update site-config

The new chi-in-a-box contains an updated inventory and passwords template under `site-config.example`.

#### Update inventory

The inventory is split into:

* [10-base-hosts](https://github.com/ChameleonCloud/chi-in-a-box/blob/chameleoncloud/2025.1/site-config.example/inventory/10-base-hosts)
* [50-kolla-hosts](https://github.com/ChameleonCloud/chi-in-a-box/blob/chameleoncloud/2025.1/site-config.example/inventory/50-kolla-hosts)
* [80-chi-hosts](https://github.com/ChameleonCloud/chi-in-a-box/blob/chameleoncloud/2025.1/site-config.example/inventory/80-chi-hosts)

Ansible merges these in alphabetical order, with later files overriding earlier ones in case of conflicts. Controller nodes are customized in `10-base-hosts`; `50-kolla-hosts` and `80-chi-hosts` can likely be left unmodified.

1. Diff your current `site-config/inventory/{10-base,50-kolla,80-chi}-hosts` against the [2024.1 chi-in-a-box inventory in site-config.example](https://github.com/ChameleonCloud/chi-in-a-box/tree/chameleoncloud/2024.1/site-config.example/inventory). It is likely that only `10-base-hosts` differs.
2. After making a backup, copy the new inventory files:

    ```shell
    cp chi-in-a-box/site-config.example/inventory/50-kolla-hosts \
      $SITE_CONFIG/inventory/
    cp chi-in-a-box/site-config.example/inventory/80-chi-hosts \
      $SITE_CONFIG/inventory/
    ```

#### Update passwords

As for 2024.1, run:

```shell
./cc-ansible update_passwords
```

This adds any entries present in `site-config.example/passwords.yml` and missing from your passwords file, and populates passwords for empty entries.

### Perform the upgrade

1. Verify the above steps: `./cc-ansible prechecks`
2. Re-bootstrap with newer dependencies: `./cc-ansible bootstrap-servers`
3. Ensure all containers can be pulled: `./cc-ansible pull`
4. Ensure all config can be generated: `./cc-ansible genconfig`
5. Upgrade: `./cc-ansible upgrade`

### Verification

All containers are tagged `2025.1-ubuntu-noble`.
