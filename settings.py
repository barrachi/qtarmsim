# -*- coding: utf-8 -*-

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

import codecs  # To use a consistent encoding when openning version.py
import os

# Read function
def read(fname):
    fname = os.path.join(os.path.dirname(__file__), fname)
    with codecs.open(fname, encoding='utf8') as f:
        return f.read()

# Settings class
class Settings():

    def __init__(self):
        self.name = 'qtarmsim'
        self.version = self._get_version()
        self.description = 'Qt graphical frontend to ARMSim'
        self.long_description = read('README.rst') + '\n\n' + read('INSTALL.rst') + '\n\n' + read('CHANGELOG.rst')
        self.url = 'http://lorca.act.uji.es/project/qtarmsim/'
        self.author = 'Sergio Barrachina Mir'
        self.email = 'barrachi@uji.es'
        self.license = 'GPLV3+'
        self.scripts = ['qtarmsim_winpostinstall.py']
        self.package_data = {
                             'qtarmsim': ['armsim/*',
                                          'gcc-arm/README.rst',
                                          'gcc-arm/linux32/g++_arm_none_eabi/README',
                                          'gcc-arm/linux32/g++_arm_none_eabi/bin/arm-none-eabi-gcc',
                                          'gcc-arm/linux32/g++_arm_none_eabi/lib/gcc/arm-none-eabi/4.4.1/__empty_dir__',
                                          'gcc-arm/linux32/g++_arm_none_eabi/libexec/gcc/arm-none-eabi/4.4.1/collect2',
                                          'gcc-arm/linux32/g++_arm_none_eabi/arm-none-eabi/bin/as',
                                          'gcc-arm/linux64/g++_arm_none_eabi/bin/arm-none-eabi-gcc',
                                          'gcc-arm/linux64/g++_arm_none_eabi/README',
                                          'gcc-arm/linux64/g++_arm_none_eabi/libexec/gcc/arm-none-eabi/4.9.3/collect2',
                                          'gcc-arm/linux64/g++_arm_none_eabi/lib/gcc/arm-none-eabi/4.9.3/__empty_dir__',
                                          'gcc-arm/linux64/g++_arm_none_eabi/arm-none-eabi/bin/as',
                                          'gcc-arm/macos/g++_arm_none_eabi/README',
                                          'gcc-arm/macos/g++_arm_none_eabi/bin/arm-none-eabi-gcc',
                                          'gcc-arm/macos/g++_arm_none_eabi/lib/gcc/arm-none-eabi/4.4.1/__empty_dir__',
                                          'gcc-arm/macos/g++_arm_none_eabi/libexec/gcc/arm-none-eabi/4.4.1/collect2',
                                          'gcc-arm/macos/g++_arm_none_eabi/arm-none-eabi/bin/as',
                                          'gcc-arm/win32/g++_arm_none_eabi/README',
                                          'gcc-arm/win32/g++_arm_none_eabi/bin/arm-none-eabi-gcc.exe',
                                          'gcc-arm/win32/g++_arm_none_eabi/lib/gcc/arm-none-eabi/4.4.1/__empty_dir__',
                                          'gcc-arm/win32/g++_arm_none_eabi/libexec/gcc/arm-none-eabi/4.4.1/collect2.exe',
                                          'gcc-arm/win32/g++_arm_none_eabi/arm-none-eabi/bin/as.exe',
                                          'html/*.html',
                                          'html/img/*',
                                          'res/desktop/qtarmsim.desktop',
                                          'res/images/qtarmsim.png',
                                          'test/add.s',
                                         ],
                            }
        self.data_files = [('share/applications', ['qtarmsim/res/desktop/qtarmsim.desktop']),
                           ('share/pixmaps', ['qtarmsim/res/images/qtarmsim.png']),]
        # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
        self.classifiers = [
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 5 - Production/Stable',
    
            # Who the project is intended for
            'Intended Audience :: Education',
            'Topic :: Software Development :: Assemblers',
            'Topic :: Software Development :: Debuggers',
            'Topic :: Software Development :: Disassemblers',
            'Topic :: System :: Emulators',
    
            # License long description
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    
            # Python versions supported
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            ]
        self.keywords = ['ARM', 'simulator', 'assembler', 'disassembler', 'debugger']
        self.requires = ['PySide >= 1.2.1', ]

    def _get_version(self):
        """Gets version from 'qtarmsim/version.py'."""
        version_dict = {}
        with codecs.open('qtarmsim/version.py') as fp:
            exec(fp.read(), version_dict)
        return version_dict['__version__']
