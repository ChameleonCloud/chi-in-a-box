# Upgrading to a new Release

## Train -> Xena

If you're running centos7, this will be annoying. This involves a major openstack version upgrade, python2->python3 upgrade, and host-os upgrade.

### Backup

On the controller node, back up the following.

* `/etc/ansible`
* `/etc/kolla`
* your mysql DB

#### mariadb

[https://docs.openstack.org/kolla-ansible/latest/admin/mariadb-backup-and-restore.html](https://docs.openstack.org/kolla-ansible/latest/admin/mariadb-backup-and-restore.html#full)

```
./cc-ansible mariadb_backup
docker run --rm -it \
  -v mariadb_backup:/mariadb_backup:ro \
  -v /tmp/backup:/backup \
  ubuntu:latest bash
  
# copy the latest backup from `/mariadb_backup to /backup`
```



On the Deploy node, back up the following:

* your git checkout of `chi-in-a-box`
* your `site-config` directory, especially including the `vault_password`

### Clean up the controller nodes

#### Ubuntu 20.04

```
# Run these on your controller node, after making a backup.
mv /etc/ansible /etc/ansible.bak
mv /etc/kolla /etc/kolla.bak
```

### Check out new chi-in-a-box

Once you've backed up your `chi-in-a-box` directory, run the following commands to get the latest code, and clean up leftover files.

```
# Run this in your chi-in-a-box directory, AFTER MAKING A BACKUP!
cd </path/to/chi-in-a-box>
git fetch
git checkout stable/xena
rm -rf venv
rm -rf .facts
./cc-ansible bootstrap-servers
```

#### Update passwords.yml

We need to set some new passwords that the new version requires. The `kolla-mergepwd` command will pull in values that are set in `site-config.example`, but missing from your passwords file.

```
# backup your passwords.yml file
cp $SITE_CONFIG/passwords.yml $SITE_CONFIG/passwords.yml.bak

$CHI_IN_A_BOX/venv/bin/ansible-vault decrypt \
  --vault-password-file $SITE_CONFIG/vault_password \
  $SITE_CONFIG/passwords.yml

# merge new passwords that are needed    
$CHI_IN_A_BOX/venv/bin/kolla-mergepwd \
  --old $SITE_CONFIG/passwords.yml \
  --new $CHI_IN_A_BOX/site-config.example/passwords.yml \
  --final $SITE_CONFIG/new_passwords.yml
 
# if the new file looks ok, run:
mv $SITE_CONFIG/new_passwords.yml $SITE_CONFIG/passwords.yml

$CHI_IN_A_BOX/venv/bin/ansible-vault encrypt \
  --vault-password-file $SITE_CONFIG/vault_password \
  $SITE_CONFIG/passwords.yml

# Finally, edit the resulting file to replace "null" with "".
# The empty values will be auto-populated.
cd $CHI_IN_A_BOX
./cc-ansible edit_passwords
```

#### Update inventory/hosts
