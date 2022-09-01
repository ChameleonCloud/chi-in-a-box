#!/usr/bin/env bash
# A simple helper to get a MySQL prompt after authenticating as the root user.
#
# Usage:
#   ./scripts/mysql.sh
#
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"
pushd $(realpath $DIR/..) >/dev/null

RW_USER="root"
RW_PASSWORD_KEY="database_password"

get_pw_cmd="./cc-ansible view_passwords"
root_pw=`$get_pw_cmd | grep -E ^$RW_PASSWORD_KEY: | cut -d' ' -f2`

docker exec -it \
    -e MYSQL_PWD="$root_pw" \
    mariadb \
    mysql -uroot "$@"
