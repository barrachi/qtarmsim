Changelog
---------

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

- Last revision of the first functional QtARMSim version. This version
  was used on the first semester of an introductory course on Computer
  Architecture at Jaume I University. Last version with PyQt and
  QScintilla dependencies.
