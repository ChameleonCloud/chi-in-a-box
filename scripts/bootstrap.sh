#!/usr/bin/env bash
set -e -u -o pipefail

dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"

NODE_CONF="$(realpath $1)"

for f in $(find "$dir/bootstrap.d" -type f -print | sort); do
  source "$f"
done
