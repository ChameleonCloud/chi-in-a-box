log "################################"
log " Base images"
log "################################"
log
log "Installing base images."
log

for image in CC-CentOS7; do
  file="$image.qcow2"

  if [[ ! -e "$file" ]]; then
    log "Downloading image '$image'..."
    wget -O "$file" "https://chi.tacc.chameleoncloud.org:7480/swift/v1/CHI-in-a-Box_public/$file"
    log "Uploading to Glance..."
    openstack image create --file "$file" --disk-format "qcow2" --public "$image"
  fi
done

log "Done."
log
