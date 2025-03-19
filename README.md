# Overview

This repos is intended to be used as a minimal starting point to deploy the "KVM flavor" of chi-in-a-box.
The design goal was to minimize the delta between this and upstream kolla-ansible, while still adding the following features:

- Federated Login with Chameleon's Keycloak, including mapping of user projects
- Apply the Chameleon Theme to horizon

While it defaults to a single-node, all-in-one installation for dev and CI/CD use, this is by no means mandatory.

## Prerequisites

This installs the "minimal/ussuri-kvm" branch of chi-in-a-box, based off of kolla-ansible's ussuri release. (specifically the tag `ussuri-eol`).

Therefore, please follow the minimum requirements found here: https://docs.openstack.org/kolla-ansible/ussuri/user/quickstart.html

* Ubuntu20.04, x86_64
* 8GB RAM
* 40GB Disk
* 2 network interfaces (can get away with 1 for CI/CD Only)

## Setup: Single node CI/CD example

This process follows a very minimal path, also executed by our CI scripts.
You're free to leave parts out and customize them, which will be noted.

### 1: Upgrade apt packages

To ensure a consistent starting point, expecially on 20.04:

```
sudo apt-get update && \
sudo apt-get dist-upgrade -y
```

### 2: Install APT Dependencies

```
sudo apt-get update && \
sudo apt-get install -y \
    python3-dev \
    libffi-dev \
    gcc \
    libssl-dev \
    python3-venv
```

### 3: clone the chi-in-a-box repo

```
git clone https://github.com/chameleoncloud/chi-in-a-box
cd chi-in-a-box
git checkout minimal/ussuri-kvm
git submodule update --init
```

### 4: install the ciab tools

Just for faster setup, we'll add `uv`, a much faster python package manager.
```
curl -L https://github.com/astral-sh/uv/releases/download/0.6.8/uv-x86_64-unknown-linux-gnu.tar.gz \
| tar -xzv \
&& sudo mv uv-x86_64-unknown-linux-gnu/uv /usr/local/bin/
```

Then:
```
uv venv .venv
source .venv/bin/activate 
uv pip install -r requirements.txt
```


### Customize the site-config

```
# generate passwords file
cp site-config/passwords.yml{.example,}

# and populate it with defaults
kolla-genpwd -p site-config/passwords.yml
```

If using the minimal CI config, add the following to `site-config/globals.yml`
```
kolla_internal_vip_address: "172.18.200.254"
network_interface: "fake_br"
neutron_external_interface: "dummy1"
```

Then set up the corresponding dummy network interfaces:
```
sudo ip link add fake_br type bridge
sudo ip link set fake_br up
sudo ip addr add 172.18.200.10/24 dev fake_br

sudo ip link add kolla_veth type veth peer name dummy1
sudo ip link set kolla_veth up
sudo ip link set kolla_veth master fake_br

sudo ip link set dummy1 up 
```


## deploy the site

The below steps are a little slower, and more verbose than strictly necessary, but will make any inconsistencies clearer.

On a known working site, pull and genconfig can be skipped.

```
./cc-ansible --site site-config bootstrap-servers
./cc-ansible --site site-config prechecks
./cc-ansible --site site-config pull
./cc-ansible --site site-config genconfig
./cc-ansible --site site-config deploy
./cc-ansible --site site-config post-deploy
```

## Kicking the tires

At this point, all services should be online and accessible.

Run the following to verify basic functionality:

```
source site-config/admin-openrc.sh
openstack endpoint list
```

You can access the horizon dashboard via a ssh tunnel, such as via sshuttle:
```
sshuttle -r $ssh_user@$ssh_ip 172.18.200.254/32
```
