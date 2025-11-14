#!/bin/bash

set -euo pipefail

# Function to create veth pair if it doesn't exist
ensure_veth_up() {
    local dev1=$1
    local dev2=$2
    
    if ! ip link show "$dev1" &> /dev/null; then
        sudo ip link add dev "$dev1" type veth peer "$dev2"
    fi

    sudo ip link set "$dev1" up
    sudo ip link set "$dev2" up
}


ensure_veth_up external1 external2
sudo ip addr replace 129.114.34.128/25 dev external1

ensure_veth_up internal1 internal2
sudo ip addr replace 10.20.111.128/25 dev internal1

ensure_veth_up neutron1 neutron2
