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

import sys

from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import Qt

from ..model.memorylcdproxymodel import MemoryLCDProxyModel
from ..model.memorymodel import MemoryModel


class MemoryLCDView(QtWidgets.QTableView):

    def __init__(self, parent=None):
        super(MemoryLCDView, self).__init__(parent)
        # ------------------------------------------------------------
        #  Instance attributes that will be properly initialized later
        # ------------------------------------------------------------
        self.memoryLCDProxyModel = None
        self.LCDColumns = None
        self.LCDRows = None
        # ------------------------------------------------------------
        self.setGridStyle(Qt.NoPen)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.setFocusPolicy(Qt.NoFocus)
        # #78AE4D
        #                 padding: 8 -8 -8 8;
        #                 padding: 4 -3 -3 4;
        self.setStyleSheet("""
            QTableView { background: transparent;
                         border-width: 18 18 18 18;
                         padding: 4 -4 -4 4;
                         border-image: url(:/images/lcd.png) 18 18 18 18;}
            QTableView::item:hover {background: none;}
        """)
        self.verticalScrollBar().setDisabled(True)
        # self.horizontalScrollBar().setDisabled(True)
        self.setFrameStyle(QtWidgets.QFrame.NoFrame)

    def setModel(self, memoryModel_, hexStartAddress, LCDColumns=32, LCDRows=6):
        """Sets the memory model and the number of columns and rows of the LCD display"""
        self.memoryLCDProxyModel = MemoryLCDProxyModel()
        self.memoryLCDProxyModel.setSourceModel(memoryModel_, hexStartAddress, LCDColumns, LCDRows)
        super(MemoryLCDView, self).setModel(self.memoryLCDProxyModel)
        self.LCDColumns = LCDColumns
        self.LCDRows = LCDRows
        self.resize()

    def resize(self):
        """Resize the columns and rows of the LCD to its contents size, and then fixes the total width and height of
        the LCD."""
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.setFixedWidth(18 + 18 + 8 + sum([self.columnWidth(i) for i in range(self.LCDColumns)]))
        self.setFixedHeight(18 + 18 + 8 + sum([self.rowHeight(i) for i in range(self.LCDRows)]))
        self.repaint()

    def wheelEvent(self, event):
        """Process the wheel event: zooms in and out whenever a CTRL+wheel event is triggered"""
        if event.modifiers() == QtCore.Qt.ControlModifier:
            self.memoryLCDProxyModel.changeFontSize(event.delta() / 120)
            self.resize()
        else:
            super(MemoryLCDView, self).wheelEvent(event)


if __name__ == "__main__":
    #
    # To test this module, execute the following command from qtarmsim upper directory:
    #
    #    python3 -m qtarmsim.widget.memorylcdview
    #
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    mainWindow.setGeometry(200, 200, 1000, 400)
    # Memory model
    memoryModel = MemoryModel(app)
    memoryModel.appendMemoryBank('ROM', '0x10010000', ['0x{:02X}'.format(i) for i in range(24)])
    memoryModel.appendMemoryBank('RAM', '0x20070000', ['0x{:02X}'.format(i) for i in range(65, 256)])
    # Memory LCD View
    memoryLCDView = MemoryLCDView(mainWindow)
    memoryLCDView.setModel(memoryModel, '0x20070000', 32, 6)
    # Show main window and enter main loop
    mainWindow.setCentralWidget(memoryLCDView)
    mainWindow.show()
    sys.exit(app.exec_())
