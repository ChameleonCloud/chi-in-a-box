#!/usr/bin/env bash
realm_name="$1"
backup_dir="/backup/${realm_name}_$(date +%Y-%m-%dT%H-%m)"

# Ensure proper permissions
docker exec -uroot keycloak_server chown -R jboss: /backup

# Create backup directory
docker exec keycloak_server mkdir -p "$backup_dir"

# Make FIFO pipe to read stdout from backgrounded Keycloak process
fifo=/tmp/krb.$(date +%s).fifo
mkfifo $fifo
trap "rm $fifo" EXIT

docker exec -e JBOSS_PIDFILE=/tmp/rb.pid keycloak_server /opt/jboss/keycloak/bin/standalone.sh \
  -Djboss.socket.binding.port-offset=100 -Dkeycloak.migration.action=export \
  -Dkeycloak.migration.realmName=$realm_name \
  -Dkeycloak.migration.usersExportStrategy=DIFFERENT_FILES \
  -Dkeycloak.migration.provider=dir \
  -Dkeycloak.migration.dir=$backup_dir >$fifo &

sed <$fifo '/KC-SERVICES0035/q' && {
  pid=$(docker exec keycloak_server sh -c 'cat /tmp/rb.pid; rm /tmp/rb.pid')
  echo "Attempting to kill Keycloak server (pid=$pid)"
  docker exec keycloak_server sh -c "kill $pid"
}

wait
