1. Running and installing QtARMSim
----------------------------------

Starting with version 2.0.0, it is not necessary to install QtARMSim from PyPI, as QtARMSim standalone executables are provided for GNU/Linux (Ubuntu), Windows, and macOS. These executables can be downloaded from the `QtARMSim home page <https://lorca.act.uji.es/project/qtarmsim>`_.

Also, if you have installed the `Nix package manager <https://nixos.org/download/>`_ and configured it to allow its experimental CLI features, then you can execute the latest version of QtARMSim on GitHub simply with::

    $ nix run github:barrachi/qtarmsim

Finally, if you have installed the `UV python package manager <https://docs.astral.sh/uv/>`_, then you can execute the latest version of QtARMSim on PyPI simply with::

    $ uvx qtarmsim


2. Installing QtARMSim from PyPI
--------------------------------

Although it is more convenient to just install the standalone executables provided in the `QtARMSim home page <https://lorca.act.uji.es/project/qtarmsim>`_, or any of the aforementioned methods, ``nix`` or ``uv``, it is also possible to install QtARMSim from the `Python Package Index (PyPI) <https://pypi.org/>`_

To install QtARMSim from PyPI, you will need to also install its dependencies. QtARMSim depends on: `Python 3 <https://www.python.org/>`_; and `Qt for Python (PySide6) <https://wiki.qt.io/Qt_for_Python>`_. The ARM simulator (ARMSim) is bundled with QtARMSim, as is the `GNU GCC Arm toolchain <http://gcc.gnu.org/>`_.

The following sections explain how to install QtARMSim and its dependencies on **GNU/Linux**, **Windows**, and **macOS**.


2.1 Installing QtARMSim on GNU/Linux
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If instead of just installing the GNU/Linux (Ubuntu) standalone executable provided in the `QtARMSim home page <https://lorca.act.uji.es/project/qtarmsim>`_, you prefer to install QtARMSim from PyPI, then follow the next instructions.

As most GNU/Linux distributions provide packages for ``Python3``, this can be installed via the system’s package manager. ``QtARMSim`` (and ``PySide6``), on the other hand, can be installed using the appropriate ``pip`` variants.

**Example: Installation on Ubuntu**

First, install the next required packages:

.. code-block:: shell-session

    $ sudo apt install pipx
    $ pipx ensurepath

Then, for a single-user installation:

.. code-block:: shell-session

    $ pipx install qtarmsim

Or for a system-wide installation:

.. code-block:: shell-session

    $ sudo pipx ensurepath --global
    $ sudo pipx install --global qtarmsim

*Note:* If the ``--global`` option is not recognised, read the ``pipx`` documentation or search for a workaround. This drawback should be solved with something similar to:

.. code-block:: shell-session

    $ sudo pipx install pipx  # Installs a newer version of pipx on the root home
    $ sudo apt remove pipx    # Removes the older system pipx
    $ sudo bash
    # ~/.local/share/pipx/venvs/pipx/bin/pipx install pipx --global
    # ~/.local/share/pipx/venvs/pipx/bin/pipx ensurepath --global
    # exit
    $ sudo pipx install --global qtarmsim  # The newer version should support --global


2.2 Installing QtARMSim on Windows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If instead of just installing the Windows standalone executable provided in the `QtARMSim home page <https://lorca.act.uji.es/project/qtarmsim>`_, you prefer to install QtARMSim from PyPI, then follow the next steps:

1. Download a 64-bit Python installer from the `Windows official Python website <https://www.python.org/downloads/windows/>`_ (or from the MS Windows store). Make sure to select **"Add python.exe to PATH"** during installation. **Select Python 3.10 or newer** (check the `Qt for Python compatibility matrix <https://wiki.qt.io/Qt_for_Python>`_ for the latest supported versions).

2. Open a console (``cmd`` or ``PowerShell``) and run the following commands:

   .. code-block:: powershell

       pip3 install qtarmsim           # to install qtarmsim
       post_install_qtarmsim           # to create start menu entry and shortcuts


2.3 Installing QtARMSim on macOS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If instead of just installing the macOS standalone executable provided in the `QtARMSim home page <https://lorca.act.uji.es/project/qtarmsim>`_, you prefer to install QtARMSim from PyPI, then follow the next steps:

1. Install Python 3 from the `official Python website <https://www.python.org/downloads/>`_. Make sure you install a Python version supported by PySide6 (check the *Python compatibility matrix* in `Qt for Python <https://wiki.qt.io/Qt_for_Python>`_).

2. Open a terminal and run:

   .. code-block:: shell-session

       $ sudo -H pip3 install qtarmsim
       $ sudo post_install_qtarmsim

After installation, you can run QtARMSim by typing ``qtarmsim`` in a **new** terminal session.

**Note:** If you encounter an error stating that PySide6 is not available for your macOS version, you can install PySide6 via `MacPorts <https://guide.macports.org/#installing.xcode>`_ and then install QtARMSim without Python dependencies:

.. code-block:: shell-session

    $ sudo port install py311-pyside6   # Replace 'py311' with your Python version
    $ sudo -H pip3 install --no-deps qtarmsim
    $ sudo post_install_qtarmsim
