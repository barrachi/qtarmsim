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

"""
Extra distutils command classes, QtClean and QtCompile, to clean and compile the qtarmsim project, respectivelly.
"""

from distutils.core import Command
import fnmatch
import os
from subprocess import call
import sys


# Find files and dirs from the given path
def findFilesAndDirs(path, filePatterns=[], dirPatterns=[]):
    files = []
    dirs = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        for filePattern in filePatterns:
            files += [os.path.join(dirpath, fn) for fn in fnmatch.filter(filenames, filePattern)]
        for dirPattern in dirPatterns:
            dirs += [os.path.join(dirpath, dn) for dn in fnmatch.filter(dirnames, dirPattern)]
    return (files, dirs)

def findFiles(path, filePatterns):
    return findFilesAndDirs(path, filePatterns, [])[0]

# Clean class (see /usr/lib64/python3.3/distutils/command/command_template)
class QtClean(Command):

    # Brief (40-50 characters) description of the command
    description = "Removes temporary files"

    # List of option tuples
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        files = []
        dirs = []
        (files, dirs) = findFilesAndDirs('.', ('*.pyc', ), ('__pycache__', ))
        filesToBeRemoved = files
        dirsToBeRemoved = dirs
        files = findFiles('./examples', ('*.o', '*.err', '*.lst'))
        filesToBeRemoved += files
        print("Removing temporary files...")
        for fileName in filesToBeRemoved:
            os.remove(fileName)
        print("Removing temporary directories...")
        for dirName in dirsToBeRemoved:
            os.rmdir(dirName)

# Clean class (see /usr/lib64/python3.3/distutils/command/command_template)
class QtCompile(Command):

    # Brief (40-50 characters) description of the command
    description = "Runs the PySide development tools on the current project"

    # List of option tuples
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # Run pysyde2-uic
        CMD = 'pyside2-uic'
        inputFileNames = findFiles('.', ('*.ui',))
        for fileName in inputFileNames:
            outputFileName = os.path.splitext(fileName)[0] + '.py'
            cmdArray = [CMD, '-o', outputFileName, fileName]
            print("Executing {}...".format(' '.join(cmdArray)))
            error = call(cmdArray) #, cwd = os.getcwd())
            if error:
                sys.exit(-1)
        # Run pyside2-rcc
        CMD = 'pyside2-rcc'
        inputFileNames = findFiles('.', ('*.qrc',))
        for fileName in inputFileNames:
            outputFileName = os.path.splitext(fileName)[0] + '_rc.py'
            # cmdArray = [CMD, '-py3', '-o', outputFileName, fileName]
            cmdArray = [CMD, '-o', outputFileName, fileName]
            print("Executing {}...".format(' '.join(cmdArray)))
            error = call(cmdArray)
            if error:
                sys.exit(-1)
        # Run lrelease
        CMD = 'lrelease'
        cmdArray = [CMD, './qtarmsim/qtarmsim.pro']
        print("Executing {}...".format(' '.join(cmdArray)))
        error = call(cmdArray)
        if error:
            sys.exit(-1)
        # Run pyside2-lupdate
        CMD = 'pyside2-lupdate'
        cmdArray = [CMD, './qtarmsim/qtarmsim.pro']
        print("Executing {}...".format(' '.join(cmdArray)))
        error = call(cmdArray)
        if error:
            sys.exit(-1)
        # Run linguist
        print("Now you can run 'linguist ./qtarmsim/lang/qtarmsim_es.ts'")
