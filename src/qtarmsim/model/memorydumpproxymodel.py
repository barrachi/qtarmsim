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
#    python3 -m qtarmsim.model.memorydumpproxymodel
# -------------------------------------------------------------------------

# References
# http://stackoverflow.com/questions/21564976/how-to-create-a-proxy-model-that-would-flatten-nodes-of-a-qabstractitemmodel-int

from __future__ import annotations

import sys
from typing import Any

from typing_extensions import override

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QModelIndex

from .common import InputToHex, DataTypes
from .memorybank import MemoryBank
from .memorymodel import MemoryModel, MemoryItem
from ..utils import getMonoSpacedFont


class MemoryDumpProxyModel(QtCore.QAbstractProxyModel):

    @QtCore.Slot(QModelIndex, QModelIndex)  # pyright: ignore[reportAny]
    def sourceDataChanged(self, topLeft: QModelIndex, bottomRight: QModelIndex) -> None:
        if not topLeft.isValid() or not bottomRight.isValid():
            return
        mdTopLeft = self.mapFromSource(topLeft)
        mdBottomRight = self.mapFromSource(bottomRight)
        if mdTopLeft.isValid() and mdBottomRight.isValid():
            self.dataChanged.emit(mdTopLeft, mdBottomRight)

    # InputToHex helper object
    input2hex = InputToHex()

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        # Set fonts
        self.qFont = getMonoSpacedFont()
        self.qFontLast = getMonoSpacedFont()
        self.qFontLast.setWeight(QtGui.QFont.Weight.Black)
        # Set brushes
        self.qBrushPrevious = QtGui.QBrush(QtGui.QColor(192, 192, 255, 60), Qt.BrushStyle.SolidPattern)
        self.qBrushLast = QtGui.QBrush(QtGui.QColor(192, 192, 255, 100), Qt.BrushStyle.SolidPattern)
        # Instance attributes that will be populated later
        self.memoryBank: MemoryBank | None = None
        self.memoryBankIndex: QModelIndex | None = None

    def applyFontSize(self, size: int) -> None:
        self.qFont.setPointSize(size)
        self.qFontLast.setPointSize(size)
        self.layoutChanged.emit()

    @override
    def sourceModel(self) -> MemoryModel:
        model = super().sourceModel()
        return model if isinstance(model, MemoryModel) else MemoryModel(self)

    @override
    def setSourceModel(self, model: MemoryModel, memoryBankRow: int = 0) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        super().setSourceModel(model)
        self.sourceModel().dataChanged.connect(self.sourceDataChanged)
        self.memoryBank = self.sourceModel().getMemoryBankInSlot(memoryBankRow)
        self.memoryBankIndex = self.sourceModel().createIndex(self.memoryBank.slot, 0, self.memoryBank)

    @override
    def mapFromSource(self, sourceIndex: QModelIndex) -> QModelIndex:  # pyright: ignore[reportIncompatibleMethodOverride]
        # If the index is root or a memory bank item, return QModelIndex()
        if sourceIndex == QModelIndex() or sourceIndex.parent() == QModelIndex():
            return QModelIndex()
        # At this point, the index should point to a memory item
        item : MemoryItem = sourceIndex.internalPointer()
        if item.memoryBank.slot != self.memoryBank.slot:
            return QModelIndex()
        # index should point to a memory item of our memory bank, specified at setSourceModel()
        row = sourceIndex.row()
        newRow = row // 16
        newColumn = row % 16
        return self.index(newRow, newColumn, self.mapFromSource(sourceIndex.parent()))

    @override
    def mapToSource(self, index: QModelIndex) -> QModelIndex:  # pyright: ignore[reportIncompatibleMethodOverride]
        if not index.isValid() or index.column() == 16:
            return QModelIndex()
        memoryRow = index.row() * 16 + index.column()
        return self.sourceModel().index(memoryRow, 0, self.memoryBankIndex)

    @override
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # pyright: ignore[reportIncompatibleMethodOverride]
        if parent == QModelIndex():
            return int(self.memoryBank.length / 16)
        else:
            return 0

    @override
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # pyright: ignore[reportIncompatibleMethodOverride]
        _ = parent
        # bytes*16 | ASCII
        return 17

    @override
    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:  # pyright: ignore[reportIncompatibleMethodOverride]
        if not self.hasIndex(row, column, parent):
            return QModelIndex()  # invalid index -> return empty QModelIndex()
        if not parent.isValid():
            return self.createIndex(row, column, self.memoryBank.getMemoryItem(row*16))
        return QModelIndex()

    @override
    def parent(self, child: QModelIndex = QModelIndex()) -> QModelIndex:  # pyright: ignore[reportIncompatibleMethodOverride]
        _ = child
        return QModelIndex()

    @staticmethod
    def _chr(hexByte: str) -> str:
        n = int(hexByte, 16)
        if 32 <= n <= 126:
            return chr(n)
        else:
            return '·'

    @override
    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> Any:  # pyright: ignore[reportIncompatibleMethodOverride]
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() < 16:
                return self.mapToSource(index).internalPointer().hexValue[2:]
            else:
                chars = []
                byteRow = index.row() * 16
                for i in range(16):
                    try:
                        item : MemoryItem = self.memoryBank.getMemoryItem(byteRow + i)
                    except KeyError:
                        break
                    else:
                        chars.append(self._chr(item.hexValue))
                return ''.join(chars)
        elif role == Qt.ItemDataRole.ToolTipRole:
            if index.column() >= 16:
                return None
            dt = DataTypes(self.mapToSource(index).internalPointer().hexValue)
            return """
                <table>
                <tr><td align="right"> Hexadecimal:</td><td><b>{0}</b></td></tr>
                <tr><td align="right">      Binary:</td><td><b>{1}</b></td></tr>
                <tr><td align="right">Unsigned int:</td><td align="right"><b>{2}</b></td></tr>
                <tr><td align="right">     Integer:</td><td align="right"><b>{3}</b></td></tr>
                <tr><td align="right">       ASCII:</td><td><b>{4}</b></td></tr>
                <tr><td align="right">       UTF-8:</td><td><b>{5}</b></td></tr>
                </table>
            """.format(
                dt.hexadecimal,
                dt.binary,
                dt.uint,
                dt.int,
                dt.ascii,
                dt.utf8,
            )
        elif role == Qt.ItemDataRole.BackgroundRole:
            byteRow = index.row() * 16 + index.column()
            byteMemoryBankRow = self.memoryBank.slot
            # If the current byte is in modifiedBytes, return qBrushLast
            if (byteMemoryBankRow, byteRow) in self.sourceModel().modifiedBytes:
                return self.qBrushLast
            # If not, if the bytes are in previouslyModifiedBytes, return qBrushPrevious
            if (byteMemoryBankRow, byteRow) in self.sourceModel().previouslyModifiedBytes:
                return self.qBrushPrevious
            # If not, return None
            return None
        elif role == Qt.ItemDataRole.FontRole:
            byteRow = index.row() * 16 + index.column()
            byteMemoryBankRow = self.memoryBank.slot
            if (byteMemoryBankRow, byteRow) in self.sourceModel().modifiedBytes:
                return self.qFontLast
            else:
                return self.qFont
        else:
            return None

    @override
    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> Any:  # pyright: ignore[reportIncompatibleMethodOverride]
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                if section < 16:
                    return "{:X}".format(section)
                else:
                    return "ASCII"
            elif orientation == Qt.Orientation.Vertical:
                byteRow = section * 16
                return self.memoryBank.getMemoryItem(byteRow).hexAddress
        return None

    @override
    def flags(self, index: QModelIndex) -> Qt.ItemFlag:  # pyright: ignore[reportIncompatibleMethodOverride]
        # Column 16 cannot be changed
        if index.column() == 16:
            return Qt.ItemFlag.ItemIsEnabled
        # If we are in columns 1 to 16, check if the bank memory is ROM or RAM
        if self.memoryBank.memType == 'ROM':
            return Qt.ItemFlag.ItemIsEnabled
        else:
            return Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled

    @override
    def setData(self, index: QModelIndex, value: Any, role: Qt.ItemDataRole = Qt.ItemDataRole.EditRole) -> bool:  # pyright: ignore[reportIncompatibleMethodOverride]
        _ = role
        (hexValue, errMsg) = self.input2hex.convert(value, 8)
        if not hexValue:
            if errMsg:
                QtWidgets.QMessageBox.warning(None, self.tr("Input error"), errMsg)
            return False
        item = self.mapToSource(index).internalPointer()
        self.sourceModel().setByte(item.hexAddress, hexValue, True)
        return True


if __name__ == "__main__":
    # To test this model, see the note in the header of this file
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    mainWindow.setGeometry(200, 200, 1000, 400)
    # Memory model
    memoryModel = MemoryModel(app)
    memoryModel.appendMemoryBank('ROM', '0x10010000', ['0x{:02X}'.format(i) for i in range(24)])
    memoryModel.appendMemoryBank('RAM', '0x20020000', ['0x{:02X}'.format(i) for i in range(256)])
    # Memory dump proxy model
    memoryDumpProxyModel = MemoryDumpProxyModel()
    memoryDumpProxyModel.setSourceModel(memoryModel, 1)
    # Memory dump view
    memoryDumpView = QtWidgets.QTableView()
    memoryDumpView.setModel(memoryDumpProxyModel)
    memoryDumpView.resizeColumnsToContents()
    memoryDumpView.resizeRowsToContents()
    # Modify the memoryModel data after setting the proxy and the view
    memoryModel.appendMemoryBank('RAM', '0x40040000', ['0x{:02X}'.format(i) for i in range(256)])
    memoryModel.setByte('0x20020000', '0xCC')
    memoryModel.stepHistory()
    memoryModel.setByte('0x20020002', '0xDD')
    # Show the main window and enter the main loop
    mainWindow.setCentralWidget(memoryDumpView)
    mainWindow.show()
    sys.exit(app.exec())
