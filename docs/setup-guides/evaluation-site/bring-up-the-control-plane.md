---
description: Bringing up only the control plane
---

# Bring up the Control Plane

## Controller node Configuration

### Verify Requirements

#### Check disk space

Here, we see that there is more than 20GB free in the root file system.

```
[root@dev01 ~]# df -h /
Filesystem               Size  Used Avail Use% Mounted on
/dev/mapper/cl_dev-root  228G  135G   94G  60% /
```

#### Check Available memory

We see that total memory is more than 8G.

```
[root@dev01 ~]# free -h
              total        used        free      shared  buff/cache   available
Mem:           125G        3.6G        106G         39M         15G        121G
Swap:          4.0G          0B        4.0G
```

{% tabs %}
{% tab title="Separate Public and Internal/Admin API Interfaces" %}
#### Check and configure networking for the Public API

Identify which network interface(s) you plan to use for the public API and ssh. We will refer to this as  `kolla_external_vip_interface`

For this example, we've made the following assumptions, but you will need to customize to your own values.

* `kolla_external_vip_interface`: `eth_public_api`
* interface ip address: `192.5.87.10/23`
* `kolla_external_vip_address`: `192.5.87.254`
* system hostname: `dev01`
* Here, we have chosen an interface named `eth_public_api` to act as the `kolla_external_vip_interface`

```
[root@dev01 ~]# ip addr show eth_public_api
2: em1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 44:a8:42:26:ef:aa brd ff:ff:ff:ff:ff:ff
    inet 192.5.87.10/23 brd 192.5.87.255 scope global eth_public_api
       valid_lft forever preferred_lft forever
```

We see that it has an address configured, and that `kolla_external_vip_address` is **not** present. This is correct, as `keepalived` will manage the VIP address.

#### Check and configure networking for the Internal/Admin API

Identify which network interface(s) you plan to use for the Admin/Internal API. We will refer to this as  `network_interface`

For this example, we've made the following assumptions, but you will need to customize to your own values.

* `network_interface`: `eth_internal_api`
* interface ip address: `10.20.111.10/23`
* `kolla_internal_vip_address`: `10.20.111.254`
* system hostname: `dev01`
* Here, we have chosen an interface named `eth_internal_api` to act as the `kolla_internal_vip_address`

```
[root@dev01 ~]# ip addr show eth_internal_api
2: em1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 44:a8:42:26:ef:aa brd ff:ff:ff:ff:ff:ff
    inet 10.20.111.10/23 brd 10.20.111.255 scope global eth_internal_api
       valid_lft forever preferred_lft forever
```

We see that it has an address configured, and that `kolla_internal_vip_address` is not present. This is correct, as `keepalived` will manage the VIP address.

#### Check and configure the system hostname

It's important that the system hostname resolves to the interface IP addresses, not to one of the VIPs

```
[root@dev01 ~]# hostname
dev01
[root@dev01 ~]# getent hosts dev01
10.20.111.254     dev01.chameleoncloud.org dev01
```

Note that the system hostname should **not** point to the `kolla_internal_vip_address`

If it does not resolve to the interface IP, this will be fixed during bootstrap later.&#x20;
{% endtab %}
{% endtabs %}

### Set up Linux users and permissions

We need somewhere to run the tools, and an account to run them as. We recommend not using the `root` account to do so. Ensure you have a non-root user account, with paswordless sudo configured. We will refer to this account as `deploy-user`, and their group as `deploy-group`. Replace these with your own values.

#### Ensure permissions and groups

```
# Create and join deploy-group
[deploy-user@dev01 ~]$ sudo groupadd <deploy-group>
[deploy-user@dev01 ~]$ sudo usermod -a -G <deploy-group> <deploy-user>

# Create and join docker group
[deploy-user@dev01 ~]$ sudo groupadd docker
[deploy-user@dev01 ~]$ sudo usermod -a -G docker <deploy-user>
```

Log out and back in to refresh group membership, then verify.

```
[deploy-user@dev01 ~]$ groups
... <deploy-group> docker
```

#### Set directory permissions

For this example, we'll be putting files into `/opt/`, so we need to ensure that it can be read and written by members of `deploy-group`

```
[deploy-user@dev01 ~]$ sudo chown root:<deploy-group> /opt
[deploy-user@dev01 ~]$ sudo chmod g+rw /opt
```

### Install Dependencies

Now we need to install some dependencies, then check out and set up chi-in-a-box

```
# Install Dependencies
sudo apt update && sudo apt install -f -y \
    python3 \
    python3-venv \
    jq \
    git
```

## Site Configuration

Clone and initialize chi-in-a-box. This assumes that we're using the `/opt` directory that was set up in the last section.

```
git clone https://github.com/ChameleonCloud/chi-in-a-box /opt/chi-in-a-box
cd /opt/chi-in-a-box
./cc-ansible init --site /opt/site-config
```

### Setting up the ansible hosts file

You'll need to configure a few lines in the file `/opt/site-config/inventory/hosts`, to tell cc-ansible which services to install where. Here, each of the `control`,`network`,`monitoring`,and `storage` groups get one entry, `dev01`, the hostname of your controller node. You don't need to modify the rest of the file.

```
# /opt/site-config/inventory/hosts

# These initial groups are the only groups required to be modified. The
# additional groups are for more control of the environment.
[control]
dev01

[network]
dev01

[compute]
# No compute node; this is a baremetal-only cluster.

[monitoring]
dev01

[storage]
dev01

[deployment]
localhost ansible_connection=local

# ... Don't edit below here ....
```

### Create a minimal \`defaults.yml\`

In your site config directory, `/opt/site-config`, you now have a file called `defaults.yml`

For a minimal deployment, you only need the following lines uncommented. The values are from the prior section.&#x20;

```
# /opt/site-config/defaults.yml

kolla_base_distro: ubuntu
kolla_internal_vip_address: 10.20.111.254
kolla_external_vip_address: 192.5.87.254

network_interface: eth_internal_api
kolla_external_vip_interface: eth_public_api
```

If you are using a separate `deploy` host from your `controller` , then you'll need to put the `_interface` lines into a separate file instead, `/opt/site-config/inventory/host_vars/<hostname>`, where `hostname` is `dev01` in this example.

### Bootstrap Servers

Run `cc-ansible --site /opt/site-config/ bootstrap-servers`

This will install docker, configure /etc/hosts, and generally configure the system to run the rest of the installation.

Afterwards, you should see that `/etc/hosts` contains an entry for your hostname, mapping it to the interface address. Note that this is NOT the haproxy VIP!

```
$ cat /etc/hosts
...
# BEGIN ANSIBLE GENERATED HOSTS
10.20.111.244 dev01
# END ANSIBLE GENERATED HOSTS
```

### Run Pre-checks

Run `cc-ansible --site /opt/site-config/ prechecks`

This will warn you about missing configuration, and other common errors.

<details>

<summary>Commonly seen prechecks errors</summary>

#### Check if ansible user can do passwordless sudo

Make sure that the user executing on the controller node can run `sudo` without a password. This can be ignored in the case that you're using a separate deploy host, and that the failure is only for the deploy host, not the controller node.

#### Fail if nscd is running

The nscd service will prevent parts of the deployment from completing successfully.\
Disable it by running `sudo systemctl disable --now nscd.service`&#x20;

#### Checking host OS distribution / Checking host OS release or version

Ensure that you're running a supported operating system on the controller node. Currently, we support `Ubuntu 20.04`GeFirst, you'll need to add our docker registry password to the passwords vault.

</details>

### Downloading Containers

#### Add our registry password

Run `./cc-ansible --site /opt/site-config edit_passwords`

Your default editor will open, and you'll see the following. Ensure that `docker_registry_password` is configured as follows.

```
...
docker_registry_password: kaQBdG9PRwlpTzknnhfGmvPf
...
```

The passwords file will be re-encrypted when you exit the editor.

After configuring this password, pull the containers!

#### Pull Container images

Run `./cc-ansible --site /opt/site-config pull`

<details>

<summary>Common issues on pull</summary>

#### manifest unknown

If you see an error message like the following, please contact us. It likely means that the container image is missing from our registry, and sometimes happens after CI errors.

`404 Client Error for http+docker://localhost/v1.41/images/create?tag=xena&fromImage=docker.chameleoncloud.org%2Fkolla%2Fubuntu-source-keystone: Not Found ("manifest for docker.chameleoncloud.org/kolla/ubuntu-source-keystone:xena not found: manifest unknown: manifest unknown")`



</details>

## Deploy!

You're now ready to run the deploy! This will bring up basic control plane services, listening on the IP addresses you configured above.

Run `./cc-ansible --site /opt/site-config deploy`

### Access your site

After deploy completes, you'll be able to access the horizon webui at `http://<kolla_external_vip_address>`

The username is `admin`, and the password can be found by running `cc-ansible --site /opt/site-config view_passwords | grep keystone_admin_password`

The next steps will set up easy API access, and create default networks, flavors, and images using the API.

There's not too much useful we can do until we enable some kind of compute service, and tenant network support, so those will come in the next steps.
