# Enable dev mode for a service:

In the `defaults.yml`, specify `kolla_dev_repos_git` as a git URL prefix, and for each service to enable dev mode in,
create options `NAME_dev_mode` and `NAME_source_version`. For example, to enable blazar dev mode:
```
kolla_dev_repos_git: https://github.com/chameleoncloud # git URL prefix
blazar_dev_mode: yes
blazar_source_version: chameleoncloud/train # git branch 
```
Then run `./cc-ansible --tags blazar reconfigure`. The source will be places in `/opt/stack/blazar`, and mounted into the container. After updating the source, you can restart the docker container for the service, and the changes will be reloaded.

# Fake hypervisors
In order to create blazar hosts, and use nova servers, you must have hypervisors. You can list hypervisors with
`openstack hypervisor list`.

To add fake hypervisors, in `defaults.yml`, remove the line `nova_compute_virt_type: kvm`, and add the following lines
```
enable_nova_fake: "yes"
num_nova_fake_per_node: 5 # Number of fake hypervisors to create
```
Then run `./cc-ansible --tags nova reconfigure`.

## Create a blazar host
Get the name of a hypervisor, and then run `openstack reservation host create <NAME>`

## Create a server on a fake hypervisor
First, you must have an image created. You can download the lightweight test image cirros from [here](http://download.cirros-cloud.net/)
and then run `openstack image create test-image --file cirros-0.5.2-x86_64-disk.img --disk-format qcow2`.

Check `openstack image list` to ensure the image was created.

Create a reservation for a host, as normal using blazar. Get the reservation ID.

Create the server:
`openstack --os-compute-api-version 2.37 server create --image test-image --flavor mini my_server --hint reservation=<RES_ID> --network none`

# Running tests
Openstack testing frameworks do not show the output from `LOG` statements. To see this output, modify the root logger:
```
from flask.logging import default_handler
from oslo_log import log as logging
root = logging.getLogger()
root.logger.addHandler(default_handler)
```