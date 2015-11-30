#!python3
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

# References:
#  + Writing post-installation-script to create shortcut on Windows desktop
#    https://www.domenkozar.com/2009/09/27/writing-post-installation-script-to-create-shortcut-on-windows-desktop/
#
#  + icehms/windows_postinstall.py
#    https://github.com/oroulet/icehms/blob/master/windows_postinstall.py
#
#  + pyside_postinstall file

import os
import sys
import shutil
import qtarmsim

name = 'qtarmsim'
desc = 'QtARMSim'

try:
    # When this script is run from inside the bdist_wininst installer,
    # file_created() and directory_created() are additional builtin
    # functions which write lines to Python23\pyside-install.log. This is
    # a list of actions for the uninstaller, the format is inspired by what
    # the Wise installer also creates.
    file_created
    is_bdist_wininst = True
except NameError:
    is_bdist_wininst = False # we know what it is not - but not what it is :)
    def file_created(*args):
        myName = sys._getframe().f_code.co_name
        print("Function '{}' called with args: {}".format(myName, ', '.join(args)))
    def directory_created(*args):
        myName = sys._getframe().f_code.co_name
        print("Function '{}' called with args: {}".format(myName, ', '.join(args)))
    def get_special_folder_path(*args):
        myName = sys._getframe().f_code.co_name
        print("Function '{}' called with args: {}".format(myName, ', '.join(args)))
        output = os.path.curdir
        print("    Return value: {}".format(output))
        return output
    def create_shortcut(*args):
        myName = sys._getframe().f_code.co_name
        print("Function '{}' called with args: {}".format(myName, ', '.join(args)))



def install():
    desktopPath = get_special_folder_path("CSIDL_DESKTOPDIRECTORY")
    menuPath = get_special_folder_path("CSIDL_COMMON_PROGRAMS")
    menuPath = os.path.join(menuPath, desc)
    menuLinkPath = os.path.join(menuPath, "{}.lnk".format(name))
    desktopLinkPath = os.path.join(desktopPath, "{}.lnk".format(name))
    iconPath = os.path.join(os.path.dirname(qtarmsim.__file__), '{}.ico'.format(name))
    appPath = os.path.join(sys.prefix, "Scripts", "{}.exe".format(name))

    # Create desktopLinkPath shortcut to appPath
    create_shortcut(
                    appPath,            # command
                    desc,               # description
                    desktopLinkPath,    # link path
                    '',                 # parameters
                    '',                 # working dir
                    iconPath            # icon path
                    )
    
    # Tell windows installer that we created another file which should be deleted on uninstallation
    file_created(desktopLinkPath)
    
    # Create menuPath if it does not exist and register the created directory
    if not os.path.isdir(menuPath):
        try:
            os.makedirs(menuPath)
        except Exception as why:
            print("Could not create menu entry for all users")
        else:
            directory_created(menuPath)
    
    # If menuPath exists, create shortcut to appPath
    if os.path.isdir(menuPath):
        create_shortcut(
                        appPath,            # command
                        desc,               # description
                        menuLinkPath,       # link path
                        '',                 # parameters
                        '',                 # working dir
                        iconPath            # icon path
                        )
        file_created(menuLinkPath)


def uninstall():
    print("QtARMSim shortcuts were successfully removed.")


if __name__ == '__main__':
    myName = sys.argv[0]
    print("Executing {}...".format(myName))
    argn = 1
    while argn < len(sys.argv):
        if sys.argv[argn] == '-install':
            install()
        elif sys.argv[argn] == '-remove':
            uninstall()
        argn += 1

    #===========================================================================
    # if len(sys.argv) != 2:
    #     print("{} must be called with exactly one parameter".format(myName))
    #     sys.exit(-1)
    #===========================================================================
