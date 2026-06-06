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
Module implementing the post-installation logic for 'pip install'.
"""

from __future__ import annotations

import logging
import os
import sys
import sysconfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------
# Post installation hooks for Windows
# ------------------------------------------------------------------------

def windowsCreateLinks() -> None:
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
        windowsCreateShortcut(linkPath, targetPath, iconPath)

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
            windowsCreateShortcut(linkPath, targetPath, iconPath)


def getWinregEntry(name: str, path: str) -> str | None:
    """
    Gets an entry from the Windows Registry.

    :param name: Variable name
    :param path: Registry variable path
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


def windowsDesktopEntries() -> list[tuple[str, str, str]]:
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


def windowsCreateShortcut(linkPath: str, targetPath: str, iconPath: str) -> None:
    """
    Creates a Windows shortcut

    :param linkPath: Path of the shortcut file.
    :param targetPath: Path the shortcut shall point to
    :param iconPath: Path of the icon file
    """

    import win32com.client
    import pywintypes

    try:
        shell = win32com.client.Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(linkPath)
        shortcut.Targetpath = targetPath
        shortcut.WorkingDirectory = os.path.dirname(targetPath)
        shortcut.IconLocation = iconPath
        shortcut.save()
    except pywintypes.com_error:
        # maybe restrictions prohibited link creation
        pass


# ------------------------------------------------------------------------
# Post installation hooks for macOS
# ------------------------------------------------------------------------

def macOsCreateSymLink() -> None:
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
# Post installation hooks for linux
# ------------------------------------------------------------------------

def linuxAppendPath() -> None:
    """
    If installed as a regular user, make sure that ~/.local/bin/ is in the path
    """
    if os.getenv("USER") != 'root':
        if os.getenv("PATH").find("/.local/bin") == -1:
            appended = False
            local_bin_path = os.path.join(os.getenv("HOME"), ".local/bin")
            bashrc_path = os.path.join(os.getenv("HOME"), ".bashrc")
            logger.warning("QtARMSim has been installed in '{0}' which is not on PATH.".format(local_bin_path))
            if os.path.exists(bashrc_path):
                logger.warning("Trying to prepend '{0}' to PATH...".format(local_bin_path))
                try:
                    with open(bashrc_path, "a") as f:
                        f.write('\n')
                        f.write('# QtARMSim post install\n')
                        f.write('[[ ":$PATH:" != *":{0}:"* ]] && PATH="{0}":"$PATH"\n'.format(local_bin_path))
                        logger.warning("...succeeded!")
                        appended = True
                except OSError:
                    # If we cannot write on .bashrc
                    logger.warning("...could not write on '{}'!".format(bashrc_path))
                    pass
            if appended:
                logger.warning("You should execute 'source {}' to update PATH on any currently open sessions."
                               "".format(bashrc_path))
            else:
                logger.warning("Please, consider adding this directory to PATH.")
                logger.warning("""This can be accomplished by appending 'PATH="{0}":"$PATH"' """
                               """to '{1}'""".format(local_bin_path, bashrc_path))


# ------------------------------------------------------------------------
# Main script
# ------------------------------------------------------------------------
def main() -> None:
    """
    Main script
    """
    if sys.platform.startswith(("win", "cygwin")):
        windowsCreateLinks()
    elif sys.platform == "darwin":
        # This is no longer required, setuptools puts the qtarmsim executable on /opt/local/bin
        # createMacOsSymLink()
        pass
    elif sys.platform == "linux":
        linuxAppendPath()


if __name__ == "__main__":
    main()
