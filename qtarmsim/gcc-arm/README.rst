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

The complete set of files for Linux32, Win32, and MacOS were
downloaded from:
`<https://code.google.com/p/arduino/downloads/list>`_. In particular
the next files were downloaded for each platform:

  * Linux32: ``gcc-arm-none-eabi-4.4.1-2010q1-188-linux32.tar.gz``
  * Win32:   ``gcc-arm-none-eabi-4.4.1-2010q1-188-win32.tar.gz``
  * MacOS:   ``gcc-arm-none-eabi-4.4.1-2010q1-188-macos.tar.gz``

On the other hand, the full Linux64 version was obtained by
downloading the ``gcc-arm-none-eabi-4_9-2015q3-20150921-src.tar.bz2``
file from https://launchpad.net/gcc-arm-embedded/ and following the
instructions for building the toolchain. The compilation was made on a
Gentoo 64 bit machine.

To reduce the required space, roughly from 150MB to 2.5MB each
platform, only those files that are required to perform the next
``gcc`` command have been kept under each platform directory::

  arm-none-eabi-gcc -mcpu=cortex-m1 -mthumb -c test.s

The ``strace`` command was used on GNU/Linux to find the files that
``arm-none-eabi-gcc`` required, and the paths it used to find each one
of them.
