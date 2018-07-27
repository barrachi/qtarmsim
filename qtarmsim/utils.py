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

from PySide2 import QtGui


def getMonoSpacedFont():
    """Tries to get a monospaced font in Linux, Windows and MacOS"""
    font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
    # If the previous line does not work...
    if not QtGui.QFontInfo(font).fixedPitch():
        font = QtGui.QFont("Monospace")
        font.setStyleHint(QtGui.QFont.Monospace)
        # If we are not there yet...
        if not QtGui.QFontInfo(font).fixedPitch():
            font.setStyleHint(QtGui.QFont.TypeWriter)
    font.setPointSize(QtGui.QFont().pointSize())  # Using the system default font point size
    return font
