# Train -> Xena

Update `passwords.yml`update `inventory/hosts`update controller node OSremove `/etc/kolla` and `/etc/ansible` from controller nodecheck out new chi-in-a-box branchremove `venv`run `cc-ansible` bootstrap-serversrun `cc-ansible pull`run `cc-ansible upgrade`script to fix nova-compute version in DBdownload new ironic pxe imagesupdate nodes to use new ironic pxe imagesreset boot, deploy interfaces on ironic nodes



## Make Backups!

Before upgrading, you MUST make a backup of the following items. This will allow roll-back/recovery in the case that something goes wrong.

### Directories

* Controller Node
  * `/etc/kolla`
* Deploy Host
  * `/<path>/<to>/chi-in-a-box`
  * `/<path>/<to>/site-config`

### Glance Images

If your glance images are stored on a directory in the local filesystem (this is `/var/lib/glance/` by default), make sure you have a backup / snapshot / copy / etc. If it is a mounted network share, e.g. nfs, cephfs, etc., unmount it for extra safety.

### MySQL Database

If you have `mariabackup` enabled (default for all recent deployments), follow the instructions here for making a backup.



## Prepare the Host(s)

Due to the python2 -> 3 upgrade, you'll need to remove the following directories.

### Deploy Host (Or controller if all-in-one)

First, we need to ensure the chi-in-a-box directory is in a clean state

```
# Clean up chi-in-a-box venv and branch
cd /<path>/<to>/chi-in-a-box
rm -rf venv
git checkout stable/xena
```

*

