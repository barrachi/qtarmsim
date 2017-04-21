#!/bin/sh

# This script automatically grabs breeze icons required by QtARMSim

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
UIPATH="${SCRIPTPATH}/../../ui"
BREEZEPATH=/usr/share/icons/breeze/actions
BREEZEDSTPATH="${SCRIPTPATH}/../breeze"

if [ ! -d "${BREEZEPATH}" ]; then
    echo "Required '${BREEZEPATH}' not found."
    exit -1
fi

for file in ${UIPATH}/*.ui; do
    for line in $(grep '<iconset theme="' ${file}); do
	icon_name=$(echo ${line} \
	    | sed -e 's/^[^"]*//' -e 's/[^"]*$//' -e 's/"//g' )
	if [ -z "${icon_name}" ]; then
	    continue
	fi
	echo "Grabbing ${icon_name}..."
	for icon_file in $(find ${BREEZEPATH} -name "${icon_name}*svg"); do
	    RELPATH=$(dirname ${icon_file/${BREEZEPATH}\//})
	    mkdir -p ${BREEZEDSTPATH}/${RELPATH}
	    cp ${icon_file} ${BREEZEDSTPATH}/${RELPATH}
	done
    done
done

echo "Done!"
echo
echo "Now you cand run 'create_breeze_qrc.sh'"
