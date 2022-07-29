# Upgrading to a new Release

## Train -> Xena

If you're running centos7, this will be annoying. This involves a major openstack version upgrade, python2->python3 upgrade, and host-os upgrade.

### Backup

On the controller node, back up the following.

* `/etc/ansible`
* `/etc/kolla`
* your mysql DB

On the Deploy node, back up the following:

* your git checkout of `chi-in-a-box`
* your `site-config` directory, especially including the `vault_password`

### Clean up the controller nodes

#### Ubuntu 20.04

```
# Run these on your controller node, after making a backup.
rm -rf /etc/ansible
rm -rf /etc/kolla
```

### Check out new chi-in-a-box

Once you've backed up your `chi-in-a-box` directory, run the following commands to get the latest code, and clean up leftover files.

```
# Run this in your chi-in-a-box directory, AFTER MAKING A BACKUP!
git checkout stable/xena
rm -rf venv
rm -rf .facts
./cc-ansible bootstrap-servers
./cc-ansible pull
./cc-ansible upgrade
```

###
