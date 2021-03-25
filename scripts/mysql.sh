#!/usr/bin/env bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"
pushd $(realpath $DIR/..) >/dev/null

root_pw="$(./cc-ansible view_passwords | grep -E '^database_password' | cut -d' ' -f2)"
docker exec -it -e MYSQL_PWD="$root_pw" mariadb mysql -uroot "$@"
