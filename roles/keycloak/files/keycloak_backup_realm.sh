#!/usr/bin/env bash
set -e -u -o pipefail

realm_name="$1"

docker exec -it keycloak_server /opt/jboss/keycloak/bin/standalone.sh
  -Djboss.socket.binding.port-offset=100 -Dkeycloak.migration.action=export
  -Dkeycloak.migration.realmName="$realm_name"
  -Dkeycloak.migration.usersExportStrategy=DIFFERENT_FILES
  -Dkeycloak.migration.provider=dir
  -Dkeycloak.migration.dir="/backup/${realm_name}_$(date +%Y-%m-%dT%H-%m)"
