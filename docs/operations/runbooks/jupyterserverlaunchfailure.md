**Summary**: a user's Jupyter server failed to launch on the JupyterHub.

**Consequences**: the user will not be able to use Jupyter environment. This could also indicate wider issues that may be affecting more users.

### Possible causes

**Docker unable to map RBD volumes**: to avoid storing too much locally on the control node that hosts JupyterHub, we map all user working directories to Ceph RBD volumes.

See if it's possible to create a new Ceph volume.

```shell
volname=test-$(date +%Y-%m-%d%H:%M%S)
docker volume create --driver rbd:latest $volname
# Try writing to it
docker run --rm -v $volname:/vol centos:7 touch /vol/test.txt
```

If that works, then RBD mapping should be working OK. If that doesn't work, then something is wrong.

1. **Clear the Ceph OSD blacklist.** It can happen that the Ceph cluster blacklists the client trying to manage the RBD volumes within Docker. Log in to the Ceph monitor node and run `ceph osd blacklist clear`.
2. **Ensure the `rbd` kernel module is loaded.** This should happen automatically, but the Docker volume driver can't automatically load kernel modules. Run `modprobe rbd`, and consider adding a file called `/etc/modules-load.d/ceph.conf` with a single line containing `rbd`, which will ensure the kernel module is loaded on boot.