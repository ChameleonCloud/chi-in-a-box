# Developing OpenStack Services

## Enable dev mode for a service:

In the `defaults.yml`, specify `kolla_dev_repos_git` as a git URL prefix, and for each service to enable dev mode in, create options `NAME_dev_mode` and `NAME_source_version`. For example, to enable blazar dev mode:

```
kolla_dev_repos_git: https://github.com/chameleoncloud # git URL prefix
blazar_dev_mode: yes
blazar_source_version: chameleoncloud/train # git branch 
```

Then run `./cc-ansible --tags blazar reconfigure`. The source will be places in `/opt/stack/blazar`, and mounted into the container. After updating the source, you can restart the docker container for the service, and the changes will be reloaded.

```
// example for neutron + neutron plugin
kolla_dev_repos_git: https://github.com/chameleoncloud
neutron_dev_mode: yes
neutron_source_version: chameleoncloud/train

neutron_dev_plugins:
  - name: networking-generic-switch
    git_repository: https://github.com/ChameleonCloud/networking-generic-switch
    source_version: "feature/dell_os10"
    packages:
      - networking_generic_switch
```



## Fake hypervisors

In order to create blazar hosts, and use nova servers, you must have hypervisors. You can list hypervisors with `openstack hypervisor list`.

To add fake hypervisors, in `defaults.yml`, remove the line `nova_compute_virt_type: kvm`, and add the following lines

```
enable_nova_fake: "yes"
num_nova_fake_per_node: 5 # Number of fake hypervisors to create
```

Then run `./cc-ansible --tags nova reconfigure`.

You might also have to run `cp /opt/chi-in-a-box/kolla/node_custom_config/nova/policy.json /etc/kolla/nova-compute-fake-5/` since the fake hypervisors require the policy.json file, but it is not in the correct volume.

### Create a blazar host

Get the name of a hypervisor, and then run `openstack reservation host create <NAME>`

If that doesn't work, you may need to install [blazar client](https://github.com/ChameleonCloud/python-blazarclient) and/or run `blazar host-create <NAME>`

### Create a server on a fake hypervisor

First, you must have an image created. You can download the lightweight test image cirros from [here](http://download.cirros-cloud.net) and then run `openstack image create test-image --file cirros-0.5.2-x86_64-disk.img --disk-format qcow2`.

Check `openstack image list` to ensure the image was created.

Create a reservation for a host, as normal using blazar. Get the reservation ID.

Create the server: `openstack --os-compute-api-version 2.37 server create --image test-image --flavor mini my_server --hint reservation=<RES_ID> --network none`

### Creating a network&#x20;

For some services, it may be useful to create a network on your development instance. Here is an example network that can help with certain tasks.

```
# Create network
openstack network create \
    --provider-network-type flat \
    --provider-physical-network public \
    my-network

# Create subnet
openstack subnet create \
    --network my-network \
    --allocation-pool start=10.0.0.2,end=10.0.0.254 \
    --subnet-range 10.0.0.0/24 \
    my-subnet
```

After this is created, you can use the network ID when creating a Floating IP, for instance.

## Running tests

Openstack testing frameworks do not show the output from `LOG` statements. To see this output, modify the root logger:

```
from flask.logging import default_handler
from oslo_log import log as logging
root = logging.getLogger()
root.logger.addHandler(default_handler)
```
