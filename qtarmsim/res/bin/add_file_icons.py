#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###########################################################################
#                                                                         #
#  This file is part of Qt ARMSim.                                        #
#                                                                         #
#  Qt ARMSim is free software: you can redistribute it and/or modify      #
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

import fnmatch
import os
import re
import sys


def png_matches(path, name):
    matches = []
    for root, dirnames, filenames in os.walk(path):  # @UnusedVariable dirnames
        for filename in fnmatch.filter(filenames, '{}.png'.format(name)):
            matches.append(os.path.join(root, filename))
    return matches

def main():
    if len(sys.argv) != 2:
        print("A python script generated from a ui file must be provided")
        sys.exit(-1)
    icon_re = re.compile('([ ]+).*QtGui.QIcon.fromTheme\(.*"([^"]*)".*')
    png_re = re.compile('.*oxygen/([0-9]+)x([0-9]+)/(.*)')
    #/home/barrachi/datos/aplicaciones/pyqt/qtarmsim/qtarmsim/res/oxygen/48x48/actions/debug-run.png
    f = open(sys.argv[1])
    ui_path = os.path.dirname(sys.argv[1])
    icon_path = os.path.abspath(os.path.join(ui_path, "..", "res", "oxygen"))
    for line in f:
        line = line.rstrip()
        result = icon_re.search(line) 
        if result:
            spaces, icon_name = result.groups() 
            print("{}# BEGIN section included by add_file_icons.py".format(spaces))
            print("{}myicon = QtGui.QIcon()".format(spaces))
            for png_path in png_matches(icon_path, icon_name):
                (width, heigth, name) = png_re.search(png_path).groups()
                print('{}myicon.addFile(":/themes/oxygen/{}x{}/{}", QtCore.QSize({}, {}))'.format(spaces, width, heigth, name, width, heigth))
            # 'icon = QtGui.QIcon.fromTheme(_fromUtf8("edit-paste"))'
            # -> 'icon = QtGui.QIcon.fromTheme(_fromUtf8("edit-paste"), myicon)'
            print("{}{}".format(line[:-1], ", myicon)"))
            print("{}# END section included by add_file_icons.py".format(spaces))
        else:
            print(line)
    print("from ..res import oxygen_rc")
    
    
if __name__ == "__main__":
    main()