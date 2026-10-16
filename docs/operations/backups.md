# Taking backups

Take these backups before any risky change, such as an OpenStack release upgrade or an OS upgrade. The commands assume the control node is also the deploy host, and that you run them from your `chi-in-a-box` checkout. Set `REL` to the release you are running now:

```shell
REL=2024.1
```

## 1. Database

Run a full backup with kolla's mariabackup, then copy it out of the `mariadb_backup` docker volume. The scheduled backup timer rotates old files out of that volume after `mariadb_backup_file_age` days (29 by default).

```shell
./cc-ansible mariadb_backup
B=$(sudo ls -t /var/lib/docker/volumes/mariadb_backup/_data | grep '^mysqlbackup-' | head -1)
echo $B   # mysqlbackup-DD-MM-YYYY-<epoch>.qp.xbc.xbs.gz
sudo install -m 600 /var/lib/docker/volumes/mariadb_backup/_data/$B /root/kolla-db-$REL.qp.xbc.xbs.gz
```

Optional: confirm the backup is complete by listing its contents. The `mariadb` container does not mount the backup volume, so `docker exec mariadb ls /backup` fails. Use a throwaway container from the running image instead. It extracts the backup to its own temporary directory, so it needs free disk space of about the size of the database.

```shell
IMG=$(docker inspect mariadb --format '{{.Config.Image}}')
docker run --rm --network none -v mariadb_backup:/b:ro --entrypoint bash $IMG -c \
  'd=$(mktemp -d); zcat "/b/$1" | mbstream -x -C $d; find $d -mindepth 1 -maxdepth 1 -type d -printf "%f\n"' _ "$B"
```

The output should list each service's database (keystone, neutron, blazar, ...).

## 2. Kolla config (control node)

```shell
sudo tar -czf /root/kolla-etc-$REL.tgz -C / etc/kolla
```

## 3. chi-in-a-box and site-config (deploy host)

Commit your site-config changes in git first, so the backup matches a known commit. Then, from the directory that contains both checkouts:

```shell
git -C site-config status   # commit any pending changes
sudo tar -czf /root/ciab-$REL.tgz chi-in-a-box/ site-config/
```

!!! warning
    The tarball contains `site-config/vault_password` and the `passwords.yml` it decrypts, so treat it as a secret.

## 4. Lock down and copy off-host

```shell
sudo chown root:root /root/kolla-db-$REL.qp.xbc.xbs.gz /root/kolla-etc-$REL.tgz /root/ciab-$REL.tgz
sudo chmod 600 /root/kolla-db-$REL.qp.xbc.xbs.gz /root/kolla-etc-$REL.tgz /root/ciab-$REL.tgz
```

Copy all three files to another machine. A backup that only exists on the host you are upgrading doesn't help if you lose that host.

Not covered here: Glance image data. See [Glance Image Storage](../reference/glance-image-storage.md).

Before risky OS work, confirm that you have out-of-band console access (IPMI serial-over-LAN or the HTML5 console) and can log in as root there.

## Restore

* **Database:** copy `kolla-db-$REL.qp.xbc.xbs.gz` back into the `mariadb_backup` volume. Then follow "Restoring backups > Full" in the [kolla-ansible MariaDB backup and restore guide](https://docs.openstack.org/kolla-ansible/2025.1/admin/mariadb-backup-and-restore.html#restoring-backups).
* **Kolla config:** move the current `/etc/kolla` aside, then run `sudo tar -xzf /root/kolla-etc-$REL.tgz -C /`.
* **chi-in-a-box and site-config:** move the current directories aside, then run `sudo tar -xzf /root/ciab-$REL.tgz` from the directory that held them.
