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

# References
# http://stackoverflow.com/questions/21564976/how-to-create-a-proxy-model-that-would-flatten-nodes-of-a-qabstractitemmodel-int

#
# To test this module, execute from qtarmsim upper directory the following command:
#
#    python3 -m qtarmsim.widget.memorylcdview
#

from PySide2 import QtCore, QtGui
from PySide2.QtCore import Qt

from .common import InputToHex


class MemoryLCDProxyModel(QtCore.QAbstractProxyModel):

    @QtCore.Slot(QtCore.QModelIndex, QtCore.QModelIndex)
    def sourceDataChanged(self, topLeft, bottomRight):
        self.dataChanged.emit(self.mapFromSource(topLeft),
                              self.mapFromSource(bottomRight))

    # InputToHex helper object
    input2hex = InputToHex()

    def __init__(self, parent=None):
        super(MemoryLCDProxyModel, self).__init__(parent)
        # ------------------------------------------------------------
        #  Instance attributes that will be properly initialized later
        # ------------------------------------------------------------
        self.hexStartAddress = None
        self.startAddress = None
        self.memoryBankItem = None
        self.memoryBankIndex = None
        self.memoryBankStartAddress = None
        # ------------------------------------------------------------
        # Set font
        QtGui.QFontDatabase.addApplicationFont(":/fonts/01 Digit.ttf")
        self.qFont = QtGui.QFont("01 digit")
        self.qFont.setPointSize(10)
        # Set brush
        self.qBrush = QtGui.QBrush(QtGui.QColor(100, 100, 100, 30), Qt.SolidPattern)
        # Initial values of LCDRows, LCDColumns, and memoryBankRow
        self.LCDRows = 0
        self.LCDColumns = 0
        self.memoryBankRow = -1

    def setSourceModel(self, model, hexStartAddress, LCDColumns, LCDRows):
        super(MemoryLCDProxyModel, self).setSourceModel(model)
        self.hexStartAddress = hexStartAddress
        self.startAddress = int(self.hexStartAddress, 16)
        self.LCDColumns = LCDColumns
        self.LCDRows = LCDRows
        self.sourceModel().connect(QtCore.SIGNAL("layoutChanged()"), self.layoutChanged)
        self.sourceModel().dataChanged.connect(self.sourceDataChanged)

    @QtCore.Slot()
    def layoutChanged(self):
        """
        It updates the memoryBank information. It should be triggered by a layoutChanged signal from source model.
        """
        (self.memoryBankRow, sourceModelMemoryBank) = self.sourceModel().getMemoryBank(self.hexStartAddress)
        if self.memoryBankRow != -1:
            self.memoryBankItem = self.sourceModel().rootItem.child(self.memoryBankRow)
            self.memoryBankIndex = self.sourceModel().createIndex(self.memoryBankRow, 0, self.memoryBankItem)
            self.memoryBankStartAddress = int(self.memoryBankItem.data(0).split(" ")[1], 16)
            self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.LCDRows - 1, self.LCDColumns - 1))

    def mapFromSource(self, index):
        # If index is root or a memory bank item, return QModelIndex()
        if index == QtCore.QModelIndex() or index.parent() == QtCore.QModelIndex or self.memoryBankRow == -1:
            return QtCore.QModelIndex()
        # At this point, index should point to a memory address
        memoryBankRow = index.parent().row()
        if memoryBankRow != self.memoryBankRow:
            return QtCore.QModelIndex()
        # At this point, index should point to a memory address of the memory bank specified at setSourceModel()
        memoryAddress = int(index.internalPointer().data(0), 16)
        row = int((memoryAddress - self.startAddress) / self.LCDColumns)
        column = (memoryAddress - self.startAddress) % self.LCDColumns
        if 0 <= row < self.LCDRows and 0 <= column < self.LCDColumns:
            return self.createIndex(row, column)
        else:
            return QtCore.QModelIndex()

    def mapToSource(self, index):
        if not index.isValid() or self.memoryBankRow == -1:
            return QtCore.QModelIndex()
        memoryRow = index.row() * self.LCDColumns + index.column() + (self.startAddress - self.memoryBankStartAddress)
        return self.sourceModel().index(memoryRow, 0, self.memoryBankIndex)

    def rowCount(self, parent):
        return self.LCDRows

    def columnCount(self, parent):
        return self.LCDColumns

    def index(self, row, column, parent):
        if parent.isValid():
            return QtCore.QModelIndex()
        return self.createIndex(row, column)

    def parent(self, index):
        return QtCore.QModelIndex()

    @staticmethod
    def _chr(hexByte):
        n = int(hexByte, 16)
        if 32 <= n <= 126:
            return chr(n)
        else:
            return '·'

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if self.memoryBankRow != -1 and self.mapToSource(index).isValid():
                return self._chr(self.mapToSource(index).internalPointer().data(1)[2:])
            else:
                return " "
        elif role == Qt.BackgroundRole:
            return self.qBrush
        elif role == Qt.FontRole:
            return self.qFont
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        else:
            return None

    def headerData(self, section, orientation, role):
        return None

    def flags(self, index):
        if not index.isValid():
            return False
        return Qt.ItemIsEnabled

    def changeFontSize(self, increment):
        myFontPointSize = self.qFont.pointSize()
        myFontPointSize += increment
        if myFontPointSize < 10:
            myFontPointSize = 10
        self.qFont.setPointSize(myFontPointSize)
