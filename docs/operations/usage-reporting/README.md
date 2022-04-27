> **This feature can only be enabled by the [Chameleon associate sites](../../README.md).**

The usage reporting is used to monitor the daily bare metal node usage of an associate site.
The tool will read data from the backups of the OpenStack databases, process the data, and store the usage data into a database named `chameleon_usage` (co-located with the OpenStack databases).
The tool will also upload the usage data to a centralized location at TACC, so that the Chameleon Team can monitor the node usage from all Chameleon sites.
 
## MariaDB backup

The usage reporting reads data from the OpenStack database backups. Currently, two backup types are supported - [kolla-ansible MariaDB backup](https://docs.openstack.org/kolla-ansible/latest/admin/mariadb-backup-and-restore.html) and [mysqldump](https://mariadb.com/kb/en/mariadb-dumpmysqldump/).
If the MariaDB is deployed by kolla-ansible (default in CHI-in-a-Box), kolla-ansible MariaDB backup is enabled by default. The backups will be stored in a docker volume named `mariadb_backup`.
Please also check that `mariadb_backup_database_password` is set in the `passwords.yml`.
If you are using the [external MariaDB](https://docs.openstack.org/kolla-ansible/latest/reference/databases/external-mariadb-guide.html), your OpenStack database will be backed up using the `mysqldump` and the default backup location is `/var/db/backup`.
To set a different backup location, overwrite `backup_location` in the site `defaults.yml`.

The MariaDB backup configuration is included in the `post-deploy`. You can also manually configure the MariaDB backup by running the `backups` playbook.

```shell
cc-ansible reconfigure --tags mariadb # if mariadb is deployed by kolla-ansible
cc-ansible --playbook playbooks/backups.yml
```

For kolla-ansible MariaDB backup, you should see a `mariadb_backup_<basename of site_config_dir>` systemd [timer](https://wiki.archlinux.org/index.php/Systemd/Timers) on the `deployment` node.

```shell
systemctl list-timers 'mariadb_backup_*'
```

For both backup types, you should see a `mariadb_backup` systemd [timer](https://wiki.archlinux.org/index.php/Systemd/Timers) on the `control` node.

```shell
systemctl list-timers 'mariadb_backup'
```

By default, the backup rotation is 29 days, but you can turn this number by overwriting `mariadb_backup_file_age` in the site `defaults.yml`.

## Configuration

The MariaDB backup is required for the usage reporting. The usage reporting is by default installed onto the `control` node in the site configuration Ansible inventory.

The usage reporting is *disabled* by default. To enable, set `enable_usage_reporting: yes` in the site `defaults.yml`.
Two passwords are required in the `passwords.yml` - `chameleon_usage_mysql_password` and `chameleon_usage_site_password`.
The `chameleon_usage_site_password` is an authentication password from the Chameleon Team: once contact and resource registration are complete, you will get this password from the Chameleon Team.

The usage reporting configuration is included in the `post-deploy`. You can also manually configure by running the `chameleon_usage` playbook.

```shell
cc-ansible --playbook playbooks/chameleon_usage.yml
```

You can check the scheduled task via the systemd [timers](https://wiki.archlinux.org/index.php/Systemd/Timers).

```shell
systemctl list-timers 'usage_node'
```

## Troubleshooting

The usage reporting logs are captured by the systemd journal.

```shell
journalctl -u usage_node
```

## Grafana and KPI report
We currently have a Grafana dashboard and a weekly KPI report email set up for the node usage of all Chameleon sites. Please let us know if you are interested in getting access to the dashboard and email.
