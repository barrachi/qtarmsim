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

from PySide import QtCore, QtGui
from PySide.QtCore import Qt

from .. model.memorymodel import MemoryModel
from .. model.memorylcdproxymodel import MemoryLCDProxyModel



class MemoryLCDView(QtGui.QTableView):
    
    def __init__(self, parent=None):
        super(MemoryLCDView, self).__init__(parent)
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
        self.horizontalScrollBar().setDisabled(True)
        self.setFrameStyle(QtGui.QFrame.NoFrame)
                           
        
    def setModel(self, memoryModel, hexStartAddress, LCDColumns = 32, LCDRows = 6):
        self.memoryLCDProxyModel = MemoryLCDProxyModel()
        self.memoryLCDProxyModel.setSourceModel(memoryModel, hexStartAddress, LCDColumns, LCDRows)
        super(MemoryLCDView, self).setModel(self.memoryLCDProxyModel)
        #QtGui.QTableView.setModel(self, self.memoryLCDProxyModel)
        self.LCDColumns = LCDColumns
        self.LCDRows = LCDRows
        #for i in range(self.LCDRows):
        #    self.resizeRowToContents(i)
        #for j in range(self.LCDColumns):
        #    self.resizeColumnToContents(j)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        for i in range(self.LCDColumns):
            self.setColumnWidth(i, self.columnWidth(i)-8)
        self.setFixedWidth(18 + 18 + 8 + sum([self.columnWidth(i) for i in range(self.LCDColumns)]))
        self.setFixedHeight(18 + 18 + 8 + sum([self.rowHeight(i) for i in range(self.LCDRows)]))
        #self.setCursor(Qt.OpenHandCursor)

if __name__ == "__main__":
    #
    # To test this module, execute from qtarmsim upper directory the following command:
    #
    #    python3 -m qtarmsim.widget.memorylcdview
    #
    app = QtGui.QApplication(sys.argv)
    mainWindow = QtGui.QMainWindow()
    mainWindow.setGeometry(200, 200, 1000, 400)
    # Memory model
    memoryModel = MemoryModel(app)
    memoryModel.appendMemoryBank('ROM', '0x10010000', ['0x{:02X}'.format(i) for i in range(24)])
    memoryModel.appendMemoryBank('RAM', '0x20070000', ['0x{:02X}'.format(i) for i in range(65, 256)])
    # Memory LCD Wiew
    memoryLCDView = MemoryLCDView(mainWindow)
    memoryLCDView.setModel(memoryModel, '0x20070000', 32, 6)
    # Show main window and enter main loop
    mainWindow.setCentralWidget(memoryLCDView)
    mainWindow.show()
    sys.exit(app.exec_())
