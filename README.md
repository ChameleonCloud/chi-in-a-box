# Steps in order

## Install needed dependencies

```
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

## get chi-in-a-box repo

```
git clone https://github.com/chameleoncloud/chi-in-a-box
cd chi-in-a-box
git checkout minimal/xena-kvm
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


## post deploy stuff

* create public network and subnet
  ```
  openstack network create --external --default --provider-physical-network physnet1 --provider-network-type flat public
  openstack subnet create --no-dhcp --network public \
    --subnet-range 172.18.200.0/24 \
    --allocation-pool start=172.18.200.100,end=172.18.200.200 \
    public
  ```
* create calico network and subnet
  ```
  openstack network create --share caliconet
  openstack subnet create --network caliconet --no-dhcp --subnet-range 192.168.0.0/16 caliconet
  ```
* create router
  ```
  openstack router create public \
    --external-gateway public
  openstack router add subnet public caliconet
  ```
