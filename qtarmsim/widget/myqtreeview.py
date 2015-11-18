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

from PySide import QtCore, QtGui

class MyQTreeView(QtGui.QTreeView):
    
    def sizeHint(self):
        """
        If there is no model yet, just return a 0x0 size.
        Else, compute the total width and set the minimum and maximum sizes of the parent dock widget
        """
        if self.model() == None:
            return QtCore.QSize(0,0)
        width=0
        my_vertical_scrollbar = self.verticalScrollBar()
        my_dock = self.parent().parent()
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)
        for i in range(2):
            width += self.columnWidth(i)
        # If the vertical scroll bar is visible, add its width
        if my_vertical_scrollbar.isVisible():
            width += my_vertical_scrollbar.width()
        self.setMinimumSize(width, 0)
        # @todo: the extra width should be obtained automatically
        my_dock.setMinimumWidth(width+15)
        return QtCore.QSize(width, 0)
