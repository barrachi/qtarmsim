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
Extra command classes:
 + DevelopAndPostDevelop: develop command that can perform post development actions.
 + InstallAndPostInstall: install command that can perform post installation actions.
 + QtClean: command that cleans the QtARMSim project.
 + QtCompile: command that compiles the QtARMSim project.

References:
 + /usr/lib64/python3.3/distutils/command/command_template
 + https://stackoverflow.com/questions/20288711/post-install-script-with-python-setuptools
"""

import atexit
import datetime
import fnmatch
import os
import sys
from distutils.core import Command
from subprocess import call

from setuptools.command.develop import develop
from setuptools.command.install import install

from qtarmsim.post_install import main as qtarmsim_post_install
from settings import Settings


class DevelopAndPostDevelop(develop):
    """Post-installation for development mode."""

    def run(self):
        develop.run(self)
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION


class InstallAndPostInstall(install):
    """Post-installation for installation mode."""

    def run(self):
        install.run(self)
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
        atexit.register(qtarmsim_post_install)


def findFilesAndDirs(path, filePatterns=None, dirPatterns=None):
    """
    Returns the files and directories found on the given path by using the given file and dir patterns.

    :param path: The path from where to search.
    :param filePatterns: File patterns to be used.
    :param dirPatterns: Directory patterns to be used.
    :return: A 2-tuple with the list of directories found and the list of files found.
    """
    if dirPatterns is None:
        dirPatterns = []
    if filePatterns is None:
        filePatterns = []
    files = []
    dirs = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        for filePattern in filePatterns:
            files += [os.path.join(dirpath, fn) for fn in fnmatch.filter(filenames, filePattern)]
        for dirPattern in dirPatterns:
            dirs += [os.path.join(dirpath, dn) for dn in fnmatch.filter(dirnames, dirPattern)]
    return files, dirs


def findFiles(path, filePatterns):
    """
    Returns the files found on the given path by using the given file and dir patterns.

    :param path: The path from where to search.
    :param filePatterns: File patterns to be used.
    :return: A list with the found files.
    """
    return findFilesAndDirs(path, filePatterns, [])[0]


class QtClean(Command):
    """
    QtClean class
    """
    # Brief (40-50 characters) description of the command
    description = "Removes temporary files"

    # List of option tuples
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        filesToBeRemoved, dirsToBeRemoved = findFilesAndDirs('.', ('*.pyc',), ('__pycache__',))
        filesToBeRemoved += findFiles('./examples', ('*.o', '*.err', '*.lst'))
        print("Removing temporary files...")
        for fileName in filesToBeRemoved:
            os.remove(fileName)
        print("Removing temporary directories...")
        for dirName in dirsToBeRemoved:
            os.rmdir(dirName)


class QtCompile(Command):
    """
    QtCompile class
    """
    # Brief (40-50 characters) description of the command
    description = "Runs the PySide development tools on the current project"

    # List of option tuples
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # 1) Run pyside2-uic
        CMD = 'pyside2-uic'
        inputFileNames = findFiles('.', ('*.ui',))
        for fileName in inputFileNames:
            outputFileName = os.path.splitext(fileName)[0] + '.py'
            cmdArray = [CMD, '-o', outputFileName, fileName]
            print("Executing {}...".format(' '.join(cmdArray)))
            error = call(cmdArray)  # , cwd = os.getcwd())
            if error:
                sys.exit(-1)
        # 2) Run pyside2-rcc
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
        # 3) Run lrelease
        CMD = 'lrelease'
        cmdArray = [CMD, './qtarmsim/qtarmsim.pro']
        print("Executing {}...".format(' '.join(cmdArray)))
        error = call(cmdArray)
        if error:
            sys.exit(-1)
        # 4) Run pyside2-lupdate
        CMD = 'pyside2-lupdate'
        cmdArray = [CMD, './qtarmsim/qtarmsim.pro']
        print("Executing {}...".format(' '.join(cmdArray)))
        error = call(cmdArray)
        if error:
            sys.exit(-1)
        # 5) Run linguist
        print("Now you can run 'linguist ./qtarmsim/lang/qtarmsim_es.ts'")


class UpdateFiles(Command):
    """
    UpdateFiles class
    """
    # Brief (40-50 characters) description of the command
    description = "Updates certain files with the current version info"

    # List of option tuples
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        in_files = ["qtarmsim/res/desktop/qtarmsim.appdata.xml.in"]
        for in_file in in_files:
            in_file = os.path.join(os.path.dirname(__file__), in_file)
            out_file = in_file[:-3]
            print("Updating {}...".format(out_file))
            with open(in_file, encoding="utf-8") as f:
                text = f.read()
            text = text \
                .replace("@MARKER@", "") \
                .replace("@VERSION@", Settings.get_version()) \
                .replace("@DATE@", datetime.date.today().isoformat())
            with open(out_file, 'w', encoding="utf-8") as f:
                f.write(text)
