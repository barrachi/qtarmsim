1. Installing QtARMSim and its dependencies
-------------------------------------------

QtARMSim has the following dependencies:
`Python3 <https://www.python.org/>`_,
`Qt for Python (PySide2) <https://wiki.qt.io/Qt_for_Python>`_, and
ARMSim.

ARMSim, which is bundled with QtARMSim, has the next dependencies:
`Ruby <https://www.ruby-lang.org/en/>`_,
`Gosu <https://www.libgosu.org/>`_, and the
`GNU Gcc toolchain targeting the ARM EABI platform <http://gcc.gnu.org/>`_.

The next sections describe how to install QtARMSim, ARMSim, and their
dependencies on GNU/Linux, Windows and macOS.


1.1 Installing QtARMSim on GNU/Linux
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The major GNU/Linux distributions already provide packages for
``Python3`` and ``Ruby``. Therefore, the actual GNU/Linux
distribution package manager can be used to install this software. As
for the GNU Gcc, the required part of the GNU Gcc toolchain targeting
the ARM platform is bundled with QtARMSim. ``Gosu`` can be installed
using the Ruby package manager ``gem``. Finally, ``Qt for Python``
and ``QtARMSim`` can be installed using the ``pip3`` command provided by
``Python3``. (If after installing ``python3``, the ``pip3`` command is
not available, it can be manually installed by downloading `get-pip.py
<https://bootstrap.pypa.io/get-pip.py>`_, and
executing it: ``sudo python3 get-pip.py``.)

For example, on Ubuntu you can install QtARMSim, ARMSim and their
dependencies using::

   $ sudo apt-get install python3-pip ruby
   $ # See https://github.com/gosu/gosu/wiki/Getting-Started-on-Linux
   $ # for installing gosu dependencies
   $ sudo gem install gosu
   $ sudo pip3 install QtARMSim

On a Gentoo distribution, you can install QtARMSim, ARMSim and their
dependencies issuing (as root)::

   # emerge -av ruby
   # # See https://github.com/gosu/gosu/wiki/Getting-Started-on-Linux
   # # for installing gosu dependencies
   # gem install gosu
   # pip3 install --user QtARMSim

Please note that if you are installing QtARMSim on a system where PySide2
is already packaged, you can install the packaged version of PySide2 and
then install QtARMSim using the ``--no-deps`` option::

    # sudo pip3 install --no-deps QtARMSim

**Note about PySide2.**
Versions 5.12.0 and 5.12.1 of PySide2 introduced some changes that prevented
QtARMSim to work. Version 5.12.2 of PySide2 corrected these bugs.
If QtARMSim does not start, check which version of PySide2 is installed,
and if necessary, uninstall that version of PySide2 and install a valid version
(e.g., ``pip3 install PySide2==5.12.2``).


1.2 Installing QtARMSim on Windows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To install QtARMSim, ARMSim, and their dependencies on Windows,
please follow the next steps:

1. Download and install a 64 bits Python version, either the 3.5, 3.6 or the 3.7
   version, from the
   `Python releases for Windows <https://www.python.org/downloads/windows/>`_ page.
   Please check the '``Add Python 3.X to PATH``' option when installing it.

2. Download and install a 64 bits version of **Ruby with Devkit** from the
   `Ruby Installer for Windows page <http://rubyinstaller.org/>`_.
   During the installation process, make sure that the
   '``Add Ruby executables to your PATH``' option is selected.

3. Open a Windows console (executing either ``Windows PowerShell`` or
   ``cmd``, depending on your Windows version), and execute the commands
   indicated in the next steps.

4. Make sure that the ``shell``, ``e2mmap`` and ``sync`` Ruby modules are installed
   using the next ``gem`` command::

     PS C:\Users\Username> gem install shell e2mmap sync

5. Install the ``Gosu`` Ruby module using the ``gem`` command::

     PS C:\Users\Username> gem install gosu

6. Install QtARMSim using the ``pip3`` command::

     PS C:\Users\Username> pip3 install QtARMSim

**Note about Ruby.**
Starting with the 2.5 version of the Ruby installer for Windows, ``shell``, ``e2mmap``
and ``sync`` ruby modules are no longer bundled in. Therefore, they must be manually
installed, as stated in the previous instructions.

**Note about PySide2.**
Versions 5.12.0 and 5.12.1 of PySide2 introduced some changes that prevented
QtARMSim to work. Version 5.12.2 of PySide2 corrected these bugs.
If QtARMSim does not start, check which version of PySide2 is installed,
and if necessary, uninstall that version of PySide2 and install a valid version
(e.g., ``pip3 install PySide2==5.12.2``).


1.3 Installing QtARMSim on macOS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To install QtARMSim, ARMSim, and their dependencies on macOS,
please follow the next steps:

1. Install the `MacPorts package manager <https://www.macports.org/>`_.
   (If you use the `Homebrew package manager <http://brew.sh/>`_, please
   adapt the following instructions conveniently.)

2. Open a ``Terminal`` and execute the commands indicated in the next steps.

3. Install ``Python 3.7`` (or ``Python 3.8``) and ``pip``::

     $ sudo port install python37 py37-pip py37wheel
     $ sudo port select --set python3 python37
     $ sudo port select --set pip pip37

4. Install ``Ruby``::

     $ sudo port install ruby25
     $ sudo port select --set ruby ruby25

5. Install ``libsdl2`` and ``Gosu``::

     $ sudo port install libsdl2
     $ sudo gem install gosu

6. Install ``QtARMSim``::

     $ sudo -H pip install QtARMSim

   If there is no matching distribution of PySide2 for your version of macOS,
   you can install the MacPorts version of PySide2 and, after that, QtARMSim
   ignoring the PySide2 dependency::

    $ sudo port install py37-pyside2
    $ sudo -H pip install --no-deps QtARMSim

**Note about PySide2.**
Versions 5.12.0 and 5.12.1 of PySide2 introduced some changes that prevented
QtARMSim to work. Version 5.12.2 of PySide2 corrected these bugs.
If QtARMSim does not start, check which version of PySide2 is installed,
and if necessary, uninstall that version of PySide2 and install a valid version
(e.g., ``sudo pip install PySide2==5.12.2``).


1.4 Installing the ``GNU Gcc toolchain targeting the ARM EABI``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Starting with version 0.3.1 of QtARMSim, the required part of the ``GNU
Gcc toolchain targeting the ARM platform`` is already bundled with
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

Once a new ``GNU Gcc toolchain targeting the ARM platform`` is installed,
please configure the ``ARMSim Gcc Compiler`` QtARMSim option to point
to the new '``arm-none-eabi-gcc``' command.


2. Executing QtARMSim
---------------------

To execute QtARMSim, run the ``qtarmsim`` command, or click on the
corresponding entry on the applications menu (on GNU/Linux, under the
``Education:Science`` category).


3. Upgrading QtARMSim
---------------------

To upgrade an already installed QtARMSim, execute the following
command on GNU/Linux::

  $ sudo pip3 install --upgrade QtARMSim

On Windows::

  PS C:\Users\Username> pip3 install --upgrade QtARMSim

On macOS::

  sudo pip install --upgrade QtARMSim


4. Uninstalling QtARMSim
------------------------

To uninstall QtARMSim on GNU/Linux, execute the following command::

  $ sudo pip3 uninstall QtARMSim

On Windows::

  PS C:\Users\Username> pip3 uninstall QtARMSim

On macOS::

  sudo pip uninstall QtARMSim

