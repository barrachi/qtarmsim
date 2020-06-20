#
# See DEVELOPMENT.rst for instructions on how to use this module
#

###########################################################################
#                                                                         #
#  This file is part of QtARMSim.                                         #
#                                                                         #
#  QtARMSim is free software: you can redistribute it and/or modify       #
#  it under the terms of the GNU General Public License as published by   #
#  the Free Software Foundation; either version 3 of the License, or      #
#  (at your option) any later version.                                    #
#                                                                         #
#  This program is distributed in the hope that it will be useful, but    #
#  WITHOUT ANY WARRANTY; without even the implied warranty of             #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU      #
#  General Public License for more details.                               #
#                                                                         #
###########################################################################

#
# References:
# + Setuptools' documentation
#   https://setuptools.readthedocs.io/en/latest/
# + Python packaging:
#   https://the-hitchhikers-guide-to-packaging.readthedocs.org/en/latest/
# + Post-install script with Python setuptools
#   https://stackoverflow.com/questions/20288711/post-install-script-with-python-setuptools
# + Post installation script to create shortcut on Windows desktop and entry on Programs Folder
#   See qtarmsim/post_install.py
#


from setuptools import setup, find_packages

from settings import Settings
from setup_extra import DevelopAndPostDevelop, InstallAndPostInstall, QtClean, QtCompile, UpdateFiles

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
    install_requires=s.install_requires,
    entry_points={
        'gui_scripts': [
            'qtarmsim=qtarmsim.qtarmsim:main',
        ],
        'console_scripts': [
            'post_install_qtarmsim=qtarmsim.post_install:main'
        ],
    },
    cmdclass={'develop': DevelopAndPostDevelop,
              'install': InstallAndPostInstall,
              'qtclean': QtClean,
              'qtcompile': QtCompile,
              'update_files': UpdateFiles,
              },
)
