Installing Qt ARMSim and its dependencies
-----------------------------------------

Qt ARMSim has the following dependencies:

  * `Python 3 <https://www.python.org/>`_.
  * `PySide
    <https://pyside.readthedocs.org/en/latest/>`_.

On the other hand, ARMSim has the next dependencies:

  * `Ruby <https://www.ruby-lang.org/en/>`_.
  * `GCC for ARM <http://gcc.gnu.org/>`_.

The next subsections describe how to install Qt ARMSim and its
dependencies on GNU/Linux and on Windows.


Installing Qt ARMSim on GNU/Linux
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The major GNU/Linux distributions provide packages for Python3,
PySide, and Ruby. Therefore, the GNU/Linux distribution package should
be used to install this software.

On the other hand, installing GCC for ARM can be achieved either by
installing a GCC for ARM package provided by the GNU/Linux
distribution at hand, building a cross-compiling toolchain, or by
extracting the ``gcc-arm-none-eabi`` ``tar.gz`` for linux32 from the
`Arduino download page
<https://code.google.com/p/arduino/downloads/list>`_ (beware that this
last option could not be appropriate on linux64 versions).

Finally, Qt ARMSim can be installed using the ``pip3`` command. (If
after installing ``python3``, ``pip3`` is not available, it can be
manually installed by downloading `get-pip.py
<https://raw.github.com/pypa/pip/master/contrib/get-pip.py>`_, and
executing the following command: ``sudo python3 get-pip.py``.)

For example, on Ubuntu you can install Qt ARMSim, ARMSim and their
dependencies using::

   $ sudo apt-get install python3-pyside python3-pip
   $ sudo apt-get install ruby2.0 gcc-arm-linux-gnueabi
   $ sudo pip3 install qtarmsim


On a Gentoo distribution, you can install Qt ARMSim, ARMSim and their
dependencies using (as root)::

   # emerge -av pyside ruby crossdev
   # echo "PORDIR_OVERLAY=/usr/local/portage" >> /etc/portage/make.conf
   # crossdev --target arm --ov-output /usr/local/portage
   # pip3 install qtarmsim


2.2 Installing Qt ARMSim on Windows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To install Qt ARMSim, ARMSim, and their dependencies on Windows,
please follow the next steps:

1. Download and install Python 3 from the `Python download page for
   windows <https://www.python.org/downloads/windows/>`_. During the
   installation process, you should say yest to '``Add Python to the
   Windows path``'.

2. Download and install Ruby 2 from `Ruby Installer for Windows page
   <https://www.ruby-lang.org/en/>`_. During the installation process,
   make sure to select the '``Add Ruby executables to you PATH``'
   option. (On Windows XP, Ruby 2 versions could fail to start. If
   this is the case, simply install a 1.9 version.)

3. Download GCC ARM cross compiler for Windows from the `Arduino
   download page <https://code.google.com/p/arduino/downloads/list>`_.
   Open the ``gcc-arm-none-eabi-x.y.y-win32.tar.gz`` file and extract
   the ``gcc-arm-none-eabi`` folder on any path you prefer. (Remember
   your decision, as you will have to configure Qt ARMSim to set the
   ``ARMSim GCC Compiler`` option to
   '``[PATH]\g++_arm_none_eabi\bin\arm-none-eabi-gcc.exe``', where
   [PATH] is the path you have used.)

4. Install PySide and Qt ARMSim using the ``pip3`` command. Open a
   Windows console (executing either ``Power Shell`` or ``cmd``,
   depending on your Windows version), and execute the next commands
   (assuming you installed Python 3.4)::

      C:\> cd C:\Python34
      C:\Python34> Scripts\pip3 install PySide qtarmsim


3. Executing Qt ARMSim
----------------------

Simply execute the ``qtarmsim`` command, or click on the corresponding
entry on the applications menu (on GNU/Linux, under the ``Education``
category).


4. Upgrading Qt ARMSim
----------------------

If you want to upgrade an already installed Qt ARMSim, simply execute
the following command on GNU/Linux::

  $ sudo pip3 install --upgrade qtarmsim
   
Or the equivalent command on Windows::

  C:\> pip3 install --upgrade qtarmsim


5. Uninstalling Qt ARMSim
-------------------------

To uninstall Qt ARMSim on GNU/Linux, execute the following command::

  $ sudo pip3 uninstall qtarmsim

Or the equivalent command on Windows::

  C:\> pip3 uninstall qtarmsim
