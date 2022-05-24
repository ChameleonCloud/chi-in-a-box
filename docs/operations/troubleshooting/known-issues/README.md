# Known issues

### **Bootstrapping MariaDB fails**

**MariaDB cluster is running, but is not reachable via HAProxy**

This can happen if the `haproxy` user is somehow not configured for MariaDB. In particular, if the `database_password` is changed at some point during bootstrapping, this can get in to a bad state.

**If just the `haproxy` user appears to be missing**: try re-running `./cc-ansible deploy --tags mariadb` and see if that helps.

**If database update operations are failing**: try resetting the root password.

1. You can allow a local login by editing `/etc/kolla/mariadb/my.cnf` and adding `skip-grant-tables` and `skip-network` (the latter disallows network access, for security).
2. Login via `docker exec -it -uroot mariadb mysql`
3. Update all of the `root` user passwords to your new password. Follow [MariaDB docs](https://mariadb.com/kb/en/set-password/) for how to do this.

**If other database operations (like creating DB users for other OpenStack services) work**: try manually creating the `haproxy` MariaDB user.

1. Login via `docker exyec -it -uroot mariadb mysql -p` and provide the (unencrypted) root password (`database_password` in your passwords.yml).
2. Create a `'haproxy'@'%'` user with an empty password. This is what the automation is supposed to do. Then perform a `GRANT USAGE ON *.* to 'haproxy'@'%'; FLUSH PRIVILEGES;`
3. Log out of the MariaDB container. You can now try to redeploy HAProxy.

### **No internet (or disconnect) when executing the `openvswitch`/`neutron` role**

During the course of provisioning the IP addresses on the interfaces will move to the OVS bridges created by Neutron; this causes remote connections to terminate. Try running the initial run in a `tmux` or `screen` session (or via an IPMI console.) If there are still issues:

* Ensure the physical interface is added as a port on `br-ex` using `ovs-vsctl show`. This should be performed during the application of the `openvswitch`. If not, to manually add, try doing `docker exec openvswitch_db ovs-vsctl add-port br-ex <public_interface>`
* Modify `/etc/sysconfig/network-script/ifcfg-<public_interface>` to make this persist on boot.
