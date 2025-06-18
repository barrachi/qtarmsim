#!/usr/bin/env bash

set -o errexit
set -o nounset

# This script automatically grabs breeze icons required by QtARMSim

TMP_DIR=$(mktemp -d /tmp/tmp_get_breeze_icons.XXXXXXXXXXX)
trap 'rm -rf "${TMP_DIR}"' EXIT

SCRIPT_PATH="$( cd "$(dirname "$0")" ; pwd -P )"

UI_PATH="$(realpath ${SCRIPT_PATH}/../../ui)"
MAIN_WINDOW_UI_PATH="${UI_PATH}/mainwindow.ui"
BREEZE_ICONS_PATH="$(realpath ${SCRIPT_PATH}/../breeze_icons)"
BREEZE_ICONS_DARK_PATH="$(realpath ${SCRIPT_PATH}/../breeze_icons_dark)"

# Download a copy of the breeze-icons project
git clone --depth 1 https://invent.kde.org/frameworks/breeze-icons.git "${TMP_DIR}"

# Create BREEZE_ICONS_PATH and BREEZE_ICONS_DARK_PATH
for DIR in "${BREEZE_ICONS_PATH}" "${BREEZE_ICONS_DARK_PATH}"; do
  [[ -d "${DIR}" ]] || mkdir "${DIR}"
done

SIZE_AND_SVGs=$(grep svg ../ui/mainwindow.ui | tr '<' '/' | cut -f 4,5 -d '/')

for SIZE_AND_SVG in ${SIZE_AND_SVGs}; do
  SIZE=$(echo ${SIZE_AND_SVG} | cut -f 1 -d '/')
  SVG=$(echo ${SIZE_AND_SVG} | cut -f 2 -d '/')
  for DIR in "${BREEZE_ICONS_PATH}" "${BREEZE_ICONS_DARK_PATH}"; do
    [[ -d "${DIR}/${SIZE}" ]] || mkdir "${DIR}/${SIZE}"
  done
  find "${TMP_DIR}/icons" -path "*${SIZE}/*${SVG}" -exec cp {} "${BREEZE_ICONS_PATH}/${SIZE}/${SVG}" \;
  find "${TMP_DIR}/icons-dark" -path "*${SIZE}/*${SVG}" -exec cp {} "${BREEZE_ICONS_DARK_PATH}/${SIZE}/${SVG}" \;
done

echo "Done!"
echo
echo "Now you cand run 'create_breeze_icons_qrc.sh'"
