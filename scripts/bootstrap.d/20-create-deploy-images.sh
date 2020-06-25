file_base="https://tarballs.opendev.org/openstack/ironic-python-agent/dib/files/"

log "################################"
log " Deployment image setup"
log "################################"
log

os_image_create() {
  local name="$1"
  local file="$2"

  if [[ ! -e "$file" ]]; then
    log "Pulling $name image from $file_base."
    wget -q "$file_base/$file"
  fi

  openstack image show "$name" -f value -c id \
   || openstack image create -f value -c id \
      --public \
      --disk-format aki \
      --container-format aki \
      --file "$file" \
      "$name"
}

export DEPLOY_KERNEL="$(os_image_create deploy_kernel ipa-centos7-stable-$OPENSTACK_RELEASE.kernel)"
export DEPLOY_RAMDISK="$(os_image_create deploy_ramdisk ipa-centos7-stable-$OPENSTACK_RELEASE.initramfs)"

log "Done."
log
