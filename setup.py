#
# See DEVELOPMENT.rst for instructions
#
# Documentation for python packaging:
# https://the-hitchhikers-guide-to-packaging.readthedocs.org/en/latest/
#
# Documentation for distutils
# https://docs.python.org/3.3/distutils/
#
# Writing post-installation-script to create shortcut on Windows desktop
# https://www.domenkozar.com/2009/09/27/writing-post-installation-script-to-create-shortcut-on-windows-desktop/
#
# Known limitations:
#
# * 'install_requires = s.requires,' could be used to automatically
#    install PySide when installing qtarmsim. The problem is that this
#    option will make the installation of PySide harder on binary
#    based GNU/Linux distributions, because PySide will be downloaded
#    as source code, and pip3 will try to compile it (which requires
#    the correct compilers, etc.  being already installed on the
#    system). This happens even if PySide has been previously
#    installed by the own package manager of that distribution.
#
#    Some python packages appear as installed when you execute 'pip3
#    list', even if they have been installed by the package manager
#    and not by pip3 itself. So, it seems, IMHO, that the problem is
#    due to PySide (or the PySide package) not saying that it is
#    already installed.
#

# from distutils.core import setup
import os

from setuptools import setup, find_packages

from settings import Settings
from setup_extra import QtClean, QtCompile

# Common settings used by distutils and cx_freeze
s = Settings()

# Setup
setup(
    # Application details
    name=s.name,
    version=s.version,
    description=s.description,
    url=s.url,
    long_description=s.long_description,
    # Author details
    author=s.author,
    author_email=s.email,
    # Application classifiers
    classifiers=s.classifiers,
    # Application keywords
    keywords=s.keywords,

    # --------------------------------
    #  distutils parameters
    # --------------------------------
    scripts=s.scripts,
    packages=find_packages(exclude=['build', 'dist', 'distfiles', 'docs', 'examples', 'scripts', 'tmp']),
    package_data=s.package_data,
    data_files=s.data_files,
    entry_points={
        'gui_scripts': [
            'qtarmsim=qtarmsim:main',
        ],
    },
    cmdclass={'qtclean': QtClean, 'qtcompile': QtCompile},
    install_requires=['PySide2']
)
