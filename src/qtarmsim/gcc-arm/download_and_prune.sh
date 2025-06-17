#!/bin/bash

set -o errexit
set -o nounset

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd ${SCRIPT_DIR}

# -------------------------------------------------------------------
# Select the correct versions from
# https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads
# The order should be:
#  1. Windows
#  2. Linux x86_64
#  3. Linux AARCH64
#  4. macOS (x86_64)
#  5. macOS (Apple silicon)
# Remove all the arguments from the url
# -------------------------------------------------------------------

GCC_VERSION=13.2.1

REMOTE_COMPRESSED_FILES="\
  https://developer.arm.com/-/media/Files/downloads/gnu/13.2.rel1/binrel/arm-gnu-toolchain-13.2.rel1-mingw-w64-i686-arm-none-eabi.zip
  https://developer.arm.com/-/media/Files/downloads/gnu/13.2.rel1/binrel/arm-gnu-toolchain-13.2.rel1-x86_64-arm-none-eabi.tar.xz
  https://developer.arm.com/-/media/Files/downloads/gnu/13.2.rel1/binrel/arm-gnu-toolchain-13.2.rel1-aarch64-arm-none-eabi.tar.xz
  https://developer.arm.com/-/media/Files/downloads/gnu/13.2.rel1/binrel/arm-gnu-toolchain-13.2.rel1-darwin-x86_64-arm-none-eabi.tar.xz
  https://developer.arm.com/-/media/Files/downloads/gnu/13.2.rel1/binrel/arm-gnu-toolchain-13.2.rel1-darwin-arm64-arm-none-eabi.tar.xz
"

# REMOTE_COMPRESSED_FILES="https://developer.arm.com/-/media/Files/downloads/gnu/13.2.rel1/binrel/arm-gnu-toolchain-13.2.rel1-x86_64-arm-none-eabi.tar.xz"

[ -d "tmp" ] || mkdir tmp
cd tmp
touch .nobackup

DST_DIRS="
./arm-none-eabi/bin
./bin
./lib
./libexec/gcc/arm-none-eabi/${GCC_VERSION}
./lib/gcc/arm-none-eabi/${GCC_VERSION}
"

EMPTY_FILES="
./lib/gcc/arm-none-eabi/${GCC_VERSION}/__empty_dir__
"

FILES="
./arm-none-eabi/bin/as
./bin/arm-none-eabi-gcc
./libexec/gcc/arm-none-eabi/${GCC_VERSION}/cc1
./libexec/gcc/arm-none-eabi/${GCC_VERSION}/collect2
"

SEPARATOR="# --------------------------------------------------------------------------------"

echo "${SEPARATOR}"

for REMOTE_COMPRESSED_FILE in ${REMOTE_COMPRESSED_FILES}; do
  COMPRESSED_FILE="$(basename ${REMOTE_COMPRESSED_FILE})"
  PLATFORM="$(echo ${COMPRESSED_FILE} | \
            sed -e 's/.*mingw-w64.*/win64/' \
                -e 's/.*[^n]-x86_64.*/linux64/' \
                -e 's/.*aarch64.*/linuxARM/' \
                -e 's/.*darwin-x86_64.*/macos/' \
                -e 's/.*darwin-arm64.*/macosARM/')"
  # 1. Download
  [ -f "${COMPRESSED_FILE}" ] || wget "${REMOTE_COMPRESSED_FILE}"
  # 2. Uncompress
  echo "Uncompressing ${COMPRESSED_FILE}..."
  if [ "${COMPRESSED_FILE##*.}" = "xz" ]; then
    # SRC_DIR="${COMPRESSED_FILE%%.tar.xz}"  # This is not true
    SRC_DIR="$(tar -tJf ${COMPRESSED_FILE} | head -n 1)"
    [ -d "${SRC_DIR}" ] || tar -xJf "${COMPRESSED_FILE}"
  elif [ "${COMPRESSED_FILE##*.}" = "zip" ]; then
    SRC_DIR="$(unzip -l ${COMPRESSED_FILE} | head -n 4 | tail -n 1 | awk '{print($4)}')"
    [ -d "${SRC_DIR}" ] || unzip "${COMPRESSED_FILE}"
  fi
  # 3. Creating directories for platform
  echo "Populating directories for platform '${PLATFORM}'..."
  for DIR in ${DST_DIRS}; do
    mkdir -p "${PLATFORM}/${DIR}"
  done
  echo "Copying files to platform '${PLATFORM}'..."
  for FILE in ${EMPTY_FILES}; do
    touch "${PLATFORM}/${FILE}"
  done
  for FILE in ${FILES}; do
    if [ "${PLATFORM}" = "win64" ]; then
      FILE="${FILE}.exe"
    fi
    cp "${SRC_DIR}/${FILE}" "${PLATFORM}/${FILE}"
  done
  echo "${SEPARATOR}"
done

echo
echo "The new configured platform files are on the 'tmp/' subdirectory."
