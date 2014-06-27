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

from PyQt4 import QtCore, QtGui

class MyQTreeView(QtGui.QTreeView):
    
    pass

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
        # Compute width as the sum of the width of all the columns and an extra width
        if self.model():
            for i in range(self.model().rowCount(self.model().index(0,0,QtCore.QModelIndex()))):
                width += self.columnWidth(i)
        # @todo: the extra width should be obtained automatically
        width += 15
        # If the vertical scrollbar is visible, add its width
        if my_vertical_scrollbar.isVisible():
            width += my_vertical_scrollbar.width()
        my_dock.setMinimumWidth(width)
        return QtCore.QSize(width, 0)
