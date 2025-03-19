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
* 2 network interfaces, but we can get away with 1 for CI/CD purposes only.

## Setup

### Install APT Dependencies

```
sudo apt-get update && \
sudo apt-get install -y \
    python3-dev \
    libffi-dev \
    gcc \
    libssl-dev \
    python3-venv
```


### Optional Deps for CI/CD

If using our CI/CD test scripts, or otherwise following them, you'll also need
`astral-uv` (an alterante python package manager), and `yq`.

There are no run-time dependencies on these, they're merely used for some of the scripts under `testing/`.

```
sudo snap install --classic \
    astral-uv
    
sudo snap install \
    yq
```

## get chi-in-a-box repo

```
git clone https://github.com/chameleoncloud/chi-in-a-box
cd chi-in-a-box
git checkout minimal/ussuri-kvm
```

## install the ciab tools
```
uv venv .venv
source .venv/bin/activate 
uv pip install -r requirements.txt
```

## Customize site-config

```
# generate passwords file
cp site-config/passwords.yml{.example,}

# and populate it with defaults
kolla-genpwd -p site-config/passwords.yml
```

edit globals.yml to set internal/external vip
edit host_vars/localhost to set interface names

To automatically generate an extra-minimal CI/CD config, run
`./testing/setup_ciab.sh ./testing/configs/base.yml`


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

At this point, you can access the horizon dasboard at `kolla_external_vip_address`, logging in with the username+password found in `site-config/admin-openrc.sh`
