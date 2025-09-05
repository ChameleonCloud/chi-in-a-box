#!/bin/bash

# This script sets up chi-in-a-box for testing
# It assumes that you have already cloned the chi-in-a-box repository

# Rather than assume anything about the network interfaces, it creates dummy interfaces
# for external and internal api networks

# Features not tested!
# - federated identity
# - baremetal nodes
# - floating IPs


setup_networking () {
    # Create dummy interfaces


    # kolla public/external iface
    sudo ip link add veth_publica type veth peer veth_publicb
    sudo ip addr add 192.168.200.10/24 dev veth_publica
    sudo ip link set veth_publica up
    sudo ip link set veth_publicb up

    # kolla internal iface
    sudo ip link add veth_inta type veth peer veth_intb
    sudo ip addr add 10.10.10.10/24 dev veth_inta
    sudo ip link set veth_inta up
    sudo ip link set veth_intb up

    # neutron external iface
    sudo ip link add veth_neutrona type veth peer veth_neutronb
    sudo ip link set veth_neutrona up
    sudo ip link set veth_neutronb up
}

### Start main section

setup_networking

# setup venv and install deps
./cc-ansible install_deps

# initialize cc-ansible site
./cc-ansible init --site ../site-config
