#!/bin/bash

# this script sets up network interfaces for chi-in-a-box to use
# it is only useful for CI/CD purposes

set -x

function setup_ifaces {
    local api_name=$1
    local neutron_name=$2
    local api_ip=$3

    sudo ip link add $api_name type bridge
    sudo ip link set $api_name up
    sudo ip addr add $api_ip dev $api_name

    sudo ip link add kolla_veth type veth peer name $neutron_name
    sudo ip link set kolla_veth up
    sudo ip link set kolla_veth master $api_name

    sudo ip link set $neutron_name up   
}

setup_ifaces $1 $2 $3
