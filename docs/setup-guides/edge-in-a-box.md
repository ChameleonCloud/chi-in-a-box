---
description: Guide to setting up an edge device testbed site such as CHI@Edge
---

# Edge-in-a-Box

## Intro

The following guide is meant to provide concise steps on how to setup an edge device testbed similar to [CHI@Edge](https://chi.edge.chameleoncloud.org/), the Chameleon edge research testbed.&#x20;

This guide assumes prior knowledge of how to use Chi-in-a-Box, we recommend at least reading and familiarizing yourself with the other&#x20;

### Install Dependencies on the controller node

Commands in this section will use the system package manager, and run with root privileges. It is recommended to use python virtual environments to install chi-in-a-box and kolla-ansible.

{% tabs %}
{% tab title="Ubuntu 20.04" %}
* Install Python dependencies and [jq](https://stedolan.github.io/jq/)

```
sudo apt update && sudo apt install -f -y \
    python3 python3-virtualenv python3-venv virtualenv \
    jq
```

* Ensure `/usr/bin/python` links to `python3`

```
update-alternatives --install /usr/bin/python python /usr/bin/python3 1
```
{% endtab %}
{% endtabs %}

### Initialize the site configuration

1.  Check out this repository:

    ```bash
    git clone https://github.com/ChameleonCloud/chi-in-a-box.git
    cd chi-in-a-box
    ```
2.  Initialize your [site configuration ](../before-you-begin/the-site-configuration/)by running `./cc-ansible init`. This will place a default site configuration into `../site-config`. You can specify a different location by running

    ```bash
     ./cc-ansible --site ../site-config init
    ```
3.  For example, running `./cc-ansible --site /opt/site-config init` should output:

    ```bash
    # Encryption successful
    # The beginnings of your site configuration were installed to /opt/site-config.
    # To use this site configuration automatically for future commands, you can
    # set an environment variable:

         export CC_ANSIBLE_SITE=/opt/site-config
    ```

    This will set the `CC_ANSIBLE_SITE` env var to point to this site configuration path for convenience. Consider adding it to your deploy user's login script. Example for bash:

    ```bash
    echo "export CC_ANSIBLE_SITE=/opt/site-config" >> ~/.bashrc
    ```

    Commands after this point assume that the environment variable is set.

    To override, use `./cc-ansible --site <path/to/site> <command>`

### Configure networking on the controller node

If you are only using two interfaces, you must do some additional configuration to avoid losing access during install (and other, hard to debug issues)

{% content-ref url="production-baremetal/hostnetworking.md" %}
[hostnetworking.md](production-baremetal/hostnetworking.md)
{% endcontent-ref %}

In addition to the above setup, edge-in-a-box requires the following physical networks to be set for the neutron flat networks to attach to:

#### `${CC_ANSIBLE_SITE}/defaults.yml`

```
# neutron logical networks needed
# public: where floating-ips live
# caliconet: where container private ips live
# tunelo-calico: "shadow network" used for wireguard IP assignment by tunelo "IPAM"


# neutron physical networks: mapping logical networks to real interfaces
# physnet1: where public logical network maps
# calico: where caliconet logical network maps
# tunelo: where tunelo-calico logical network maps

neutron_networks:
- name: physnet1
  bridge_name: br_physnet1
  external_interface: physnet1_veth
  public:
    segment_type: flat
    cidr: <your floating ip cidr here>
    gateway: <your gateway ip here>
    ip_range_start: <start of floating ip range>
    ip_range_end: <end of floating ip range>
- name: calico (dummy physnet)
  bridge_name: br_calico
  external_interface: physnet_calico
- name: tunelo (dummy physnet)
  bridge_name: br_tunelo
  external_interface: physnet_tunelo
```

## Edge-specific site configuration

Edge-in-a-box is built on a different set of components from traditional baremetal sites. in this section, we will show you how to configure the following components for edge-in-a-box

### General site configuration

#### `${CC_ANSIBLE_SITE}/defaults.yml`

```
openstack_region_name: "edge region name"
chameleon_site_name: "edge site name"
```

### Disabling unnecessary components

#### `${CC_ANSIBLE_SITE}/defaults.yml`

```
enable_ironic: no
enable_nova: no
enable_glance: no
enable_heat: no
```

### K3S, the container backend

Edge-in-a-Box uses Kubernetes as a backend to enable users to deploy their containerized workloads. The K3S ansible role and playbook comprised in Chi-in-a-Box is a core component of Edge-in-a-Box responsible for setting up a k3s cluster with the Calico CNI. To set up K3S, add the following options to&#x20;

#### `${CC_ANSIBLE_SITE}/defaults.yml`

```
enable_k3s: yes

# k3s_server_ip should be different from kolla_external_vip_address 
# since k3s is not proxied through HAProxy
k3s_server_ip: <k3s server ip> 
k3s_server_port: "6443"
```

### Zun, the container interface for Openstack

To drive the Kubernetes backend through an openstack interface, Edge-in-a-Box uses Openstack Zun, the dedicated container service in conjunction with a k8s compute driver developped by the Chameleon team for Zun to provide container services through an Openstack cloud layer. After enabling K3S, it is essential to enable zun as well as the K8S compute module for it. Add the following config options to&#x20;

&#x20; **`${CC_ANSIBLE_SITE}/defaults.yml`**

```
enable_zun: yes
enable_zun_compute_k8s: yes
```

### Wireguard tunnel management: Tunelo and Neutron-Wireguard

To enable secure networking to containers, Edge-in-a-Box sets up [Tunelo](https://github.com/ChameleonCloud/tunelo), a Chameleon-developed service that creates wireguard tunnels on demand, this service uses the neutron api to access the `tunelo-calico` neutron network where it creates ports for each tunnel it maintains.&#x20;

On the neutron side of things, a [Neutron ML2 driver ](https://github.com/ChameleonCloud/networking-wireguard)that represents Wireguard tunnels as a set of interconnected ports handles tunelo's requests. This Chameleon-developed driver is denoted as neutron-wireguard and is necessary to the functioning of wireguard tunnels in edge-in-a-box.

The result is that edge-in-a-Box maintaints a Hub and Spoke network configuration where the controller host acts as the wireguard hub and relays wireguard packets to the spokes (edge devices) .&#x20;

To enable Tunelo and neutron wireguard, add the following options to&#x20;

&#x20; **`${CC_ANSIBLE_SITE}/defaults.yml`**

```
enable_neutron_wireguard: yes
enable_tunelo: yes
```

**Note:** if you intend to only create one single wireguard hub port, it is important to scope it to the controller host's root network namespace. Add the following line to&#x20;

**`${CC_ANSIBLE_SITE}/defaults.yml`**

```
neutron_wireguard_create_hub_in_root_netns: True
```

### Device reservation management: Blazar

To enable advance reservation of edge devices, Edge-in-a-Box deploys Openstack Blazar. Using the chameleon-developed Kubernetes plugin for it, Blazar can set reservation labels on worker nodes in Kubernetes. To enable blazar and its Kubernetes plugin, add the following lines to&#x20;

&#x20; **`${CC_ANSIBLE_SITE}/defaults.yml`**

```
enable_blazar: yes
blazar_enable_device_plugin_k8s: yes
```

### Device enrollment management: Doni

Edge-in-a-Box deploys Doni to manage edge device enrollment. Doni is essentially the nerve center of edge-in-a-box, it is the main datastore for information about edge device enrollments; furthermore it handles the synchronization of edge device settings across servies such as:

* Wireguard Tunnel state per device
* Setting several Kubernetes settings such as authentication tokens, node labels/taints, and more
* Registration of the device with the Blazar reservation service
* Balena-cloud device enrollment and setting of environment variables and configuration&#x20;

To deploy Doni and configure it, add the following option to&#x20;

&#x20; **`${CC_ANSIBLE_SITE}/defaults.yml`**

```
enable_doni: yes
```

#### Device hardware management: Balena Cloud

To manage edge devices without physical access, edge-in-a-box assumes the existence of a balena cloud deployment. Doni then handles the responsibility of enrolling devices in balena. The setup of Balena-Cloud is entirely up to the operator but once done, to point Doni to the right balena-cloud fleet, add the following option to&#x20;

&#x20; **`${CC_ANSIBLE_SITE}/defaults.yml`**

```
default_balena_fleet: <name_of_your_balena_fleet>
```

### Bootstrap the controller node

1.  Bootstrap your controller node by running `./cc-ansible bootstrap-servers` With the default configuration, it would be:

    ```bash
    ./cc-ansible bootstrap-servers
    ```

    This will install Docker on your target node and put SELinux into permissive mode

    > currently [Kolla containers do not have working SELinux profiles.](https://bugs.launchpad.net/kolla-ansible/+bug/1797277)
2. Reboot if needed to apply SELinux changes
3.  If you plan to run the provisioning tools as a non-root user, you will need to allow access to Docker. One easy way is to add the user to the `docker` group, though this effectively gives the user root access. The deploy will install docker, but at this point you'll need to create the group manually.

    ```bash
    sudo groupadd -f docker
    sudo usermod -a -G docker $USER
    ```

    Log out and back in, and check your group membership using:

    ```bash
    groups
    #cc adm wheel systemd-journal docker
    ```

### Verify Configuration with Pre-Checks

*   kolla-ansible has a set of roles under `prechecks` to ensure that the system configuration is consistent and avoids known edge cases. Run these via the command

    ```bash
    ./cc-ansible prechecks
    ```
* For example, if the subnets configured in `defaults.yml` do not match your interfaces, an error will be thrown here.
* Similarly, kolla-ansible is not compatible with the service `nscd`, and will require that it be disabled before succeeding.&#x20;

### Pull container images

All Chameleon services are packaged as Docker containers and they need to be downloaded to your host machine(s) as a first step. This will take a while depending on your connection.

To pull the container images.

```bash
./cc-ansible pull
```

### Deploy container images

Once the images are pulled, you can run the "deploy" phase, which sets up all the configuration for all the services and deploys them piece by piece. It's important to note however that in Edge-in-a-Box, several components are not functional yet due to the absence of the Kubeconfig file which is to be generated as part of the K3S playbook in the next step. A later section explores these circular dependencies in more detail.

```bash
./cc-ansible deploy
```

> **Note**: if you encounter errors and need to re-run the deploy step, which is expensive, you can skip parts you know have already succeeded. You can watch the Ansible output to see which "role" (service) it is updating. If you know a certain role has completed successfully, you can try skipping it on the next run with the `--skip-tags` option, e.g. `--skip-tags keystone,nova` to skip the Keystone and Nova provisioning. You can persist these by uncommenting their lines in `kolla-skip-tags`

### Deploy K3S Playbook

The K3S playbook performs a bulk of essential tasks in Edge-in-a-Box. Here is an outline of all its tasks and some manual additions that have to be made by the operator.

* Config K3S service:  Installs K3S, starts the K3S service, and generates the kubeconfig
* Config K3S client: sets up node token file, and creates symlinks for Kubernetes command line utilities
* Config Calico: Downloads and installs [Calico](https://www.tigera.io/project-calico/) container network runtime, and applies the following global network policies
  * allow-ping: Allow ICMP ping over ipv4 and ipv6
  * default-deny: allow all namespaces to communicate to DNS pods
* Config device plugins: configures [nvidia-device-plugin](https://github.com/NVIDIA/k8s-device-plugin) and [smarter-device-manager](https://github.com/smarter-project/smarter-device-manager) plugin daemonsets on the worker-nodes
* Config Neutron: Essential step to enable wireguard connectivity and floating ip connectivity to worker containers:
  * Sets up the three essential neutron networks for edge-in-a-box:
    * `public`: manages publicly routable floating ips
    * `caliconet`: manages container private ips
    * `tunelo-calico`: "shadow network" used for wireguard IP assignment by tunelo "IPAM"
  * **Manual step needed by operator to enable floating ip connectivity**
    * add the `caliconet-subnet` as an internal interface to the admin router
    * Add an external gateway to the `public` network to the admin router
  * Finally, the config-neutron task generate a Calico/Neutron connection script which creates routing rules for traffic incoming for caliconet ports through public floating ips

To deploy K3S playbook, run the following command

```
./cc-ansible --playbook playbooks/k3s.yml
```

**Important Note:** Due to some circular dependencies in the sequence of deployment between K3S playbook and the rest of the components, it may become necessary to run the playbook another time after the deployment of services and vice-versa until the state is satisfactory.

### Redeploy services that require a `Kubeconfig`

The following services require a `kubeconfig` file to access the Kubernetes cluster, it's important to redeploy them.

* Zun
* Blazar
* Doni

```
./cc-ansible reconfigure --tags zun,blazar,doni --site ../site-config/
```

### Enabling Kubernetes worker-node tainting

To ensure that Kubernetes core services and any unintended services do not get scheduled on worker nodes. Edge-in-a-Box supports adding a special taint that is applied through Doni to every worker node. Furthermore, every user container launched by Zun tolerates this taint if enabled.&#x20;

#### Deployment strategy for a new edge site&#x20;

Add the worker node taint to

&#x20; **`${CC_ANSIBLE_SITE}/defaults.yml`**

```
k8s_worker_taint:
    key: "worker-node"
    value: "true"
    effect: "NoSchedule"
zun_tolerate_worker_taint: True # Tells Zun to add tolerations to the taint
doni_enable_worker_taint: True # Tells Doni add the taint every worker node
```

#### Deployment strategy for a running edge site&#x20;

To avoid any downtime of core services or eviction of existing user pods, follow these steps in order to enable worker node tainting for a running edge-in-a-box deployment:

1.  Add the taint to the site's config and enable Zun tolerations but keep Doni tainting disabled

    ```
    k8s_worker_taint:
        key: "worker-node"
        value: "true"
        effect: "NoSchedule"
    zun_tolerate_worker_taint: True
    doni_enable_worker_taint: False 
    ```
2.  Re-deploy K3S playbook to apply tolerations to the core device plugins `daemonsets`

    ```
    ./cc-ansible --playbook playbooks/k3s.yml
    ```
3.  Redeploy Zun so that it starts adding tolerations to newly launched user containers

    ```
    ./cc-ansible reconfigure --tags zun --site ../site-config/
    ```
4.  Finally, set `doni_enable_worker_taint` to `True` and re-deploy Doni

    ```
    doni_enable_worker_taint: True 

    # Run the following command
    ./cc-ansible reconfigure --tags doni --site ../site-config/
    ```
5. Re-sync all devices after re-deploying Doni.

The edge site should now be operational.
