#!/bin/bash

# this script sets up network interfaces for chi-in-a-box to use
# it is only useful for CI/CD purposes

set -x

function setup_ifaces {
    local bridge_name=$1
    local api_name=$2
    local neutron_name=$3
    local api_ip=$4

    sudo ip link add $bridge_name type bridge
    sudo ip link set $bridge_name up

    sudo ip link add $api_name type dummy
    sudo ip link set $api_name master $bridge_name
    sudo ip link set $api_name up
    sudo ip addr add $api_ip dev $api_name

    sudo ip link add $neutron_name type dummy
    sudo ip link set $neutron_name master $bridge_name
    sudo ip link set $neutron_name up
}

setup_ifaces $1 $2 $3 $4
