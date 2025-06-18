#!/bin/sh

# This script runs bin/qrcgen.py with the adequate options
# Should be called after get_breeze_icons.sh

SCRIPT_PATH="$( cd "$(dirname "$0")" ; pwd -P )"
DIRECTORY="breeze_icons"
PREFIX="themes"

export PATH="/opt/local/bin:/opt/bin:$PATH"

cd ${SCRIPT_PATH}/..

bin/qrcgen.py "$DIRECTORY" "$PREFIX"
