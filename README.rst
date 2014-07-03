Qt ARMSim
=========

Qt ARMSim is a graphical frontend to the ARMSim ARM simulator.

It should run on any platform supported by PyQt4, including GNU/Linux,
MacOS/X and Windows.


Dependencies
------------

Qt ARMSim has the following dependencies:

  * `Python3 <https://www.python.org/>`_.
  * `PyQt4 for Python3
    <http://www.riverbankcomputing.co.uk/software/pyqt/intro>`_.
  * `QScintilla <http://www.riverbankcomputing.co.uk/software/qscintilla/intro>`_.

(Depending on the platform, QScintilla is sometimes bundled with
PyQt4. If this is the case, it is not necessary to install it
separately.)

On the other hand, ARMSim has the next dependencies:

  * `Ruby <https://www.ruby-lang.org/en/>`_.
  * `GCC for ARM <http://gcc.gnu.org/>`_.


Installing the dependencies on GNU/Linux
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The GNU/Linux major distributions provide packages for Python3, PyQt4,
QScintilla (if not bundled with PyQt4), and Ruby. You should use the
package manager of your GNU/Linux distribution to install PyQt4 for
Python3 (the package manager will take care of its dependencies and
will also install Python3 if it is not already installed); QScintilla
with python bindings, if offered as a separate package; and Ruby.

For example, in Gentoo, you can use::

  # emerge -av PyQt4 qscintilla-python ruby

Installing GCC for ARM can be achieved either by building a
cross-compiling toolchain, or by installing the `Arduino IDE
<http://arduino.cc/en/Main/Software>`_.

On gentoo, building the cross-compiling toolchain involves the
following commands::

  # emerge -av crossdev
  # crossdev --target arm --ov-output /usr/local/portage


Installing the dependencies on Windows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Windows support has been tested with PyQt4 for Python 3.3. It should
work on newer versions, just make sure that you get the PyQt4 binary
package for the python version that you have installed.

To install Qt ARMSim, and ARMSim dependencies on Windows, please
follow the next steps:

1. Download and install
   `Python 3.3.x <https://www.python.org/downloads/windows/>`_
   (either 32 or 64 bits version). If you want to install a newer
   Python version, just check that there is a PyQt binary package for
   that version.

2. Download and install the binary package of `PyQt4 for Python 3.3
   <http://www.riverbankcomputing.co.uk/software/pyqt/download>`_ (either
   32 or 64 bits, the same as the Python one).

3. Download and install `Ruby <https://www.ruby-lang.org/en/>`_.

Installing GCC for ARM can be achieved either by building a
cross-compiling toolchain, or by installing the `Arduino IDE
<http://arduino.cc/en/Main/Software>`_.


Installing Qt ARMSim
--------------------

Qt ARMSim can be installed automatically using pip (a tool for
installing Python packages), or it can be installed manually, as
described later.


Using pip (recommended method)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If pip is not installed in your system, download `get-pip.py
<https://raw.github.com/pypa/pip/master/contrib/get-pip.py>`_, and
execute::

  python3 get-pip.py

Once ``pip`` is installed, you can install Qt ARMSim with::

  pip3 install --pre qtarmsim

If you execute the previous command as root, it will be installed
system wide. If not, it will be installed only for the user that
executed that command.


Manual installation
^^^^^^^^^^^^^^^^^^^

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



Executing Qt ARMSim
-------------------

If Qt ARMSim has been installed system wide, you can simple execute
the command ``qtarmsim``, as it will have been installed in the system
path.

Otherwise, ``qtarmsim`` will be on a user directory. On GNU/Linux, it
will be on ``~/.local/bin/``.

