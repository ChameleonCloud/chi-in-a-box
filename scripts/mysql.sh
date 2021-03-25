#!/usr/bin/env bash
# A simple helper to get a MySQL prompt after authenticating as the root user.
#
# Usage:
#   ./scripts/mysql.sh
#
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"
pushd $(realpath $DIR/..) >/dev/null

root_pw="$(./cc-ansible view_passwords | grep -E '^database_password' | cut -d' ' -f2)"
docker exec -it -e MYSQL_PWD="$root_pw" mariadb mysql -uroot "$@"
