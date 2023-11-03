ABOUT THIS DIRECTORY
====================

This directory contains a reduced set of the GNU compiler toolchain
targeting the ARM EABI platform used by the Maple IDE distributed by
LeafLabs (http://leaflabs.com). It is distributed alongside with
QtARMSim to avoid the need of installing a complete GNU compiler
toolchain targeting the ARM EABI platform.

The original README files, describing the software license and where
to find the correspondent source code have been kept in case you are
interested on getting the whole version.

The complete set of files for Windows, Linux x86_64, Linux AARCH64,
macOS (x86_64), and macOS (Apple silicon) have been automatically
downloaded and pruned using the ``download_and_prune.sh`` script.

To reduce the required space, roughly from 1 GB to 30 MB each
platform, only those files that are required to perform the next
``gcc`` commands have been kept under each platform directory::

  arm-none-eabi-gcc -mcpu=cortex-m1 -mthumb -c test.s
  arm-none-eabi-gcc -S -mcpu=cortex-m1 -mthumb -c test.c

The ``strace`` command was used on GNU/Linux to find the files that
``arm-none-eabi-gcc`` required, and the paths it used to find each one
of them.

The older 32 bit versions for Windows and Linux were obtained from:
`<https://code.google.com/p/arduino/downloads/list>`_.
