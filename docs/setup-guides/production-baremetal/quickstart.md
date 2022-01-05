# Baremetal QuickStart

## Configure networking on the controller node

If you are only using two interfaces, you must do some additional configuration to avoid losing access during install (and other, hard to debug issues)

{% content-ref url="hostnetworking.md" %}
[hostnetworking.md](hostnetworking.md)
{% endcontent-ref %}

## Install Dependencies on the _controller node_

Commands in this section will use the system package manager, and run with root privileges. It is recommended to use python virtual environments to install chi-in-a-box and kolla-ansible.

{% tabs %}
{% tab title="Ubuntu 18.04" %}
* Install Python dependencies and [jq](https://stedolan.github.io/jq/)

```
sudo apt update && sudo apt install -f -y \
    python3 python3-virtuaenv virtualenv \
    jq
```

* Ensure `/usr/bin/python` links to `python3`

```
update-alternatives --install /usr/bin/python python /usr/bin/python3 1
```
{% endtab %}

{% tab title="Centos8" %}
* Install Python dependencies and [jq](https://stedolan.github.io/jq/)

```
sudo dnf install \
    python3-devel python3-libselinux python3-virtualenv \
    libffi-devel openssl-devel gcc jq
```

* Ensure `/usr/bin/python` links to `python3`

```
update-alternatives --install /usr/bin/python python /usr/bin/python3 1
```
{% endtab %}
{% endtabs %}

## Initialize the site configuration

1.  Check out this repository:

    ```bash
    git clone https://github.com/ChameleonCloud/chi-in-a-box.git
    cd chi-in-a-box
    ```
2.  Initialize your [site configuration ](../../reference/the-site-configuration/)by running `./cc-ansible init`. This will place a default site configuration into `../site-config`. You can specify a different location by running

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

## Site-Specific Configuration

### `${CC_ANSIBLE_SITE}/inventory/hosts`

*   Edit the [Ansible inventory](https://docs.ansible.com/ansible/latest/user\_guide/intro\_inventory.html) of your site configuration to include the hostname of the node you are installing to. It should look like this:

    ```ini
    # These initial groups are the only groups required to be modified. The
    # additional groups are for more control of the environment.
    [control]
    <hostname>

    [network]
    <hostname>

    [compute]
    # No compute node; this is a baremetal-only cluster.

    [monitoring]
    <hostname>

    [storage]
    <hostname>

    [deployment]
    localhost ansible_connection=local
    ```

    > **Note** If you used `./cc-ansible init` this may have been done automatically for you.

### `${CC_ANSIBLE_SITE}/inventory/host_vars/<hostname>`

* Update the "[host\_vars](https://docs.ansible.com/ansible/latest/user\_guide/intro\_inventory.html#organizing-host-and-group-variables)" file for your host to include the correct names of the network interfaces you want to use.
* **network\_interface** should be set to the name of the private interface (or bridge if only two interfaces) you chose
*   **kolla\_external\_vip\_interface** should be set to the name of the public interface (or bridge if only two interfaces) you chose

    ```yaml
    # for host with hostname "chihost"
    # file: inventory/host_vars/chihost.yml
    ---
    network_interface: eno1
    kolla_external_vip_interface: eno2
    ```

### `${CC_ANSIBLE_SITE}/defaults.yml`

1.  The following keys are mandatory for the install to complete. Set the values as appropriate to your setup.

    ```yaml
    openstack_region_name: CHI@XYZ
    chameleon_site_name: xyz

    kolla_internal_vip_address: <spare IP on private subnet>
    kolla_external_vip_address: <spare IP on public subnet>
    ```
2.  Provide a certificate matching the hostname, which must resolve to the chosen public IP.

    The certificate must be placed in  `${CC_ANSIBLE_SITE}/certificates/haproxy.pem`

    An HAProxy PEM file is a concatenation of the certificate, any intermediate certificates in the chain, and then the private key.

    ```bash
    cat certificate.crt intermediates.pem private.key > /etc/kolla/certificates/haproxy.pem
    ```
3.  If you haven't been provided a keystone\_idp\_client\_id by your federated ID provider, disable it for now:

    ```yaml
    enable_keystone_federation: no
    enable_keystone_federation_openid: no
    keystone_idp_client_id: null
    ```
4.  To give nodes internet access, at lease one internal and one external network must be enabled.

    ```yaml
    neutron_networks:
      - name: physnet1
        on_demand_vlan_ranges:
          - 200:250
        reservable_vlan_ranges:
          - 250:300
        bridge_name: br-eth1
        external_interface: <neutron internal interface, or veth-internalb if only two interfaces>
      - name: public
        bridge_name: br-ex
        external_interface: <neutron public interface, or veth-publicb if only two interfaces>
        # This should be your public IP block assigned to your deployment.
        cidr: 0.0.0.0/32
    ```
5.  To enable bare metal provisioning, provide a vlan and subnet for ironic to use.

    ```yaml
    ironic_provisioning_network_vlan: 200
    ironic_dnsmasq_dhcp_range: 10.51.0.0/24
    ```

## Bootstrap the _control node_

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

## Verify Configuration with Pre-Checks

*   kolla-ansible has a set of roles under `prechecks` to ensure that the system configuration is consistent and avoids known edge cases. Run these via the command

    ```bash
    ./cc-ansible prechecks
    ```
* For example, if the subnets configured in `defaults.yml` do not match your interfaces, an error will be thrown here.
* Similarly, kolla-ansible is not compatible with the service `nscd`, and will require that it be disabled before succeeding.

## Pull container images

All Chameleon services are packaged as Docker containers and they need to be downloaded to your host machine(s) as a first step. This will take a while depending on your connection.

1. The Chameleon Docker registry requires authentication. use the read-only password `kaQBdG9PRwlpTzknnhfGmvPf`
2.  run the following command, and set the value for key `docker_registry_password`

    ```bash
    ./cc-ansible edit_passwords
    ```
3.  Pull the container images.

    ```bash
    ./cc-ansible pull
    ```

## Deploy container images

Once the images are pulled, you can run the "deploy" phase, which sets up all the configuration for all the services and deploys them piece by piece.

```bash
./cc-ansible deploy
```

> **Note**: if you encounter errors and need to re-run the deploy step, which is expensive, you can skip parts you know have already succeeded. You can watch the Ansible output to see which "role" (service) it is updating. If you know a certain role has completed successfully, you can try skipping it on the next run with the `--skip-tags` option, e.g. `--skip-tags keystone,nova` to skip the Keystone and Nova provisioning. You can persist these by uncommenting their lines in `kolla-skip-tags`

### 6. Run post-deployment configuration

Once the deployment is complete, there should be a more or less functional OpenStack deployment that you can log in to. The admin credentials can be seen using `./cc-ansible view_passwords` under `keystone`

However, much of the bare metal functionality will not work, as there are a few special entities necessary, namely:

* A provisioning network on its own VLAN, which Ironic must know about
* Access on that VLAN to the Ironic TFTP server
* A "baremetal" Nova flavor that is used to allow users to schedule bare metal deployments
* Ironic deploy images available in Glance that hold the deployment ramdisk/kernel
* A special "freepool" Nova aggregate used by Blazar to manage node reservations

All of these will be provisioned by running the post-deploy script:

```bash
./cc-ansible post-deploy
```

### 7. Enroll bare metal nodes

To enroll your nodes, we have provided an enrollment script you can run against a configuration of nodes. To use this, first prepare some information about your nodes. You will need to pick a name for the node, know its (existing) IPMI address on the network (and be able to connect to this from the controller node already), its (existing) IPMI password, the MAC address for its NIC, the name of the switch it is connected to (which you have defined in `switch_configs` in your `defaults.yml` file), and which switch port it is connected to. An example is:

```ini
[node01]
ipmi_username = root
ipmi_password = hopefully_not_default
ipmi_address = 10.10.10.1
# Optional, defaults to this value.
ipmi_port = 623
# Arbitrary terminal port; this is used to plumb a socat process to allow
# reading and writing to a virtual console. It is just important that it does
# not conflict with another node or host process.
ipmi_terminal_port = 30133
[node01.ports.eno1]
switch_name = LeafSwitch01
switch_port_id = Te 1/10/1
mac_address = 00:00:de:ad:be:ef

# .. repeat for more nodes.
```

Once you have this file (let's call it `nodes.conf`), you can kick off the bootstrap script:

```bash
chameleon node enroll --node-conf nodes.conf
```

This script will enroll each node into Ironic and register its network port(s) (so Neutron can hook it up to networks later), as well as add the node to Blazar to make it reservable.

Once all of this has completed successfully, you should have a working setup capable of performing baremetal provisioning.

> **Note**: This enrollment script is designed to be run multiple times in case you encounter failures; it should be safe to re-run.

## Troubleshooting

### Speeding up repeated runs

Rerunning the install can take a long time. You can speed this up by uncommenting lines in the file `kolla-skip-tags`. Each line corresponds to a tag associated with an ansible task. For example, if the script keeps failing at configuring neutron, then uncomment the lines prior to neutron. Ansible will run the common setup tasks, then skip to the first tag that isn't uncommented.

### Finding out what's failing

Many times a failure is caused by a typo or missing line in defaults.yml or your host configuration. Run `./cc-ansible deploy` with multiple `-v` flags to get line-by-line errors.

For example, on centos8, /etc/modules-load.d may not exist, and you'll get an error like `failed: [shermanm-chibox] (item=ip_vs) => {"ansible_loop_var": "item", "changed": false, "item": {"name": "ip_vs"}, "msg": "Destination /etc/modules does not exist !", "rc": 257}`

running it with `-vvv` will show that it first checked for `/etc/modules-load.d` which also didn't exist.