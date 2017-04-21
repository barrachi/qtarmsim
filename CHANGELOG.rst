Changelog
---------

0.3.12 (2017-04-21)
^^^^^^^^^^^^^^^^^^^

- Changed the icon set to the KDE Breeze one.
- LCD Display not rescaling correctly on some desktop environments fixed.
- LCD display can now be zoomed with CTRL+mouse wheel.
- Editors and panels now honor the system default point size.
- Now the menu bar is displayed on the system menu bar on Mac OS X.


0.3.11 (2016-10-30)
^^^^^^^^^^^^^^^^^^^

- The Edit menu actions have been implemented.
- Settings values are now automatically stripped to avoid errors due to
  misplaced spaces.
- ARMSim: updated firmware to correct a bug on sdivide subroutine.


0.3.10 (2016-09-19)
^^^^^^^^^^^^^^^^^^^

- ARMSim: updated firmware to provide a signed division subroutine.


0.3.8 (2016-09-19)
^^^^^^^^^^^^^^^^^^

- Bug corrected: waiting spinner occluded File and Edit menus.


0.3.7 (2016-09-18)
^^^^^^^^^^^^^^^^^^

- Added firmware ROM that provides, among others, functions to display
  strings and numbers on the LCD display. The new memory organization
  consists of two ROM blocks and two RAM blocks. The first ROM block
  is filled with the assembled user code. The second ROM, with the
  firmware machine code. The first RAM can be used to store the user
  program data. The second RAM is used by the LCD display.
- The graphical interface now uses a thread to retrieve the memory
  contents and the disassembled code from the two ROM blocks.
- The regular expressions used to highlight the code on the editors
  have been optimized to increase the highlighting process speed.


0.3.5 (2016-09-12)
^^^^^^^^^^^^^^^^^^

- Improved the Mac OS X compatibility and added installation
  instructions for this platform.
- Changed the minimum size of the code editor container to accommodate
  lower resolution screens.
- ARMSim: (i) LSL result is now bounded to 32 bits; (ii) command
  redirection is performed explicitly to avoid an error on newer
  Windows versions; and (iii) the method used to compare whether
  memory blocks where not defined has been changed to avoid errors on
  Ruby with version >= 2.3.


0.3.4 (2016-01-21)
^^^^^^^^^^^^^^^^^^

- Added a memory dump dock widget that allows to see and edit the
  memory at byte level. It also shows the ASCII equivalent of each
  byte.
- Added a LCD display dock widget that provides a simple output
  system. It has a size of 32x6 and each character is mapped to a
  memory position starting a 0x20070000.


0.3.3 (2015-11-28)
^^^^^^^^^^^^^^^^^^

- Added a visual indication of which instructions have already been
  executed on the left margin of the ARMSim panel.
- Added automatic scroll on simulation mode in order to keep the next
  line that is going to be executed visible.
- Improved the automatic selection of a mono spaced font (previously
  selected font used ligatures).
- Fixed an error on the Preferences Dialog which prevented to select
  the ``ARMSim directory`` and the ``Gcc ARM command line`` using the
  corresponding directory/file selector dialogs.
- ARMSim. Fixed the simulation of shift instructions: only the 8 least
  significant bits are now used to obtain the shift amount.
- ARMSim. Fixed the behaviour when memory outside the current memory
  map is accessed: each wrong access now raises a memory access error.
- Bundled a reduced set of the GNU compiler toolchain. To reduce the
  package size, only those files actually required to assemble an
  assembly source code have been included.


0.3.0 (2015-06-09)
^^^^^^^^^^^^^^^^^^

- Migrated from PyQt to PySide to allow a simpler installation of
  QtARMSim.
- Developed a new source code editor based on QPlainTextEdit, though
  removing the prior QScintilla dependency, which allows a simpler
  installation of QtARMSim.
- Improved the ARM Assembler syntax highlighting.


0.2.7 (2014-11-05)
^^^^^^^^^^^^^^^^^^

- Last revision of the first functional QtARMSim implementation. This
  implementation  was used on the first semester of an introductory
  course on Computer Architecture at Jaume I University. This is the
  last version of that implementation, which used PyQt and QScintilla.
