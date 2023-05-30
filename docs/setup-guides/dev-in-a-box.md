---
description: Minimal evaluation site with no compute services
---

# Dev-in-a-Box

## Intro

To get familiar with the setup procedures for chi-in-a-box, or to develop services, you can follow this (very) minimal setup guide.

Note: This doesn't include support for HAProxy, TLS, or any compute services (Nova, Ironic, or Zun). Please don't use this guide for a production site, as it compromises security and reliability for simplicity.

## Prerequisites:

Baremetal or Virtual Machine with 4 cores, 8 gb ram, 40gb disk.

You must have a user account on the machine with passwordless sudo.

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

    <pre class="language-bash"><code class="lang-bash"><strong>export CC_ANSIBLE_SITE=/opt/site-config/
    </strong></code></pre>
4.  Create a dummy loopback interface to bind services to. You can choose whatever interface name and IP you want. The name will be later used for the `network_interface` and the IP for `kolla_internal_vip_address` in the next step.

    ```bash
    ip link add name diab type dummy
    ip addr add 10.100.100.1/32 dev diab
    ```
5.  &#x20;Edit `/opt/site-config/defaults.yml` to contain ONLY the following lines.

    ```yaml
    ---
    kolla_base_distro: ubuntu
    network_interface: diab
    kolla_internal_vip_address: 10.100.100.1
    enable_haproxy: no

    # Disable central logging to reduce resource usage (no elasticsearch or kibana)
    enable_central_logging: no
    # Disable prometheus to speed up deployment
    enable_prometheus: no
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
    1. Creating default networks
    2. Creating compute "flavors"
    3. Uploading default disk images for users to use
    4. Installing various hammers and other utility services/cron-jobs.
    5.  To run this step, execute:

        ```
        ./cc-ansible post-deploy
        ```
12. Use your site! You can access it by the following methods:
    1.  Horizon is listening on 127.0.0.1:80, you can access it by forwarding your browser over SSH, for example via sshuttle. The username is `admin`, and the password can be viewed by running the following command:

        ```
        ./cc-ansible view_passwords | grep "^keystone_admin_password"
        ```
    2.  You can use the Openstack CLI or API directly. The CLI tools are pre-installed in the chi-in-a-box virtualenv, and the admin credentials in an `admin-openrc` file in your site-config directory. Access the tools as follows:

        ```
        source /opt/chi-in-a-box/venv/bin/activate
        source /opt/site-config/admin-openrc.sh
        openstack <put command here>
        ```
