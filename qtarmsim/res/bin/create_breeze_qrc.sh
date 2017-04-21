#!/bin/sh

# This script runs bin/qrcgen.py with the adecuate options
# Should be called after get_oxygen_icons.sh

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
DIRECTORY="breeze"
PREFIX="themes"

export PATH="/opt/local/bin:/opt/bin:$PATH"

cd ${SCRIPTPATH}/..

bin/qrcgen.py "$DIRECTORY" "$PREFIX"
