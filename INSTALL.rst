1. Installing QtARMSim
----------------------

In order to install QtARMSim, its dependencies should be installed first.

QtARMSim has the following dependencies: `Python3 <https://www.python.org/>`_,
`Qt for Python (PySide2) <https://wiki.qt.io/Qt_for_Python>`_, and ARMSim.

ARMSim, which is bundled with QtARMSim, has in turn the next dependencies:
`Ruby <https://www.ruby-lang.org/en/>`_ and the
`GNU GCC Arm toolchain <http://gcc.gnu.org/>`_.

The next subsections describe how to install QtARMSim and its dependencies on
GNU/Linux, Windows and macOS.


1.1 Installing QtARMSim on GNU/Linux
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The major GNU/Linux distributions already provide packages for ``Python3`` and
``Ruby``. Therefore, the provided package manager can be used to install them.
As for the GNU GCC, the required part of the GNU GCC Arm toolchain is bundled
with QtARMSim. Finally, ``Qt for Python`` and ``QtARMSim`` can be installed
using the ``pip3`` command provided by ``Python3``.

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
package(s) are installed, QtARMSim should be installed as follows:

.. code-block:: shell-session

    # sudo pip3 install --no-deps QtARMSim


1.2 Installing QtARMSim on Windows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To install QtARMSim on Windows please follow the next steps:

1. Download a 64 bits **Python executable installer** from
   `Python releases for Windows <https://www.python.org/downloads/windows/>`_.
   During the installation process, please select the ``Add Python 3.X to PATH``
   option.

2. Download a 64 bits **Ruby with Devkit** installer from
   `Ruby Installer for Windows <http://rubyinstaller.org/>`_.
   During the installation process, make sure that the
   ``Add Ruby executables to your PATH`` option is selected.

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

1. Download and install **Python 3** from the
   `Python downloads page <https://www.python.org/downloads/>`_.

2. Open a ``Terminal`` and execute the next command:

   .. code-block:: shell-session

     $ sudo -H pip3 install QtARMSim

After doing the previous steps, you should be able to execute QtARMSim by
typing ``qtarmsim`` on a **new** ``Terminal``.

Note: If an error message appeared when executing the ``pip3`` command saying that
there was no matching distribution of PySide2 for your macOS version, you can
instead install PySide2 with
`MacPorts <https://guide.macports.org/#installing.xcode>`_ and QtARMSim with no
dependencies using the following commands (MacPorts should be installed
previously):

.. code-block:: shell-session

  $ sudo port install py39-pyside2   # same version as the installed Python
  $ sudo -H pip3 install --no-deps QtARMSim


1.4 Installing the ``GNU GCC Arm toolchain`` (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Starting with version 0.3.1 of QtARMSim, the required part of the ``GNU GCC Arm
toolchain`` is already bundled with QtARMSim. So this step should only be done
if there is a problem with the bundled GNU GCC Arm toolchain (i.e., QtARMSim
is not able to assemble any source code).

In this case, another instance of GNU GCC Arm toolchain can be installed and used.

On GNU/Linux, this can be accomplished by installing a GNU GCC ARM package
provided by the GNU/Linux distribution being used, by building a cross-compiling
toolchain, or by extracting the ``gcc-arm-none-eabi-????-linux.tar.bz2``
file from the `GNU Arm Embedded Toolchain Downloads page
<https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain/gnu-rm/downloads>`_.

For example, on Ubuntu, this optional step can be achieved with:

.. code-block:: shell-session

    $ sudo apt install gcc-arm-linux-gnueabi

And on Gentoo with:

.. code-block:: shell-session

  # emerge -av crossdev
  # echo "PORTDIR_OVERLAY=/usr/local/portage" >> /etc/portage/make.conf
  # crossdev --target arm --ov-output /usr/local/portage

On Windows and macOS, to perform this optional step, download and execute the
respective Windows or macOS GNU GCC Arm toolchain package from the
`GNU Arm Embedded Toolchain Downloads page
<https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain/gnu-rm/downloads>`_.

Once a new ``GNU GCC Arm toolchain`` is installed, please
configure the ``ARMSim Gcc Compiler`` QtARMSim option to point to the new
``arm-none-eabi-gcc`` executable.


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

    sudo -H pip3 install --upgrade QtARMSim


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

    sudo -H pip3 uninstall QtARMSim


5. Installation related known issues
------------------------------------

If something goes wrong after installing QtARMSim, executing the ``qtarmsim``
command on a terminal could give some insight of what is the cause of the error.

The next known issues should not occur if the installation instructions are
followed to the letter. They are listed here just in case they can be of some
help when upgrading a previously installed version.

+ The 5.14 packaged version of PySide2 on Ubuntu 20.04 LTS does not properly
  display some icons and SVG images of QtARMSim. This can be solved by
  installing a newer version of PySide2 using ``pip``::

    $ sudo pip3 install PySide2

+ On Ubuntu 20.04 LTS, if the next error is shown when executing QtARMSim from
  a terminal::

    qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
    [...]

  It can be solved by installing the package ``libxcb-xinerama0``::

    $ sudo apt install libxcb-xinerama0

+ Starting with the 2.5 version of the Ruby installer, ``shell``, ``e2mmap``
  and ``sync`` ruby modules are no longer bundled in. Therefore, they must be
  manually installed using the ``gem`` command, as stated in the general
  instructions.

+ Versions 5.12.0 and 5.12.1 of PySide2 introduced some changes that prevented
  QtARMSim to work. Version 5.12.2 of PySide2 corrected these regressions.
