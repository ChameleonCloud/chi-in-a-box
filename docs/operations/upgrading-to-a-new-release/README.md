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

#### Centos7 (unsupported)

This will be a bit annoying, as centos7 is not quite supported in xena.

Run the following, AFTER MAKING A BACKUP#

```
# Run these on your controller node, after making a backup.
rm -rf /etc/ansible
yum install -y libselinux-python3
```

Then update centos7 -> centos8

Then update centos8 -> centos-stream8

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
