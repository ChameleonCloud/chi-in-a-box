#!/bin/bash

# install uv
# clone and checkout ciab
# git submodule update --init
# install python3, python3-venv

set -euo pipefail

# rm -rf .venv
# rm -f site-config/passwords.yml
# rm -f site-config/globals.yml

# load a yaml config to use.
test_config="${1}"

# set ip addresses and ifaces
./testing/setup_ifaces.sh \
    $(yq '.ci_api_name' $test_config) \
    $(yq '.ci_neutron_name' $test_config) \
    $(yq '.ci_api_ip' $test_config)

# set hostname
sudo hostnamectl set-hostname "ciablocal"

uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt

kolla-ansible install-deps

# setup passwords. Not overwriting to permit repeated runs
cp --no-clobber site-config/passwords.yml{.example,}
kolla-genpwd -p site-config/passwords.yml

# overwriting globals.yml with test config
cat $test_config >> site-config/globals.yml

# ./cc-ansible --site site-config bootstrap-servers
# ./cc-ansible --site site-config prechecks
# ./cc-ansible --site site-config pull
# ./cc-ansible --site site-config genconfig
# ./cc-ansible --site site-config deploy
# ./cc-ansible --site site-config post-deploy
