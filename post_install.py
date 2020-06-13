#!/usr/bin/env python3
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

###########################################################################
# Based on eric6_post_install.py script from eric6                        #
#   https://eric-ide.python-projects.org/eric-code.html                   #
#   Copyright (c) 2019 - 2020 Detlev Offenbach <detlev@die-offenbachs.de> #
###########################################################################

"""
Module implementing the post install logic for 'pip install'.
"""

import os
import sys
import sysconfig


# ------------------------------------------------------------------------
# Post installation hooks for Windows
# ------------------------------------------------------------------------

def createWindowsLinks():
    """
    Creates Desktop and Start Menu links.
    """
    regPath = (
            "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer" +
            "\\User Shell Folders"
    )

    # 1) Create desktop shortcuts
    regName = "Desktop"
    desktopFolder = os.path.normpath(os.path.expandvars(getWinregEntry(regName, regPath)))
    for linkName, targetPath, iconPath in windowsDesktopEntries():
        linkPath = os.path.join(desktopFolder, linkName)
        createWindowsShortcut(linkPath, targetPath, iconPath)

    # 2) Create start menu entry and shortcuts
    regName = "Programs"
    programsEntry = getWinregEntry(regName, regPath)
    if programsEntry:
        programsFolder = os.path.normpath(os.path.expandvars(programsEntry))
        qtarmsimEntryPath = programsFolder
        # The next code will generate a custom folder on the programs one
        # 8< - - - - - - - -
        # qtarmsimEntryPath = os.path.join(programsFolder, "QtARMSim")
        # if not os.path.exists(qtarmsimEntryPath):
        #     try:
        #         os.makedirs(qtarmsimEntryPath)
        #     except EnvironmentError:
        #         # maybe restrictions prohibited link creation
        #         return
        # 8< - - - - - - - -
        for linkName, targetPath, iconPath in windowsDesktopEntries():
            linkPath = os.path.join(qtarmsimEntryPath, linkName)
            createWindowsShortcut(linkPath, targetPath, iconPath)


def getWinregEntry(name, path):
    """
    Gets an entry from the Windows Registry.

    :param name: Variable name
    :param path: Registry path of the variable
    :return: Value of the requested registry variable
    """
    try:
        import winreg
    except ImportError:
        return None

    try:
        registryKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(registryKey, name)
        winreg.CloseKey(registryKey)
        return value
    except WindowsError:
        return None


def windowsDesktopEntries():
    """
    Generates the data for the Windows Desktop links.

    :return: List of tuples containing the desktop link name, the link target and the icon target.
    """
    scriptsDir = sysconfig.get_path("scripts")
    return [
        ("QtARMSim.lnk",
         os.path.join(scriptsDir, "qtarmsim.exe"),
         os.path.join(scriptsDir, "qtarmsim.ico")
         ),
    ]


def createWindowsShortcut(linkPath, targetPath, iconPath):
    """
    Creates a Windows shortcut

    :param linkPath: Path of the shortcut file.
    :param targetPath: Path the shortcut shall point to
    :param iconPath: Path of the icon file
    """

    from win32com.client import Dispatch
    from pywintypes import com_error

    try:
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(linkPath)
        shortcut.Targetpath = targetPath
        shortcut.WorkingDirectory = os.path.dirname(targetPath)
        shortcut.IconLocation = iconPath
        shortcut.save()
    except com_error:
        # maybe restrictions prohibited link creation
        pass


# ------------------------------------------------------------------------
# Post installation hooks for macOS
# ------------------------------------------------------------------------

def createMacOsSymLink():
    """
    Creates a symbolic link to qtarmsim in /opt/local/bin/.
    """
    if os.geteuid() == 0:
        srcPath = "/opt/local/Library/Frameworks/Python.framework/Versions/{}.{}/bin/qtarmsim".format(
            sys.version_info.major, sys.version_info.minor)
        dstPath = "/opt/local/bin/qtarmsim"
        if os.path.exists(dstPath):
            os.unlink(dstPath)
        os.symlink(srcPath, dstPath)


# ------------------------------------------------------------------------
# Main script
# ------------------------------------------------------------------------

def main():
    """
    Main script
    """
    if sys.platform.startswith(("win", "cygwin")):
        createWindowsLinks()
    elif sys.platform == "darwin":
        # This is no longer required, setuptools puts the qtarmsim executable on /opt/local/bin
        # createMacOsSymLink()
        pass


if __name__ == "__main__":
    main()
