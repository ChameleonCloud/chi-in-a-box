**Summary**: There is likely not enough space on the Ironic conductor node to stage images for provisioning.

**Consequences**: When using "direct" deploy mode, Ironic conductor moves disk images to a temporary disk cache before transferring it to the target node via iSCSI. When there is not enough space in this directory, the conductor will raise an error to the user when they try to provision a node. Typically this happens for users with large disk images.

### Possible causes

Disk utilization issues usually require freeing up space somehow:

- **Resize LVM volumes**: it may be possible to simply allocate more space from a pool
- **Delete log files**: perhaps logrotate is misconfigured, or logs are simply being held for too long / are too big. Maybe a service is writing a lot of data to logs.
- **Clean Docker cache**: Docker's internal disk cache can get bloated after a while. Consider using `docker system prune` to clean out old/unused images and containers. Make sure you don't delete a stopped container that has data that you need!