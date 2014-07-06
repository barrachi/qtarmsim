Qt ARMSim
=========

Qt ARMSim is a graphical frontend to the ARMSim ARM simulator.

It should run on any platform supported by PyQt4, including GNU/Linux,
MacOS/X and Windows.


1. Dependencies
---------------

Qt ARMSim has the following dependencies:

  * `Python 3 <https://www.python.org/>`_.
  * `PyQt4 for Python 3
    <http://www.riverbankcomputing.co.uk/software/pyqt/intro>`_.
  * `QScintilla <http://www.riverbankcomputing.co.uk/software/qscintilla/intro>`_.

(Depending on the platform, QScintilla can be bundled with the PyQt4
installer.)

On the other hand, ARMSim has the next dependencies:

  * `Ruby <https://www.ruby-lang.org/en/>`_.
  * `GCC for ARM <http://gcc.gnu.org/>`_.


1.1 How to install the dependencies on GNU/Linux?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The GNU/Linux major distributions provide packages for Python3, PyQt4,
QScintilla (if not bundled with PyQt4), and Ruby. You should use the
package manager of your GNU/Linux distribution to install PyQt4 for
Python3 (the package manager will take care of its dependencies and
will also install Python3 if it is not already installed); QScintilla
with python bindings, if offered as a separate package; and Ruby.

For example, in Gentoo, you can use::

  # emerge -av PyQt4 qscintilla-python ruby

Installing GCC for ARM can be achieved either by building a
cross-compiling toolchain, installing a GCC for ARM package provided
by your distribution, or by extracting the ``gcc-arm-none-eabi``
``tar.gz`` for linux32 or linux64 from the `Arduino download page
<https://code.google.com/p/arduino/downloads/list>`_.

For example, on Gentoo, building the cross-compiling toolchain
involves the following commands::

  # emerge -av crossdev
  # crossdev --target arm --ov-output /usr/local/portage

On Ubuntu, the ``gcc-arm-linux-gnueabi`` package should be installed.


1.2 How to install the dependencies on Windows?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Windows support has been tested with PyQt4 for Python |~| 3.4. It should
work on newer versions, just make sure that you get the PyQt4 binary
package for the very same Python version you install.

To install Qt ARMSim and ARMSim dependencies on Windows, please
follow the next steps:

1. Check which binaries versions of PyQt4 are available on the `PyQt4
   download page
   <http://www.riverbankcomputing.co.uk/software/pyqt/download>`_. Select
   one version of PyQt4 that works with Python3 and Qt4. Write down
   the version of Python for which it has been compiled. The Python
   version is coded on the installer file name. For example, the file
   ``PyQt4-4.11.1-gpl-Py3.4-Qt4.8.6-x64.exe`` provides an installer
   for PyQt4 for Python |~| 3.4 and Qt |~| 4.8.6.  What is important
   in this step is to write down that the version of Python should be
   the |~| 3.4. The 3.4 |~| version, not any other version, not even a
   minor revision like |~| 3.4.1. Download now the chosen installer
   for PyQt4, but do not install it yet.

2. Download and install Python3 from the `Python download page for
   windows <https://www.python.org/downloads/windows/>`_ (you should
   search for the exact version required by PyQt4 on the previous
   step).  During the installation, it is convenient to mark the
   option that adds Python to the Windows path.

3. Install the PyQt4 package you downloaded on step 1.

4. Download and install Ruby from `Ruby Installer for Windows
   <https://www.ruby-lang.org/en/>`_.  Install a |~| 1.9 version (no a
   |~| 2 version). Please, make sure to select the ``Add Ruby
   executables to you PATH`` option.

5. Download GCC ARM cross compiler for Windows from the `Arduino
   download page <https://code.google.com/p/arduino/downloads/list>`_.
   Open the ``gcc-arm-none-eabi-x.y.y-win32.tar.gz`` file and extract
   its contents on any folder you choose. (Later you will configure Qt
   |~| ARMSim to use the
   ``g++_arm_none_eabi\bin\arm-none-eabi-gcc.exe`` as the ARMSim GCC
   Compiler.)



2. Installing Qt ARMSim
-----------------------

Qt ARMSim can be automatically installed using pip (a tool for
installing Python packages), or it can be manually installed.
Next section shows how to install Qt |~| ARMSim using `pip`,
which is the recommended method. Section |~| 2.2 shows how to
install it manually. 


2.1 Using pip (recommended method)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If pip is not installed in your system, download `get-pip.py
<https://raw.github.com/pypa/pip/master/contrib/get-pip.py>`_, and
execute::

  # python3 get-pip.py

Once ``pip`` is installed, you can install Qt ARMSim with::

  # pip3 install --pre qtarmsim

If you execute the previous commands as root, they will be installed
system wide. If not, they will be installed only for the current user.


2.2 Manual installation
^^^^^^^^^^^^^^^^^^^^^^^

Download the last ``qtarmsim-x.y.z.tar.gz`` file from
`<https://pypi.python.org/pypi/qtarmsim/>`_, uncompress it, and enter in
the ``qtarmsim-x.y.z`` directory::

	$ tar -xzf qtarmsim-x.y.z.tar.gz
	$ cd qtarmsim-x.y.z

Once there, you can install Qt ARMSim system wide or on a user
basis. To install it system wide, you should use the following command
as ``root``::

	# python3 setup.py install

If you prefer to install Qt ARMSim on a user basis, you should execute
the following command::

	$ python3 setup.py install --user



3. Executing Qt ARMSim
----------------------

If Qt ARMSim has been installed system wide, you can simply execute
the ``qtarmsim`` command, as it should have been installed on a directory
that should be on the system path.

Otherwise, ``qtarmsim`` will be on a user directory. On GNU/Linux, it
will be on ``~/.local/bin/``. On Windows, it will be on
``C:\\Users\YourUser\AppData\Roaming\Python\Scripts\``. You can add
that directory to your path if you want.



.. |~| unicode:: U+00A0 .. non-breaking space
   :trim:
