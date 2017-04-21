1. Installing QtARMSim and its dependencies
-------------------------------------------

QtARMSim has the following dependencies: `Python3
<https://www.python.org/>`_, `PySide
<https://pyside.readthedocs.org/en/latest/>`_, and ARMSim. On the
other hand, ARMSim, which is bundled with QtARMSim, has the next
dependencies: `Ruby <https://www.ruby-lang.org/en/>`_ and the `GNU Gcc
toolchain targeting the ARM EABI platform <http://gcc.gnu.org/>`_. The
next subsections describe how to install QtARMSim, ARMSim, and their
dependencies on GNU/Linux, Windows and Mac OS X.


1.1 Installing QtARMSim on GNU/Linux
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The major GNU/Linux distributions already provide packages for
``Python3``, ``PySide``, and ``Ruby``. Therefore, the actual GNU/Linux
distribution package manager can be used to install this software. As
for the GNU Gcc, the required part of the GNU Gcc toolchain targeting
the ARM platform is already bundled with QtARMSim. Finally, QtARMSim
itself can be installed using the ``pip3`` command. (If after
installing ``python3``, the ``pip3`` command is not available, it can
be manually installed by saving `get-pip.py
<https://bootstrap.pypa.io/get-pip.py>`_, and
executing: ``sudo python3 get-pip.py``.)

For example, on Ubuntu you can install QtARMSim, ARMSim and their
dependencies using::

   $ sudo apt-get install python3-pyside python3-pip
   $ sudo apt-get install ruby
   $ sudo pip3 install qtarmsim

On a Gentoo distribution, you can install QtARMSim, ARMSim and their
dependencies issuing (as root)::

   # emerge -av pyside ruby
   # pip3 install qtarmsim


1.2 Installing QtARMSim on Windows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To install QtARMSim, ARMSim, and their dependencies on Windows,
please follow the next steps:

1. Download and install a 32 bits Python 3.4 version from the `Python
   download page for windows
   <https://www.python.org/downloads/windows/>`_. During the
   installation process, you must say yest to '``Add python.exe to
   Path``'. **Be sure that you do NOT install**:

   - A Python 3.5 version, as Python 3.5, at least 3.5.1rc1, does
     not install the ``pip`` command and PySide does not provide
     binaries for Python 3.5 yet.
   - A 64 bits Python, because PySide does not provide Windows
     binaries for 64bits Python yet.

2. Download and install Ruby from `Ruby Installer for Windows page
   <http://rubyinstaller.org/>`_. During the installation process,
   make sure to select the '``Add Ruby executables to your PATH``'
   option.

3. Install PySide using the ``pip3`` command. Open a Windows console
   (executing either ``Power Shell`` or ``cmd``, depending on your
   Windows version), and execute the next commands (assuming you
   installed Python 3.4 for all the users on your system, if not,
   change the directory to something like
   ``C:\Users\YOURUSERNAME\AppData\Local\Programs\Python\Python34``,
   where ``YOURUSERNAME`` is the name of your user)::

     C:\> cd C:\Python34
     C:\Python34> Scripts\pip3.exe install PySide

   If the latest version of PySide is not automatically installed,
   i.e., if there is no binary version available for your system,
   install the 1.2.2 version of PySide with::

     C:\Python34> Scripts\pip3 install PySide==1.2.2

4. Install QtARMSim using the ``pip3`` command. On the same directory
   of the previous step, run the following command::

     C:\Python34> Scripts\pip3.exe install QtARMSim

After installing QtARMSim, its executable will be at: ``C:\Python34\Scripts\qtarmsim.exe``.

QtARMSim python source code under: ``C:\Python34\Lib\site-packages\qtarmsim\``.

And the ARMSim ruby source code under: ``C:\Python34\Lib\site-packages\qtarmsim\armsim``.


1.3 Installing QtARMSim on Mac OS X
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To install QtARMSim, ARMSim, and their dependencies on Mac OS X,
please follow the next steps:

1. Install the MacPorts package manager (https://www.macports.org/) or
   the Homebrew package manager (http://brew.sh/). The next instructions
   are for the MacPorts package manager.

2. Install Python 3.4::

     sudo port install python34

3. Install Ruby::

     sudo port install ruby23

4. Install PySide::

     sudo port install py34-pyside

5. Install QtARMSim::

     sudo pip3 install QtARMSim


1.4 Installing the GNU Gcc toolchain targeting the ARM EABI
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Starting with version 0.3.1 of QtARMSim, the required part of the GNU
Gcc toolchain targeting the ARM platform is already bundled with
QtARMSim. So this step is no longer required, unless there is some
problem with the bundled GNU Gcc toolchain (for example, if QtARMSim
does not assemble a given source code). In this case, another
instance of GNU Gcc can be installed and used.

On GNU/Linux, this can be accomplished by installing a GNU Gcc for ARM
package provided by the GNU/Linux distribution being used, by building
a cross-compiling toolchain, or by extracting the
``gcc-arm-none-eabi`` ``tar.gz`` for linux32 from the `Arduino
download page
<https://code.google.com/p/arduino/downloads/list>`_. For example, on
Ubuntu, this optional step can be achieved with::

  $ sudo apt-get install gcc-arm-linux-gnueabi

And on Gentoo with::

  # emerge -av crossdev
  # echo "PORDIR_OVERLAY=/usr/local/portage" >> /etc/portage/make.conf
  # crossdev --target arm --ov-output /usr/local/portage

On Windows, to perform this optional step, download the GNU Gcc ARM
cross compiler for Windows from the `Arduino download page
<https://code.google.com/p/arduino/downloads/list>`_.  Open the
``gcc-arm-none-eabi-x.y.y-win32.tar.gz`` file, and extract the
``gcc-arm-none-eabi`` folder on any path you prefer.


Once a new GNU Gcc toolchain targeting the ARM platform is installed,
please configure QtARMSim to point the ``ARMSim Gcc Compiler`` option
to the new '``arm-none-eabi-gcc``' command.


2. Executing QtARMSim
---------------------

To execute QtARMSim, run the ``qtarmsim`` command, or click on the
corresponding entry on the applications menu (on GNU/Linux, under the
``Education`` category).


3. Upgrading QtARMSim
---------------------

To upgrade an already installed QtARMSim, execute the following
command on GNU/Linux::

  $ sudo pip3 install --upgrade qtarmsim

On Windows::

  C:\Python34> Scripts\pip3.exe install --upgrade qtarmsim

On Mac OS X::

  sudo pip3 install --upgrade qtarmsim


4. Uninstalling QtARMSim
------------------------

To uninstall QtARMSim on GNU/Linux, execute the following command::

  $ sudo pip3 uninstall qtarmsim

On Windows::

  C:\Python34> Scripts\pip3.exe uninstall qtarmsim

On Mac OS X::

  sudo pip3 uninstall qtarmsim
