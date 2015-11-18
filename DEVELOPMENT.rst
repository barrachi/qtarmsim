QtARMSim development
====================

How to distribute a new version
-------------------------------

To create a source distribution and upload it to the `testpypi
repository <https://testpypi.python.org/>`_::

   $ python3 ./setup.py qtclean qtcompile sdist upload -r testpypi

To test a sdist tar.gz::

   $ virtualenv --python=python3 testqtarmsim
   $ . testqtarmsim/bin/activate
   $ pip3 install dist/qtarmsim-x.y.z.tar.gz
   $ deactivate


How to build a binary installer for Windows
-------------------------------------------

To create a binary installer for Windows from GNU/Linux with wine, the
next command can be executed::

   $ wine python ./setup.py bdist_wininst --bitmap wininst_banner.bmp --install-script qtarmsim_winpostinstall.py

**Waring:** Although the installer seems to work, the
``qtarmsim_winpostinstall.py`` script does not get called, therefore
the main motivation of using this method is lost. The ``postinstall``
script should create a desktop shortcut and a menu shortcut on Windows
with the appropriate QtARMSim icon.


Install python on Wine
----------------------

To install python on Wine:
  
1. Download ``Python 3.4.3 Windows x86 MSI installer`` from
   `<https://www.python.org/downloads/windows/>`_.
2. Execute: '``wine msiexec /i python-3.4.3.msi``'.
