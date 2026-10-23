#!/bin/sh
set -eu
TASKPACK_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec python3 "$TASKPACK_DIR/qualify.py" "$@"
