#!/usr/bin/env bash
#
# Bootstrap script to configure all nodes.
#
# This script is intended to be used by vagrant to provision nodes.
# To use it, set it as 'PROVISION_SCRIPT' inside your Vagrantfile.custom.
# You can use Vagrantfile.custom.example as a template for this.

VM=$1
MODE=$2
CHI_IN_A_BOX_PATH=$3
NUMBER_OF_COMPUTE_NODES=$4
NUMBER_OF_STORAGE_NODES=$5
NUMBER_OF_NETWORK_NODES=$6
NUMBER_OF_CONTROL_NODES=$7
NUMBER_OF_MONITOR_NODES=$8

export http_proxy=
export https_proxy=

function _ensure_lsb_release {
    if type lsb_release >/dev/null 2>&1; then
        return
    fi

    if type apt-get >/dev/null 2>&1; then
        apt-get -y install lsb-release
    elif type yum >/dev/null 2>&1; then
        yum -y install redhat-lsb-core
    fi
}

function _is_distro {
    if [[ -z "$DISTRO" ]]; then
        _ensure_lsb_release
        DISTRO=$(lsb_release -si)
    fi

    [[ "$DISTRO" == "$1" ]]
}

function is_ubuntu {
    _is_distro "Ubuntu"
}

function is_centos {
    _is_distro "CentOS"
}

# Install common packages and do some prepwork.
function prep_work {
    yum install -y epel-release
}

# if [ "$MODE" == 'aio' ]; then
#     kolla-cli setdeploy local
#     kolla-cli host add localhost
#     for group in control deployment compute monitoring network storage; do
#         kolla-cli group addhost $group localhost
#     done
# else
#     for node_num in $(seq 1 ${NUMBER_OF_COMPUTE_NODES}); do
#         node_name="compute0${node_num}"
#         kolla-cli host add $node_name
#         kolla-cli group addhost compute $node_name
#     done

#     for node_num in $(seq 1 ${NUMBER_OF_STORAGE_NODES}); do
#         node_name="storage0${node_num}"
#         kolla-cli host add $node_name
#         kolla-cli group addhost storage $node_name
#     done

#     for node_num in $(seq 1 ${NUMBER_OF_NETWORK_NODES}); do
#         node_name="network0${node_num}"
#         kolla-cli host add $node_name
#         kolla-cli group addhost network $node_name
#     done

#     for node_num in $(seq 1 ${NUMBER_OF_CONTROL_NODES}); do
#         node_name="control0${node_num}"
#         kolla-cli host add $node_name
#         kolla-cli group addhost control $node_name
#     done

#     for node_num in $(seq 1 ${NUMBER_OF_MONITOR_NODES}); do
#         node_name="monitor0${node_num}"
#         kolla-cli host add $node_name
#         kolla-cli group addhost monitoring $node_name
#     done
# fi

# Configure the operator node and install some additional packages.
function configure_operator {
    yum install -y jq git python python-pip python-virtualenv

    pushd "$CHI_IN_A_BOX_PATH"
    VIRTUALENV=vagrant/venv ./cc-ansible init --site vagrant/site-config
    popd

    cat >/etc/profile.d/chi_in_a_box.sh <<EOF
export VIRTUALENV=$CHI_IN_A_BOX_PATH/vagrant/venv
export ANSIBLE_STRATEGY_PLUGINS=$CHI_IN_A_BOX_PATH/vagrant/venv/lib/mitogen-latest/ansible_mitogen/plugins/strategy
export CC_ANSIBLE_SITE=$CHI_IN_A_BOX_PATH/vagrant/site-config
EOF

    cat >>vagrant/site-config/host_vars/operator <<EOF
ansible_become: yes
ansible_become_user: root
EOF

    # Make sure Ansible uses scp.
    cat > ~vagrant/.ansible.cfg <<EOF
[defaults]
forks=100
remote_user = root

[ssh_connection]
scp_if_ssh=True
EOF
    chown vagrant: ~vagrant/.ansible.cfg
}

prep_work

if [[ "$VM" == "operator" ]]; then
    configure_operator
fi
