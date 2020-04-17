#!/usr/bin/env bash
set -e -u -o pipefail

realm_name="$1"
backup_dir="/backup/${realm_name}_$(date +%Y-%m-%dT%H-%m)"

# Ensure proper permissions
docker exec -it -uroot keycloak_server chown -R jboss: /backup

# Create backup directory
docker exec -it keycloak_server mkdir -p "$backup_dir"

# Export realm
# The 'sed' will cause the server to automatically terminate if the message
# signifying the export completed successfully is printed.
docker exec -it keycloak_server /opt/jboss/keycloak/bin/standalone.sh \
  -Djboss.socket.binding.port-offset=100 -Dkeycloak.migration.action=export \
  -Dkeycloak.migration.realmName="$realm_name" \
  -Dkeycloak.migration.usersExportStrategy=DIFFERENT_FILES \
  -Dkeycloak.migration.provider=dir \
  -Dkeycloak.migration.dir="$backup_dir" \
  | sed '/KC-SERVICES0035/q'
