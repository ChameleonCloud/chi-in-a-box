---
description: Minimal evaluation site with no compute services
---

# Dev-in-a-Box

## Intro

To get familiar with the setup procedures for chi-in-a-box, or to develop services, you can follow this (very) minimal setup guide.

Note: This doesn't include support for TLS, or for communication outside of the single controller node. Services will be accessed via SSH tunnel or similar method.

## Prerequisites:

Baremetal or Virtual Machine with 4 cores, 8 gb ram, 40gb disk.
You must have a user account on the machine with passwordless sudo.

If launching a VM on Chameleon to host this, follow the following steps.

1. Launch an instance on KVM
   flavor: m1.xlarge
   image: CC-Ubuntu20.04
   network: sharednet1
2. Attach a floating IP
3. Allow SSH via the floating IP
4. SSH into the node as cc@floating-ip


## Installation

1.  Prepare a working directory. We use `/opt` by convention. It must be writable by your current user.

    ```bash
    cd /opt
    sudo chown cc:cc /opt
    ```
2.  Clone the chi-in-a-box repo, install, and initialize your site-configuration

    ```sh
    git clone https://github.com/ChameleonCloud/chi-in-a-box
    cd chi-in-a-box
    ./cc-ansible --site /opt/site-config/ init
    ```
3.  export an env var so you don't need to type "--site" for the remaining commands

    <pre class="language-bash"><code class="lang-bash">export CC_ANSIBLE_SITE=/opt/site-config/
    </code></pre>

4.  Create some veth-pairs to act as "dummy" network interfaces.

    External API interface
    ```bash
    sudo ip link add name ext_api_veth type veth peer ext_api_vethb
    sudo ip addr add 192.168.100.2/24 dev ext_api_veth
    sudo ip link set ext_api_veth up
    sudo ip link set ext_api_vethb up
    ```

    Internal API interface
    ```bash
    sudo ip link add name int_api_veth type veth peer int_api_vethb
    sudo ip addr add 10.10.10.2/24 dev int_api_veth
    sudo ip link set int_api_veth up
    sudo ip link set int_api_vethb up
    ```

    Neutron Provider Network interfaces
    ```bash
    sudo ip link add name physnet1_veth type veth peer physnet1_vethb
    sudo ip link set physnet1_veth up
    sudo ip link set physnet1_vethb up

    sudo ip link add name physnet2_veth type veth peer physnet2_vethb
    sudo ip link set physnet2_veth up
    sudo ip link set physnet2_vethb up

    sudo ip link add name physnet3_veth type veth peer physnet3_vethb
    sudo ip link set physnet3_veth up
    sudo ip link set physnet3_vethb up
    ```

5.  In your site-config, replace defaults.yml with the one for dev-in-a-box

    ```
    cp /opt/site-config/dev-in-a-box.yml /opt/site-config/defaults.yml
    ```

6.  Bootstrap the controller node, this will install apt packages, configure Docker, and modify /etc/hosts

    ```
    ./cc-ansible bootstrap-servers
    ```

7.  Run prechecks to ensure common issues are avoided.

    ```
    ./cc-ansible prechecks
    ```

    *   this will probably yell about nscd.service. If so, run the following, then rerun prechecks.

        ```
        sudo systemctl disable --now nscd.service
        ```
8.  Next, we'll pull container images for all configured services. This is done by running:

    ```
    ./cc-ansible pull
    ```
9.  We now need to generate the configuration that all of these services will use. This will combine the upstream defaults, contents of `chi-in-a-box`, and your `site-config`, and template config files into `/etc/kolla/<service_name>`

    ```
    ./cc-ansible genconfig
    ```

    * If you've added additional configuration, this step can warn you about invalid or missing config values, before actually modifying any running containers.
    * Even if the step passes, you may want to inspect files under `/etc/kolla/` to make sure they match your expectations.
10. Finally, we want to deploy the containers for each service. This step will start each necessary container, including running one-off bootstrap steps. If you've updated any of the service configurations, this step will restart the relevant containers and apply that config.\
    Technically, this step includes the `genconfig` step above, but it's mentioned separately for clarity.

    ```
    ./cc-ansible deploy
    ```
11. If all the steps so far have passed, all the core services should now be running! However, this isn't everything needed for a useful cloud. `post-deploy` consists of all the steps that require a functioning control plane. These include:
    * Creating default networks
    * Creating compute "flavors"
    * Uploading default disk images for users to use
    * Installing various hammers and other utility services/cron-jobs.
    To run this step, execute:
    ```
    ./cc-ansible post-deploy
    ```

12. Now, we'll create some "virtual" baremetal nodes, used to test out the site. These are just VMs run with libvirt, but are
configured via IPMI and pxe network booted like a baremetal node, so we can exercise Ironic. The following playbook will install and configure the `tenks` utility to accomplish this. At the end of the invocation, it will print out some commands for you to run yourself to finish the setup.

```
./cc-ansible --playbook playbooks/fake_baremetal.yml
```

13. Run the commands to bring up tenks. They will look something like the following, but may vary if you've changed your site-config from what's included here.

```
cd ~/tenks
source .venv/bin/activate # activate tenks virtualenv
source /opt/site-config/admin-openrc.sh # source admin credentials to enroll nodes

ansible-playbook \
    --inventory ansible/inventory/ \
    ansible/deploy.yml \
    --extra-vars="@override.yml"
```

Once it's finished, we'll need to add an IP address to the bridge it attached
for the ironic-provisioning network.

```
sudo ip addr add 10.205.10.1/24 brtenks0
```

14. Access your site! You can access it by the following methods:

    1. All services are listening on the haproxy VIP on "ext_api_veth" interface, so you need a way to get to 192.168.100.0/24.
       We recommend using `sshuttle` on your local machine, invoked as:
       `sshuttle -r cc@<floating_ip_address> 192.168.100.0/24`

    2.  HAProxy and thus Horizon are listening on 192.168.100.254:80, which you can access after starting sshuttle. The username is `admin`, and the password can be viewed by running the following command:

        ```
        ./cc-ansible view_passwords | grep "^keystone_admin_password"
        ```
    2.  You can use the Openstack CLI or API directly. The CLI tools are pre-installed in the chi-in-a-box virtualenv, and the admin credentials in an `admin-openrc` file in your site-config directory. Access the tools as follows:

        ```
        source /opt/chi-in-a-box/venv/bin/activate
        source /opt/site-config/admin-openrc.sh
        openstack <put command here>
        ```
