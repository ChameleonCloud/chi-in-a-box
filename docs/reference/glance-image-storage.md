# Glance Image Storage



All images used to launch instances are stored by Glance. However, glance holds the metadata, and delegates the actual data storage to one or more backends. Configuration and best practices are summarized below.

The kolla-ansible docs with details are listed here: [https://docs.openstack.org/kolla-ansible/xena/reference/shared-services/glance-guide.html](https://docs.openstack.org/kolla-ansible/xena/reference/shared-services/glance-guide.html)

{% hint style="warning" %}
Images saved using cc-snapshot are also stored in Glance. This means that it contains user-data, and should be treated with care.
{% endhint %}

### File Backend

If not configured, Glance defaults to storing image data on the controller node, in the path `/var/lib/glance/images`.&#x20;

{% hint style="danger" %}
Make sure you back up this directory!
{% endhint %}

Customize this path by setting:

```
glance_backend_file: "yes"
glance_file_datadir_volume: "/path/to/shared/storage/"
```

#### Notes for network filesystems

Even if using a network filesystem as the `glance_file_datadir_volume`, ensure that it has backups, or at least snapshots to allow recovery from file deletion.

If the mount "flaps", that is goes down and back up due to a network disruption, the following procedure must be taken to mount it inside the container.

1. Stop the glance container `docker stop glance_api`
2. unmount the network share `umount /path/to/shared/storage`
3. remount the network share `mount /path/to/shared/storage`
4. start the glance container `docker start glance_api`
