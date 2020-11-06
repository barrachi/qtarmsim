1. Installing QtARMSim
----------------------

In order to install QtARMSim, its dependencies should be installed first.

QtARMSim has the following dependencies: `Python3 <https://www.python.org/>`_,
`Qt for Python (PySide2) <https://wiki.qt.io/Qt_for_Python>`_, and ARMSim.

ARMSim, which is bundled with QtARMSim, has in turn the next dependencies: `Ruby
<https://www.ruby-lang.org/en/>`_ and the `GNU Gcc toolchain for the ARM EABI
platform <http://gcc.gnu.org/>`_.

The next subsections describe how to install QtARMSim and its dependencies on
GNU/Linux, Windows and macOS.


1.1 Installing QtARMSim on GNU/Linux
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The major GNU/Linux distributions already provide packages for ``Python3`` and
``Ruby``. Therefore, the actual GNU/Linux distribution package manager can be
used to install these. As for the GNU Gcc, the required part of the GNU Gcc
toolchain for the ARM platform is bundled with QtARMSim. Finally, ``Qt for
Python`` and ``QtARMSim`` can be installed using the ``pip3`` command provided
by ``Python3``.

For example, on Ubuntu you can install QtARMSim using:

.. code-block:: shell-session

    $ sudo apt install python3-pip ruby libxcb-xinerama0
    $ sudo gem install shell e2mmap sync
    $ sudo pip3 install QtARMSim

On a Gentoo distribution, you can install QtARMSim issuing (as root):

.. code-block:: shell-session

    # emerge -av pip ruby
    # pip3 install --user QtARMSim

If you are installing QtARMSim on a system where PySide2 is already provided as
a package, you can install the packaged version of PySide2 and then install
QtARMSim using the ``--no-deps`` option (be aware that the packaged version can
be not so to up to date as the one obtained from pip). Once the PySide2
package(s) are installed, QtARMSim can be installed as follows:

.. code-block:: shell-session

    # sudo pip3 install --no-deps QtARMSim


1.2 Installing QtARMSim on Windows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To install QtARMSim on Windows please follow the next steps:

1. Download a 64 bits **Python executable installer** from
   `Python releases for Windows <https://www.python.org/downloads/windows/>`_.
   During the installation process, please check the '``Add Python 3.X to PATH``'
   option.

2. Download a 64 bits **Ruby with Devkit** installer from
   `Ruby Installer for Windows <http://rubyinstaller.org/>`_.
   During the installation process, make sure that the
   '``Add Ruby executables to your PATH``' option is selected.

3. Open a Windows console (executing either ``Windows PowerShell`` or
   ``cmd``, depending on your Windows version), and execute the commands
   indicated in the next steps.

   3.1. Install the ``shell``, ``e2mmap`` and ``sync`` Ruby modules with:

   .. code-block:: powershell

     PS C:\Users\Username> gem install shell e2mmap sync

   3.2. Install QtARMSim using the ``pip3`` command:

   .. code-block:: powershell

     PS C:\Users\Username> pip3 install QtARMSim



1.3 Installing QtARMSim on macOS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To install QtARMSim on macOS, please follow the next steps:

1. Install the `MacPorts package manager <https://www.macports.org/>`_.
   (If you use the `Homebrew package manager <http://brew.sh/>`_, please
   adapt the following instructions conveniently.)

2. Open a ``Terminal`` and execute the commands indicated in the next steps.

   2.1. Install a ``Python`` version (for example, ``Python 3.8``) and ``pip``:

   .. code-block:: shell-session

     $ sudo port install python38 py38-pip py38wheel
     $ sudo port select --set python3 python38
     $ sudo port select --set pip pip38

   2.2. Install a ``Ruby`` version:

   .. code-block:: shell-session

     $ sudo port install ruby25
     $ sudo port select --set ruby ruby25

   2.3. Install ``libsdl2`` and ``Gosu``:

   .. code-block:: shell-session

     $ sudo port install libsdl2
     $ sudo gem install gosu

   2.4 Install ``QtARMSim``:

   .. code-block:: shell-session

     $ sudo -H pip install QtARMSim

   If when executing the previous command it says that there is no matching
   distribution of PySide2 for your macOS version, you can instead install the
   MacPorts version of PySide2 and, after that, install QtARMSim without its
   dependencies:

   .. code-block:: shell-session

    $ sudo port install py38-pyside2
    $ sudo -H pip install --no-deps QtARMSim


1.4 Installing the ``GNU Gcc toolchain targeting the ARM EABI`` (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Starting with version 0.3.1 of QtARMSim, the required part of the ``GNU Gcc
toolchain targeting the ARM platform`` is already bundled with QtARMSim. So this
step is no longer required, unless there is some problem with the bundled GNU
Gcc toolchain (for example, if QtARMSim does not assemble a given source code).
In this case, another instance of GNU Gcc can be installed and used.

On GNU/Linux, this can be accomplished by installing a GNU Gcc for ARM package
provided by the GNU/Linux distribution being used, by building a cross-compiling
toolchain, or by extracting the ``gcc-arm-none-eabi`` ``tar.gz`` for linux32
from the `Arduino download page
<https://code.google.com/p/arduino/downloads/list>`_. For example, on Ubuntu,
this optional step can be achieved with:

.. code-block:: shell-session

    $ sudo apt install gcc-arm-linux-gnueabi

And on Gentoo with:

.. code-block:: shell-session

  # emerge -av crossdev
  # echo "PORTDIR_OVERLAY=/usr/local/portage" >> /etc/portage/make.conf
  # crossdev --target arm --ov-output /usr/local/portage

On Windows, to perform this optional step, download the GNU Gcc ARM cross
compiler for Windows from the `Arduino download page
<https://code.google.com/p/arduino/downloads/list>`_.  Open the
``gcc-arm-none-eabi-x.y.y-win32.tar.gz`` file, and extract the
``gcc-arm-none-eabi`` folder on any path you prefer.

Once a new ``GNU Gcc toolchain targeting the ARM platform`` is installed, please
configure the ``ARMSim Gcc Compiler`` QtARMSim option to point to the new
'``arm-none-eabi-gcc``' command.


2. Executing QtARMSim
---------------------

To execute QtARMSim, run the ``qtarmsim`` command, or click on the corresponding
entry on the applications menu (on GNU/Linux, under the ``Education:Science``
category).


3. Upgrading QtARMSim
---------------------

To upgrade an already installed version of QtARMSim, execute the following
command on GNU/Linux:

.. code-block:: shell-session

    $ sudo pip3 install --upgrade QtARMSim

On Windows:

.. code-block:: powershell

    PS C:\Users\Username> pip3 install --upgrade QtARMSim

On macOS:

.. code-block:: shell-session

    sudo -H pip install --upgrade QtARMSim


4. Uninstalling QtARMSim
------------------------

To uninstall QtARMSim on GNU/Linux, execute the following command:

.. code-block:: shell-session

    $ sudo pip3 uninstall QtARMSim

On Windows:

.. code-block:: powershell

    PS C:\Users\Username> pip3 uninstall QtARMSim

On macOS:

.. code-block:: shell-session

    sudo -H pip uninstall QtARMSim


5. Installation related known issues
------------------------------------

If something goes wrong after installing QtARMSim, executing the ``qtarmsim``
command on a terminal could give some insight of what is the cause of the error.

The next known issues should not occur if the installation instructions are
followed to the letter. They are listed here just in case they can be of some
help when upgrading a previously installed version.

+ The 5.14 packaged version of PySide2 on Ubuntu 20.04 LTS does not properly
  display some icons and SVG images of QtARMSim. This can be solved by
  installing a newer version PySide2 using ``pip``::

    $ sudo pip3 install PySide2

+ On Ubuntu 20.04 LTS, if the next error is shown when executing QtARMSim from
  a terminal::

    qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
    [...]

  It can be solved by installing the package ``libxcb-xinerama0``::

    $ sudo apt install libxcb-xinerama0

+ Starting with the 2.5 version of the Ruby installer, ``shell``, ``e2mmap``
  and ``sync`` ruby modules are no longer bundled in. Therefore, they must be
  manually installed using the ``gem`` command.

+ Versions 5.12.0 and 5.12.1 of PySide2 introduced some changes that prevented
  QtARMSim to work. Version 5.12.2 of PySide2 corrected these regressions.
