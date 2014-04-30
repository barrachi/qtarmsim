Install instructions for Qt ARMSim
==================================

Qt ARMSim requires the following applications:

  * [Python3](https://www.python.org/)
  * [PyQt4](http://www.riverbankcomputing.co.uk/software/pyqt/intro)
  
Once they are installed, you just have to execute the `qtarmsim.py`
file.


GNU/Linux
---------

The major GNU/Linux distributions provide packages for both Python3
and PyQt4. You should use your the package manager of your
distribution to install PyQt4 (the package manager will take care of
its dependencies and also install Python3 if it is not already
required).

For example, in Gentoo, you could use:

	emerge -av PyQt4


Windows
-------

Windows support has been tested with PyQt4 for Python 3.3. It should
work on newer versions, just make sure that you get the PyQt4 binary
package for the python version that you have installed.

To install Qt ARMSim dependencies on Windows, please follow the next
steps:

1. Download and install
[Python 3.3.x](https://www.python.org/downloads/windows/) (either 32
or 64 bits version). If you want to install a newer Python version,
just check that there is a PyQt binary package for that version.

2. Download and install the binary package of
[PyQt4 for Python 3.3](http://www.riverbankcomputing.co.uk/software/pyqt/download)
(either 32 or 64 bits, the same as the Python one).
