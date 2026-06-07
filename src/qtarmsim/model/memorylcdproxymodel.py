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

# References
# http://stackoverflow.com/questions/21564976/how-to-create-a-proxy-model-that-would-flatten-nodes-of-a-qabstractitemmodel-int

from __future__ import annotations

from typing import Any

from typing_extensions import override

from PySide6 import QtCore, QtGui
from PySide6.QtCore import Qt, QModelIndex

from .common import InputToHex
from .memorybank import MemoryBank
from .memorymodel import MemoryModel, MemoryItem


class MemoryLCDProxyModel(QtCore.QAbstractProxyModel):

    @QtCore.Slot(QModelIndex, QModelIndex)  # pyright: ignore[reportAny]
    def sourceDataChanged(self, topLeft: QModelIndex, bottomRight: QModelIndex) -> None:
        if not topLeft.isValid() or not bottomRight.isValid():
            return
        lcdTopLeft = self.mapFromSource(topLeft)
        lcdBottomRight = self.mapFromSource(bottomRight)
        if lcdTopLeft.isValid() and lcdBottomRight.isValid():
            self.dataChanged.emit(lcdTopLeft, lcdBottomRight)

    # InputToHex helper object
    input2hex = InputToHex()

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super(MemoryLCDProxyModel, self).__init__(parent)
        # Set fonts
        QtGui.QFontDatabase.addApplicationFont(":/fonts/AlphaSmart3000.ttf")
        self.qFont = QtGui.QFont("AlphaSmart 3000")
        self.qFont.setPointSize(14)
        # Set brushes
        self.qBrush = QtGui.QBrush(QtGui.QColor(100, 100, 100, 30), Qt.BrushStyle.SolidPattern)
        self.qForeground: QtGui.QBrush | None = None
        #  Instance attributes that will be populated later
        self.LCDRows: int = 0
        self.LCDColumns: int = 0
        self.memoryBank: MemoryBank | None = None
        self.memoryBankIndex: QModelIndex | None = None
        self.hexStartAddress: str | None = None
        self.startAddress: int | None = None

    @override
    def sourceModel(self) -> MemoryModel:
        model = super().sourceModel()
        return model if isinstance(model, MemoryModel) else MemoryModel(self)

    @override
    def setSourceModel(self, model: MemoryModel, hexStartAddress: str = '0x2008000', LCDColumns: int = 32, LCDRows: int = 6) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        super().setSourceModel(model)
        self.hexStartAddress = hexStartAddress
        self.LCDColumns = LCDColumns
        self.LCDRows = LCDRows
        # --
        # self.sourceModel().connect(QtCore.SIGNAL("layoutChanged()"), self.layoutChanged)
        self.sourceModel().dataChanged.connect(self.sourceDataChanged)
        self.memoryBank = self.sourceModel().getMemoryBankWithHexAddress(hexStartAddress)
        self.memoryBankIndex = self.sourceModel().createIndex(self.memoryBank.slot, 0, self.memoryBank)
        self.startAddress = int(hexStartAddress, 16)

    @override
    def mapFromSource(self, index: QModelIndex) -> QModelIndex:  # pyright: ignore[reportIncompatibleMethodOverride]
        # If index is root or a memory bank item (parent is root), return QModelIndex()
        if not index.isValid() or not index.parent().isValid() or self.memoryBank is None:
            return QModelIndex()
        # At this point, index should point to a memory item
        item: MemoryItem = index.internalPointer()
        if item.memoryBank.slot != self.memoryBank.slot:
            return QModelIndex()
        # At this point, index should point to a memory item of the memory bank with self.hexStartAddress
        row = index.row()
        newRow = (row - (self.startAddress - self.memoryBank.startAddress)) // self.LCDColumns
        newColumn = (row - (self.startAddress - self.memoryBank.startAddress)) % self.LCDColumns
        if 0 <= newRow < self.LCDRows and 0 <= newColumn < self.LCDColumns:
            return self.index(newRow, newColumn, self.mapFromSource(index.parent()))
        else:
            return QtCore.QModelIndex()

    @override
    def mapToSource(self, index: QModelIndex) -> QModelIndex:  # pyright: ignore[reportIncompatibleMethodOverride]
        if not index.isValid() or self.memoryBank is None:
            return QModelIndex()
        memoryRow = index.row() * self.LCDColumns + index.column() + (self.startAddress - self.memoryBank.startAddress)
        return self.sourceModel().index(memoryRow, 0, self.memoryBankIndex)

    @override
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # pyright: ignore[reportIncompatibleMethodOverride]
        _ = parent
        return self.LCDRows

    @override
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # pyright: ignore[reportIncompatibleMethodOverride]
        _ = parent
        return self.LCDColumns

    @override
    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:  # pyright: ignore[reportIncompatibleMethodOverride]
        if not self.hasIndex(row, column, parent):
            return QModelIndex()  # invalid index -> return empty QModelIndex()
        if not parent.isValid():
            return self.createIndex(row, column)
        return QModelIndex()

    @override
    def parent(self, index: QModelIndex = QModelIndex()) -> QModelIndex:  # pyright: ignore[reportIncompatibleMethodOverride]
        _ = index
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
            sourceIndex = self.mapToSource(index)
            if self.memoryBank is not None and sourceIndex.isValid():
                item: MemoryItem = sourceIndex.internalPointer()
                return self._chr(item.hexValue)
            else:
                return " "
        elif role == Qt.ItemDataRole.BackgroundRole:
            return self.qBrush
        elif role == Qt.ItemDataRole.ForegroundRole:
            return self.qForeground
        elif role == Qt.ItemDataRole.FontRole:
            return self.qFont
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter
        else:
            return None

    @override
    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = Qt.ItemDataRole.EditRole) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        _ = section, orientation, role
        return None

    @override
    def flags(self, index: QModelIndex) -> Qt.ItemFlag:  # pyright: ignore[reportIncompatibleMethodOverride]
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled

    def setDarkMode(self, dark: bool) -> None:
        if dark:
            self.qBrush = QtGui.QBrush(Qt.BrushStyle.NoBrush)
            self.qForeground = QtGui.QBrush(QtGui.QColor('#ffffff'))
        else:
            self.qBrush = QtGui.QBrush(QtGui.QColor(100, 100, 100, 30), Qt.BrushStyle.SolidPattern)
            self.qForeground = None
        self.layoutChanged.emit()

    def changeFontSize(self, increment: int) -> None:
        myFontPointSize = self.qFont.pointSize()
        myFontPointSize += increment
        if myFontPointSize < 10:
            myFontPointSize = 10
        self.qFont.setPointSize(myFontPointSize)
