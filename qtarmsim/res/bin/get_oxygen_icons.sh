#!/bin/sh

# This script automatically grabs oxygen icons required by QtARMSim

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
UIPATH="${SCRIPTPATH}/../../ui"
OXYGENPATH=/usr/share/icons/oxygen
OXYGENDSTPATH="${SCRIPTPATH}/../oxygen"

if [ ! -d "${OXYGENPATH}" ]; then
    echo "Required '${OXYGENPATH}' not found."
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
	for icon_file in $(find ${OXYGENPATH} -name "${icon_name}*png"); do
	    RELPATH=$(dirname ${icon_file/${OXYGENPATH}\//})
	    mkdir -p ${OXYGENDSTPATH}/${RELPATH}
	    cp ${icon_file} ${OXYGENDSTPATH}/${RELPATH}
	done
    done
done

echo "Done!"
echo
echo "Now you cand run 'create_oxygen_qrc.sh'"

