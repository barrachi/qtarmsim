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

The complete set of files were downloaded from:
`<https://code.google.com/p/arduino/downloads/list>`_. In particular
the next files were downloaded for each platform:

  * Linux32: ``gcc-arm-none-eabi-4.4.1-2010q1-188-linux32.tar.gz``
  * Win32:   ``gcc-arm-none-eabi-4.4.1-2010q1-188-win32.tar.gz``
  * MacOS:   ``gcc-arm-none-eabi-4.4.1-2010q1-188-macos.tar.gz``

To reduce the required space, from 230MB to 4.5MB, only those files
that are required to perform the next ``gcc`` command have been kept
under each platform directory::

  arm-none-eabi-gcc -mcpu=cortex-m1 -mthumb -c test.s

The ``strace`` command was used on GNU/Linux to find the required
files and the path they were looked for.
