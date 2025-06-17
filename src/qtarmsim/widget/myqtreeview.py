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

from PySide6 import QtCore, QtWidgets, QtGui


class MyQTreeView(QtWidgets.QTreeView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry_updated = False
        self.header().setStretchLastSection(False)
        # self.header().setSectionResizeMode(QHeaderView.ResizeToContents)

    def updateGeometrySizes(self):
        self.geometry_updated = True
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)
        width = self.columnWidth(0) + self.columnWidth(1)
        # If the vertical scroll bar is visible, add its width
        my_vertical_scrollbar = self.verticalScrollBar()
        if my_vertical_scrollbar.isVisible():
            width += my_vertical_scrollbar.width()
        self.setMinimumWidth(width)
        self.parent().setMinimumWidth(0)
        self.parent().parent().setMinimumWidth(0)

    def sizeHint(self):
        """
        If there is no model yet, just return a 0x0 size.
        Else, compute the total width and height and set the minimum and maximum sizes of the parent dock widget
        """
        hint = super().sizeHint()
        if self.model() is None or self.model().rowCount(QtCore.QModelIndex()) == 0:
            return hint
        if not self.geometry_updated:
            self.updateGeometrySizes()
        hint.setWidth(self.minimumWidth())
        return hint

    def increaseFontSize(self, inc):
        """
        Increases (decreases) the font size
        :param inc: number of points to increase the font
        """
        self.model().beginResetModel()
        myFontPointSize = self.model().qFont.pointSize()
        myFontPointSize += inc
        if myFontPointSize < 10:
            myFontPointSize = 10
        self.model().qFont.setPointSize(myFontPointSize)
        self.model().qFontLast.setPointSize(myFontPointSize)
        expanded = [self.isExpanded(self.model().index(row, 0, QtCore.QModelIndex())) for row in
                    range(self.model().rootItem.childCount())]
        self.model().endResetModel()
        for row in range(self.model().rootItem.childCount()):
            self.setExpanded(self.model().index(row, 0, QtCore.QModelIndex()), expanded[row])
        self.updateGeometrySizes()

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        """
        Processes the CTRL++ and CTRL+- events
        """
        if event.modifiers() == QtCore.Qt.ControlModifier:
            if event.text() == '+':
                self.increaseFontSize(1)
                return
            elif event.text() == '-':
                self.increaseFontSize(-1)
                return
        super().keyPressEvent(event)

    def wheelEvent(self, event):
        """
        Processes the wheel event: zooms in and out whenever a CTRL+wheel event is triggered
        """
        if event.modifiers() == QtCore.Qt.ControlModifier:
            self.increaseFontSize(event.angleDelta().y() / 120)
        else:
            super().wheelEvent(event)
