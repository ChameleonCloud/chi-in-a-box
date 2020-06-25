export OPENSTACK_RELEASE=train
export OS_BAREMETAL_API_VERSION=1.29

log() {
  echo "$@" >&2
}
export -f log

log "Loading OpenStack environment from $HOME/adminrc."
log

source "$HOME/adminrc"
