#!/usr/bin/env bash
#
# Detect if any inputs match Kolla services or Ansible playbooks.
# Just looks at a list of string inputs and sees if they contain a Kolla service
# name or an Ansible playbook name. This is useful for knowing if a set of
# changed files in a commit affect a Kolla service configuration and therefore
# should be deployed.
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

echo "$(for s in ${kolla_services[@]}; do
  for l in $@; do
    if [[ "$l" == *"$s"* ]]; then
      echo -e "kolla\t$s"
    fi
  done
done | sort | uniq)"

playbooks=(
  docker_registry
  frontends
  jupyterhub
  metric_collector
  precis
  prometheus
  vendordata
)

echo "$(for s in ${playbooks[@]}; do
  for l in $@; do
    if [[ "$l" == *"$s"* ]]; then
      echo -e "playbook\t$s"
    fi
  done
done | sort | uniq)"
