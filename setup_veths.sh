#!/bin/bash
set -euo pipefail

ifaces_to_veth="ext_api int_api physnet1 physnet2 physnet3"

for iface in ${ifaces_to_veth}
do
    vetha="${iface}_veth"
    vethb="${iface}_vethb"

    sudo ip link add \
        name ${vetha} \
        type veth \
        peer ${vethb} \
        || true

    sudo ip link set ${vetha} up
    sudo ip link set ${vethb} up

    if [[ "${iface}" == "ext_api" ]]; then
        sudo ip addr add 192.168.100.2/24 dev ${vetha}
    fi

    if [[ "${iface}" == "int_api" ]]; then
        sudo ip addr add 10.10.10.2/24 dev ${vetha}
    fi
done
