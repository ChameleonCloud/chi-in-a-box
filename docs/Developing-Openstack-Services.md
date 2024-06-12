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

First, you must have an image created. You can download the lightweight test image cirros from [here](http://download.cirros-cloud.net/) and then run `openstack image create test-image --file cirros-0.5.2-x86_64-disk.img --disk-format qcow2`.

Check `openstack image list` to ensure the image was created.

Create a reservation for a host, as normal using blazar. Get the reservation ID.

Create the server: `openstack --os-compute-api-version 2.37 server create --image test-image --flavor mini my_server --hint reservation=<RES_ID> --network none`

### Creating a network

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

## Customizing Containers

CHI-in-a-box, kolla-ansible, and kolla allow for customization at many levels.

#### Kolla

The containers and their dockerfiles are defined in the [kolla repository](https://github.com/ChameleonCloud/kolla), for example,  [certbot](https://github.com/ChameleonCloud/kolla/blob/chameleoncloud/xena/docker/letsencrypt/letsencrypt-certbot/Dockerfile.j2).\
These dockerfiles contain macros and support templating.

```
{% raw %}
{% block letsencrypt_certbot_header %}{% endblock %}
{% endraw %}
```

#### Kolla-containers

The Build-time customization is done in the [kolla-containers](https://github.com/ChameleonCloud/kolla-containers) repository. We maintain a file, `template-overrides.j2`, with per-service overrides. In addition, the [kolla-build.conf](https://github.com/ChameleonCloud/kolla-containers/blob/xena/kolla-build.conf.j2) sets build-wide settings, including the git repos and branches to use for each service build.&#x20;

We have an extra layer of templating in place, as we maintain multiple variants of this build config. Currently, we have the following variants.

| OpenStack Release | Operating System | Architecture | Variant   |
| ----------------- | ---------------- | ------------ | --------- |
| Xena              | Ubuntu 20.04     | x86\_64      | Baremetal |
| Xena              | Ubuntu 20.04     | x86\_64      | CHI@Edge  |
| Train             | Centos7          | x86\_64      | KVM       |

All Centos8 variants are deprecated, as are the arm64 builds for CHI@Edge.

#### Kolla-Ansible

[Kolla-ansible](https://github.com/ChameleonCloud/kolla-ansible) defines run-time defaults, configuration, and tooling. Each service has a set of roles, corresponding to deployment phases. [See Letsencrypt example.](https://github.com/ChameleonCloud/kolla-ansible/tree/chameleoncloud/xena/ansible/roles/letsencrypt/tasks)

They template configuration files from ansible key-value pairs into a configuration directory, usually `/etc/kolla/service`. The source for said configuration can be selectively overridden. `merge_configs` will combine ini-like config from the entries, while `with_first_found` will do as its name suggests.

```yaml
merge_configs:
  sources:
    - "{{ role_path }}/templates/doni.conf.j2"
    - "{{ node_custom_config }}/global.conf"
    - "{{ node_custom_config }}/doni.conf"
    - "{{ node_custom_config }}/doni/{{ item.key }}.conf"
    - "{{ node_custom_config }}/doni/{{ inventory_hostname }}/doni.conf"
```

Finally, each time a container starts, it uses a `config.json` file to define what volumes to load, and what config files to copy from said volume into its runtime location. Example for [Doni-worker](https://github.com/ChameleonCloud/kolla-ansible/blob/chameleoncloud/xena/ansible/roles/doni/templates/doni-worker.json.j2).

Upstream documentation: [https://docs.openstack.org/kolla/latest/admin/kolla\_api.html](https://docs.openstack.org/kolla/latest/admin/kolla\_api.html)

#### CHI-in-a-box

Finally, the [chi-in-a-box repository](https://github.com/ChameleonCloud/chi-in-a-box) sets the key-value pairs used by kolla-ansbile for configuration, as well as provides templated configuration files, using by the above `merge_configs` or `with_first_found` methods.&#x20;

Configuration files are applied in the following order, with more specific replacing less specific.

* defaults from kolla-ansible
* `node_custom_config/service.conf`
* `node_custom_config/service/service.conf`
* `node_custom_config/service/hostname/service.conf`

See the [kolla-ansible docs](https://docs.openstack.org/kolla-ansible/latest/admin/advanced-configuration.html#openstack-service-configuration-in-kolla) for more.&#x20;


## Running end-to-end functional tests with Tempest

Openstack Tempest is a framework to exercise the API of a deployed Openstack site. You can utilize this to make sure that your changes have not broken the API's compatibility, and generally that tasks such as a creating a network or launching an instance work as expected.

CHI-in-a-box includes a playbook to install and configure tempest to run against the local development site. 

WARNING: Do NOT run this against a production site, or one with user instances/data present. Although tempest seeks to isolate the resources it creates/deletes in ephemerial Openstack Projects, it can easily consume all networks/floating ips/other instance resources on your site. Addtionally, cleaning up after tempest is not always straightforward, and significant care must be taken to avoid deleting user created resources.

For this reason, we currently recommend running these tests only against a development site, or before releasing a site to end-users. 
We are working on a "safe subset" configuration, but it's not ready yet.


After setting your site up, including `post-deploy`, set the following parameters in your defaults.yml:

```
tempest_fixed_network_name: "sharednet1"
tempest_public_network_uuid:  <uuid of public neutron network>
tempest_compute_image_uuid:  <uuid of glance image to test instances with>
tempest_baremetal_flavor_uuid: <uuid of the barmetal flavor>
```

If updating an existing site to add this feature, you'll need to add the following ansible group to your `inventory/hosts` file.

Then, run `cc-ansible --playbook playbooks/tempest.yml` to install the tempest config file and tools. They will be installed into `~/tempest` by default, but you can override this by setting `tempest_install_dir` in your defaults.yml.

After installing, run the following:
```
cd ~/tempest
source .venv/bin/activate

tempest run 
  --workspace local \
  --concurrency 1 \
  --smoke
```
This will run a subset of important tests against your dev site.

Concurrency is set to 1 to avoid running out of baremetal nodes, you can turn this up if more nodes are available. To run all tests, instead of the most critical subset, remove `--smoke`

For an example of how to exclude specific tests, append the argument:
`--exclude-list /opt/chi-in-a-box/roles/tempest/templates/exclude-list.conf`
This list excludes tests which are known to fail if only `flat` networks are availalable, namely anything to do with user creation/update/delete of tenant networks.
