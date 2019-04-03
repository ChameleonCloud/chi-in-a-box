#!/usr/bin/env bash
#
# Detect if any files match Kolla services. Just looks at a list of files
# and sees if they contain a Kolla service name. This is useful for knowing
# if a set of changed files in a commit affect a Kolla service configuration
# and therefor should be deployed.
#

kolla_services=(
  blazar
  cinder
  glance
  heat
  horizon
  ironic
  keystone
  neutron
  nova
)

detected_services="$(for s in ${kolla_services[@]}; do
  for l in $@; do
    if [[ "$l" == *"$s"* ]]; then
      echo "$s"
    fi
  done
done | sort | uniq)"

echo "$detected_services"
