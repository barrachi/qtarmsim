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

# -----------------------------------oOOo----------------------------------
# To test this module, execute from the qtarmsim upper directory:
#    python3 -m qtarmsim.widget.memorylcdview
# -------------------------------------------------------------------------

from __future__ import annotations

import sys

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt

from ..model.memorylcdproxymodel import MemoryLCDProxyModel
from ..model.memorymodel import MemoryModel


class MemoryLCDView(QtWidgets.QTableView):

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super(MemoryLCDView, self).__init__(parent)
        self.setGridStyle(Qt.PenStyle.NoPen)
        self.horizontalHeader().hide()
        self.horizontalHeader().setMinimumSectionSize(1)  # Minimum width
        self.verticalHeader().hide()
        self.verticalHeader().setMinimumSectionSize(1)  # Minimum height
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # #78AE4D
        #                 padding: 8 -8 -8 8;
        #                 padding: 4 -3 -3 4;
        self.setStyleSheet("""
            QTableView { background: transparent;
                         border-width: 8 8 8 8;
                         padding: 16 -6 -6 16;
                         border-image: url(:/images/lcd.png) 8 8 8 8;}
            QTableView::item:hover {background: none;}
        """)
        self.verticalScrollBar().setDisabled(True)
        self.horizontalScrollBar().setDisabled(True)
        self.setFrameStyle(QtWidgets.QFrame.Shape.NoFrame)
        #  Instance attributes that will be populated later
        self.memoryLCDProxyModel = None
        self.LCDColumns = None
        self.LCDRows = None

    def setModel(self, memoryModel_: MemoryModel, hexStartAddress: str = '0x20080000', LCDColumns: int = 32, LCDRows: int = 6) -> None:
        """Sets the memory model and the number of columns and rows of the LCD"""
        self.memoryLCDProxyModel = MemoryLCDProxyModel()
        self.memoryLCDProxyModel.setSourceModel(memoryModel_, hexStartAddress, LCDColumns, LCDRows)
        super().setModel(self.memoryLCDProxyModel)
        self.LCDColumns = LCDColumns
        self.LCDRows = LCDRows
        self.resize()

    def resize(self, size: QtCore.QSize = QtCore.QSize(0, 0)) -> None:
        """Resize the columns and rows of the LCD to the size of its content, and then fixes the total width and height of
        the LCD."""
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.setFixedWidth(18 + 18 + 8 + sum([self.columnWidth(i) for i in range(self.LCDColumns)]))
        self.setFixedHeight(18 + 18 + 8 + sum([self.rowHeight(i) for i in range(self.LCDRows)]))
        # self.update()  # @todo: check that update is not required any more

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        """Process the wheel event: zooms in and out whenever a CTRL+wheel event is triggered"""
        if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
            self.memoryLCDProxyModel.changeFontSize(event.angleDelta().y() / 120)
            self.resize()
        else:
            super(MemoryLCDView, self).wheelEvent(event)


if __name__ == "__main__":
    # To test this model, see the note in the header of this file
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    mainWindow.setGeometry(200, 200, 1000, 400)
    # Memory model
    memoryModel = MemoryModel(app)
    memoryModel.appendMemoryBank('ROM', '0x10010000', ['0x{:02X}'.format(i) for i in range(24)])
    memoryModel.appendMemoryBank('RAM', '0x20080000', ['0x{:02X}'.format(i) for i in range(65, 256)])
    # Memory LCD View
    memoryLCDView = MemoryLCDView(mainWindow)
    memoryLCDView.setModel(memoryModel, '0x20080000', 32, 6)
    # Show main window and enter the main loop
    mainWindow.setCentralWidget(memoryLCDView)
    mainWindow.show()
    sys.exit(app.exec())
