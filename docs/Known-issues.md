#### MariaDB cluster is running, but is not reachable via HAProxy

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


#### No internet (or disconnect) when executing the `openvswitch`/`neutron` role

During the course of provisioning the IP addresses on the interfaces will move to the OVS bridges created by Neutron; this causes remote connections to terminate. Try running the initial run in a `tmux` or `screen` session (or via an IPMI console.) If there are still issues:

- Ensure the physical interface is added as a port on `br-ex` using `ovs-vsctl show`. This should be performed during the application of the `openvswitch`. If not, to manually add, try doing `docker exec openvswitch_db ovs-vsctl add-port br-ex <public_interface>`
- Modify `/etc/sysconfig/network-script/ifcfg-<public_interface>` to make this persist on boot.

#### Serial console doesn't work

Check if those serial console bitrate match with each other: Serial-Over-LAN (BMC), OS setting, and Ironic's configuration.

#### Horizon displays “No valid host was found” error

This can happen for _many_ reasons. Check a few things:

- Are there errors in the `/var/log/ironic/ironic-conductor.log`?
- Is the node in maintenance mode? (It must be set to the "available" status for Nova to consider it.)
- Does the node have enough space on the file system? It must have more than the space defined in the `baremetal` Nova flavor (we set this to a low value on purpose; 20Gb).

#### Can't rename a Nova hypervisor or Zun compute node

If the hostname on a Nova or Zun compute node changes, it can be very difficult to figure out how to "flush out" the old hostname. The system will cache it in some unexpected places. The following procedures should wipe it out. Importantly, existing service containers **must** be stopped and removed in order to prompt a recreate; otherwise the container will still have the hostname it was originally created with, which will be stale.

##### Nova hypervisors

Ensure you have already set the hostname to its new value.

Run the following on the compute node:

```shell
for c in $(sudo docker container ls -a --filter name=nova --format "{{.Names}}"); do
  sudo docker stop $c && sudo docker rm $c
done
```

Run the following on the control node:

```shell
export OS_COMPUTE_API_VERSION=2.53
for uuid in $(openstack compute service list --service nova-compute -f value -c ID); do
  openstack compute service delete $uuid
  openstack resource provider delete $uuid
done
```

Finally, run the following on the deploy node:

```shell
./cc-ansible upgrade --tags nova
```

##### Zun compute node

Ensure you have already set the hostname to its new value.

Run the following on the compute node:

```shell
for c in $(sudo docker container ls -a --filter name=zun --format "{{.Names}}"); do
  sudo docker stop $c && sudo docker rm $c
done
```

Finally, run the following on the deploy node:

```shell
./cc-ansible upgrade --tags zun
```