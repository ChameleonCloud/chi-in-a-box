## Viewing Logs

Logs can be found in the directory `/var/log/kolla/`

You can also view the `stdout` of each container by running `docker logs -f container_name`

## Executing debugging commands

Each service is running in its own container, so the commands aren't available natively on the host.

Instead, you can run the commands using `docker exec`

For example, for openvswitch commands: `docker exec openvswitch_db ovs-vsctl show`