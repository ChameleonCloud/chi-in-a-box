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
git checkout ciab_minimal/2023.1
```

## install the ciab tols
```
uv venv .venv
source .venv/bin/activate 
uv pip install \
    -r requirements.txt \
    ../kolla-ansible
kolla-ansible install-deps
```

## Customize site-config

```
# generate passwords file
cp site-config/passwords.yml{.example,}

# and populate it with defaults
kolla-genpwd -p ../site-config/passwords.yml
```


edit globals.yml to set internal/external vip
edit host_vars/localhost to set interface names


## bootstrap servers
1. `./cc-ansible --site /home/cc/synced_files/site-config/ bootstrap-servers`
1. `./cc-ansible --site /home/cc/synced_files/site-config/ pull`
1. `./cc-ansible --site /home/cc/synced_files/site-config/ genconfig`
1. `./cc-ansible --site /home/cc/synced_files/site-config/ deploy`


<!-- uv pip install \
    -r requirements.txt \
    --reinstall-package kolla-ansible \
    ../kolla-ansible -->
