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
from typing_extensions import override

from ..model.memorylcdproxymodel import MemoryLCDProxyModel
from ..model.memorymodel import MemoryModel


_LCD_STYLE_LIGHT = """
    QTableView { background: transparent;
                 border-width: 8 8 8 8;
                 padding: 16 -6 -6 16;
                 border-image: url(:/images/lcd.png) 8 8 8 8;}
    QTableView::item { background: transparent; }
    QTableView::item:hover { background: none; }
"""

_LCD_STYLE_DARK = """
    QTableView { background: transparent;
                 border-width: 8 8 8 8;
                 padding: 16 -6 -6 16;
                 border-image: url(:/images/lcd_dark.png) 8 8 8 8;}
    QTableView::item { background: transparent; color: white; }
    QTableView::item:hover { background: none; }
"""


class MemoryLCDView(QtWidgets.QTableView):

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super(MemoryLCDView, self).__init__(parent)
        self.setGridStyle(Qt.PenStyle.NoPen)
        self.horizontalHeader().hide()
        self.horizontalHeader().setMinimumSectionSize(1)  # Minimum width
        self.verticalHeader().hide()
        self.verticalHeader().setMinimumSectionSize(1)  # Minimum height
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setStyleSheet(_LCD_STYLE_LIGHT)
        self.verticalScrollBar().setDisabled(True)
        self.horizontalScrollBar().setDisabled(True)
        self.setFrameStyle(QtWidgets.QFrame.Shape.NoFrame)
        #  Instance attributes that will be populated later
        self.memoryLCDProxyModel: MemoryLCDProxyModel | None = None
        self.LCDColumns: int | None = None
        self.LCDRows: int | None = None

    def setMemoryModel(self, memoryModel_: MemoryModel, hexStartAddress: str = '0x20080000', LCDColumns: int = 32, LCDRows: int = 6) -> None:
        """Sets the memory model and the number of columns and rows of the LCD"""
        self.memoryLCDProxyModel = MemoryLCDProxyModel()
        self.memoryLCDProxyModel.setSourceModel(memoryModel_, hexStartAddress, LCDColumns, LCDRows)
        super().setModel(self.memoryLCDProxyModel)
        self.LCDColumns = LCDColumns
        self.LCDRows = LCDRows
        self._resizeToContents()

    def setDarkMode(self, dark: bool) -> None:
        self.setStyleSheet(_LCD_STYLE_DARK if dark else _LCD_STYLE_LIGHT)
        if self.memoryLCDProxyModel is not None:
            self.memoryLCDProxyModel.setDarkMode(dark)

    def _resizeToContents(self) -> None:
        """Resize the columns and rows of the LCD to the size of its content and then fixes the total width and height of
        the LCD."""
        if self.LCDColumns is None or self.LCDRows is None:
            return
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.setFixedWidth(18 + 18 + 8 + sum([self.columnWidth(i) for i in range(self.LCDColumns)]))
        self.setFixedHeight(18 + 18 + 8 + sum([self.rowHeight(i) for i in range(self.LCDRows)]))
        # self.update()  # @todo: check that update is not required any more

    @override
    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        """Process the wheel event: zooms in and out whenever a CTRL+wheel event is triggered"""
        if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
            if self.memoryLCDProxyModel is not None:
                self.memoryLCDProxyModel.changeFontSize(event.angleDelta().y() // 120)
            self._resizeToContents()
        else:
            super(MemoryLCDView, self).wheelEvent(event)


if __name__ == "__main__":
    # To test this model, see the note in the header of this file
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    mainWindow.setGeometry(200, 200, 1000, 400)
    # Memory model
    memoryModel = MemoryModel(app)  # pyright: ignore[reportArgumentType]
    memoryModel.appendMemoryBank('ROM', '0x10010000', ['0x{:02X}'.format(i) for i in range(24)])
    memoryModel.appendMemoryBank('RAM', '0x20080000', ['0x{:02X}'.format(i) for i in range(65, 256)])
    # Memory LCD View
    memoryLCDView = MemoryLCDView(mainWindow)
    memoryLCDView.setMemoryModel(memoryModel, '0x20080000', 32, 6)
    # Show the main window and enter the main loop
    mainWindow.setCentralWidget(memoryLCDView)
    mainWindow.show()
    sys.exit(app.exec())
