#!/bin/bash

set -euo pipefail

# Function to run a stage with GitHub Actions grouping
run_stage() {
    local stage_name="$1"
    shift
    
    if [ -n "${GITHUB_ACTIONS:-}" ]; then
        echo "::group::$stage_name"
    else
        echo "=== $stage_name ==="
    fi
    
    # Run the command and capture exit code
    "$@"
    local exit_code=$?
    
    if [ -n "${GITHUB_ACTIONS:-}" ]; then
        echo "::endgroup::"
        if [ $exit_code -ne 0 ]; then
            echo "::error::$stage_name failed"
        fi
    fi
    
    return $exit_code
}

copy_configs() {
    cp "./tests/${configdir}/defaults.yml" /opt/site-config/defaults.yml \
    && cp "./tests/${configdir}/host_vars.yml" "/opt/site-config/inventory/host_vars/$HOSTNAME"
}

configdir="${1}"

# set hostname to keep rabbit happy
sudo hostnamectl set-hostname "ciablocal"

run_stage "Install dependencies" ./cc-ansible install_deps

run_stage "Initialize site-config" ./cc-ansible init --site-config /opt/site-config || true

run_stage "Setup network interfaces" "./tests/${configdir}/setup_ifaces.sh"

run_stage "Copy configuration files" copy_configs

run_stage "Bootstrap servers" ./cc-ansible bootstrap-servers

run_stage "Deploy services" ./cc-ansible deploy

# run_stage "Post-deploy" ./cc-ansible post-deploy

# run_stage "Run tests" ./cc-ansible run-tests

echo "All stages completed successfully!"
