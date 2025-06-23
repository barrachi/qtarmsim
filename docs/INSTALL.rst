1. Installing QtARMSim
----------------------

For installing QtARMSim, you need to also install its dependencies.

QtARMSim depends on:

- `Python 3 <https://www.python.org/>`_
- `Qt for Python (PySide6) <https://wiki.qt.io/Qt_for_Python>`_
- ARMSim

ARMSim, which is bundled with QtARMSim, requires:

- `Ruby <https://www.ruby-lang.org/en/>`_
- `GNU GCC Arm toolchain <http://gcc.gnu.org/>`_

The following sections explain how to install QtARMSim and its
dependencies on **GNU/Linux**, **Windows**, and **macOS**.


1.1 Installing QtARMSim on GNU/Linux
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Most GNU/Linux distributions provide packages for ``Python3`` and
``Ruby``, which therefore can be installed via the system’s package manager. The
required portion of the ``GNU GCC Arm toolchain`` is bundled with
QtARMSim (so this part does not have to be manually installed). Finally,
``QtARMSim`` (and ``PySide6``) can be installed using ``pip3``.

**Example: Installation on Ubuntu**

First, install the next required packages:

.. code-block:: shell-session

    $ sudo apt install ruby
    $ sudo gem install shell e2mmap sync
    $ sudo apt install pipx
    $ pipx ensurepath

Then, for a single-user installation:

.. code-block:: shell-session

    $ pipx install qtarmsim

Or for a system-wide installation:

.. code-block:: shell-session

    $ sudo pipx ensurepath --global
    $ sudo pipx install --global qtarmsim

*Note:* If the ``--global`` option is not recognized, consult ``pipx``
documentation or ask ChatGPT for a workaround. This drawback can be solved
with something similar to:

.. code-block:: shell-session

    $ sudo pipx install pipx  # Installs a newer version of pipx on the root home
    $ sudo apt remove pipx    # Removes the older system pipx
    $ sudo bash
    # ~/.local/share/pipx/venvs/pipx/bn/pipx install pipx --global
    # ~/.local/share/pipx/venvs/pipx/bn/pipx ensurepath --global
    # exit
    $ sudo pipx install --global qtarmsim  # The newer version should support --global


**Example: Installation on Gentoo**

.. code-block:: shell-session

    $ sudo emerge -av pip ruby
    $ sudo gem install shell e2mmap sync
    $ pip3 install --user qtarmsim
    $ post_install_qtarmsim


1.2 Installing QtARMSim on Windows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Follow these steps to install QtARMSim on Windows:

1. Download a 64-bit Python installer from the `Windows official
   Python website <https://www.python.org/downloads/windows/>`_ (or from the MS Windows store). Make
   sure to select **"Add python.exe to PATH"** during
   installation. **Select the 3.12 Python version** (which is supported
   by PySide6).

2. Download a 64-bit Ruby installer (with Devkit) from the `Ruby
   Installer website <http://rubyinstaller.org/>`_. Ensure **"Add Ruby
   executables to your PATH"** is selected.

3. Open a console (``cmd`` or ``PowerShell``) and run the following
   commands:



   .. code-block:: powershell

       gem install shell e2mmap sync   # to install the required Ruby modules
       pip3 install qtarmsim           # to install qtarmsim
       post_install_qtarmsim           # to create start menu entry and shortcuts

1.3 Installing QtARMSim on macOS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Follow these steps to install QtARMSim on macOS:

1. Install Python 3 from the `official Python website
   <https://www.python.org/downloads/>`_ (or from the macOS store). Make sure you
   install a python version supported by PySide6 (check the *python compatibility
   matrix* in `Qt for Python <https://wiki.qt.io/Qt_for_Python>`_).

2. Open a terminal and run:

   .. code-block:: shell-session

       $ sudo -H pip3 install qtarmsim
       $ sudo post_install_qtarmsim

After installation, you can run QtARMSim by typing ``qtarmsim`` in a
**new** terminal session.

**Note:** If you encounter an error stating that PySide6 is not
available for your macOS version, you can install PySide6 via
`MacPorts <https://guide.macports.org/#installing.xcode>`_ and then
install QtARMSim without Python dependencies:

.. code-block:: shell-session

    $ sudo port install py311-pyside6   # Replace 'py311' with your Python version
    $ sudo -H pip3 install --no-deps qtarmsim
    $ sudo post_install_qtarmsim


1.4 Optional: installing the GNU GCC Arm Toolchain
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Starting with QtARMSim version 0.3.1, the required components of the
``GNU GCC Arm toolchain`` are bundled with QtARMSim. Manual installation
is only needed if the bundled toolchain does not work properly.

**On GNU/Linux**

You can install the ``GNU GCC Arm toolchain`` via your distribution’s
package manager or by downloading it from the `GNU Arm Embedded
Toolchain Downloads page
<https://developer.arm.com/Tools%20and%20Software/GNU%20Toolchain>`_.

**Example (Ubuntu):**

.. code-block:: shell-session

    $ sudo apt install gcc-arm-linux-gnueabi

**Example (Gentoo):**

.. code-block:: shell-session

    # emerge -av crossdev
    # echo "PORTDIR_OVERLAY=/usr/local/portage" >> /etc/portage/make.conf
    # crossdev --target arm --ov-output /usr/local/portage

**On Windows and macOS**

Download and install the appropriate package from the `GNU Arm
Embedded Toolchain Downloads page
<https://developer.arm.com/Tools%20and%20Software/GNU%20Toolchain>`_.

Once a new ``GNU GCC Arm toolchain`` has been installed, you must configure
the **ARMSim Gcc Compiler** option in QtARMSim preferences to point to the
new ``arm-none-eabi-gcc`` executable.


2. Running QtARMSim
-------------------

To run QtARMSim, execute the ``qtarmsim`` command or launch it from
the applications menu (on GNU/Linux, under the **Education:Science**
category).


3. Upgrading QtARMSim
---------------------

To upgrade QtARMSim to its latest version, use the following commands:

- **On GNU/Linux:**

  Depending or your method of installation (``pix``):

  .. code-block:: shell-session

      $ sudo pipx upgrade qtarmsim

  or (``pip``)::

  .. code-block:: shell-session

      $ sudo pip3 install --upgrade qtarmsim


- **On Windows:**

  .. code-block:: powershell

      pip3 install --upgrade qtarmsim

- **On macOS:**

  .. code-block:: shell-session

      $ sudo -H pip3 install --upgrade qtarmsim


4. Uninstalling QtARMSim
------------------------

To uninstall QtARMSim, run:

- **On GNU/Linux:**

  .. code-block:: shell-session

      $ sudo pipx uninstall qtarmsim

  or

  .. code-block:: shell-session

      $ sudo pipx uninstall qtarmsim


- **On Windows:**

  .. code-block:: powershell

      pip3 uninstall qtarmsim

- **On macOS:**

  .. code-block:: shell-session

      $ sudo -H pip3 uninstall qtarmsim


5. Known installation issues
----------------------------

If QtARMSim does not start correctly, try running ``qtarmsim`` from a
terminal to inspect any error messages.

**Common issues and solutions:**

- **Issue:** PySide6 installation fails

  **Solution:**

  PySide6 installation problems usually are related to which python versions it supports.
  This can be checked in `<https://pypi.org/project/PySide6/>`_ (**requires** filed under
  Meta section) or checking the *python compatibility matrix* in
  `Qt for Python <https://wiki.qt.io/Qt_for_Python>`_. If you are using a version of Python not
  supported by the last version of PySide6, install a supported python version.

  Another option is to check if your operating system provides its own PySide6
  packages. If this is the case, you can install them and then install QtARMSim
  without pulling its dependencies:

  .. code-block:: shell-session

      # sudo pip3 install --no-deps qtarmsim

- **Issue:** On Ubuntu 20.04 LTS, the PySide2 5.14 package does not
  display some icons or SVGs properly.

  **Solution:**

  .. code-block:: shell-session

      $ sudo pip3 install pyside2

- **Issue:** The following error appears when launching QtARMSim::

      qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in ""
      even though it was found.

  **Solution:**

  .. code-block:: shell-session

      $ sudo apt install libxcb-xinerama0

- **Issue:** Since Ruby installer version 2.5, the ``shell``,
  ``e2mmap``, and ``sync`` modules are no longer bundled.

  **Solution:** Manually install these modules using the ``gem``
  command as shown in the Windows installation instructions.

- **Issue:** PySide2 versions 5.12.0 and 5.12.1 introduced regressions
  that prevent QtARMSim from working properly.

  **Solution:** Upgrade to PySide2 version 5.12.2 or later.

