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

import sys

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import Qt

from .common import InputToHex, DataTypes
from .memorymodel import MemoryModel
from ..utils import getMonoSpacedFont


class MemoryDumpProxyModel(QtCore.QAbstractProxyModel):

    @QtCore.Slot(QtCore.QModelIndex, QtCore.QModelIndex)
    def sourceDataChanged(self, topLeft, bottomRight):
        self.dataChanged.emit(self.mapFromSource(topLeft),
                              self.mapFromSource(bottomRight))

    # InputToHex helper object
    input2hex = InputToHex()

    def __init__(self, parent=None):
        super(MemoryDumpProxyModel, self).__init__(parent)
        # Set fonts
        self.qFont = getMonoSpacedFont()
        self.qFontLast = getMonoSpacedFont()
        self.qFontLast.setWeight(QtGui.QFont.Black)
        # Set brushes
        self.qBrushPrevious = QtGui.QBrush(QtGui.QColor(192, 192, 255, 60), Qt.SolidPattern)
        self.qBrushLast = QtGui.QBrush(QtGui.QColor(192, 192, 255, 100), Qt.SolidPattern)

    def setSourceModel(self, model, memoryBankRow=0):
        super(MemoryDumpProxyModel, self).setSourceModel(model)
        self.memoryBankRow = memoryBankRow
        self.memoryBankItem = self.sourceModel().rootItem.child(memoryBankRow)
        self.memoryBankIndex = self.sourceModel().createIndex(memoryBankRow, 0, self.memoryBankItem)
        self.memoryBankStartAddress = int(self.memoryBankItem.data(0).split(" ")[1], 16)
        self.sourceModel().dataChanged.connect(self.sourceDataChanged)

    def mapFromSource(self, index):
        # If index is root or a memory bank item, return QModelIndex() 
        if index == QtCore.QModelIndex() or index.parent() == QtCore.QModelIndex:
            return QtCore.QModelIndex()
        # At this point, index should point to a memory address
        memoryBankRow = index.parent().row()
        if memoryBankRow != self.memoryBankRow:
            return QtCore.QModelIndex()
        # At this point, index should point to a memory address of the memory bank specified at setSourceModel()
        memoryAddress = int(index.internalPointer().data(0), 16)
        row = int((memoryAddress - self.memoryBankStartAddress) / 16)
        column = (memoryAddress - self.memoryBankStartAddress) % 16
        return self.createIndex(row, column)

    def mapToSource(self, index):
        if not index.isValid() or index.column() == 16:
            return QtCore.QModelIndex()
        memoryRow = index.row() * 16 + index.column()
        return self.sourceModel().index(memoryRow, 0, self.memoryBankIndex)

    def rowCount(self, parent):
        if not parent.isValid():
            return int(self.memoryBankItem.childCount() / 16)
        else:
            return 0

    def columnCount(self, parent):
        # bytes*16 | ASCII 
        return 17

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
            if index.column() < 16:
                return self.mapToSource(index).internalPointer().data(1)[2:]
            else:
                chars = []
                byteRow = index.row() * 16
                for i in range(16):
                    try:
                        item = self.memoryBankItem.child(byteRow + i)
                    except KeyError:
                        break
                    chars.append(self._chr(item.data(1)[2:]))
                return ''.join(chars)
        elif role == Qt.ToolTipRole:
            if index.column() >= 16:
                return None
            dt = DataTypes("0x{}".format(self.mapToSource(index).internalPointer().data(1)[2:]))
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
        elif role == Qt.BackgroundRole:
            byteRow = index.row() * 16 + index.column()
            byteMemoryBankRow = self.memoryBankRow
            # If the current byte is in modifiedBytes, return qBrushLast
            if (byteMemoryBankRow, byteRow) in self.sourceModel().modifiedBytes:
                return self.qBrushLast
            # If not, if the bytes is in previouslyModifiedBytes, return qBrushPrevious
            if (byteMemoryBankRow, byteRow) in self.sourceModel().previouslyModifiedBytes:
                return self.qBrushPrevious
            # If not, return None
            return None
        elif role == Qt.FontRole:
            byteRow = index.row() * 16 + index.column()
            byteMemoryBankRow = self.memoryBankRow
            if (byteMemoryBankRow, byteRow) in self.sourceModel().modifiedBytes:
                return self.qFontLast
            else:
                return self.qFont
        else:
            return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section < 16:
                    return "{:X}".format(section)
                else:
                    return "ASCII"
            elif orientation == Qt.Vertical:
                byteRow = section * 16
                return self.memoryBankItem.child(byteRow).data(0)

    def flags(self, index):
        if not index.isValid():
            return False
        # Column 16 can not be changed
        if index.column() == 16:
            return Qt.ItemIsEnabled
        # If we are in columns 1 to 16, check if the bank memory is ROM or RAM
        if self.memoryBankItem.data(0)[:3] == 'ROM':
            return Qt.ItemIsEnabled
        else:
            return Qt.ItemIsEditable | Qt.ItemIsEnabled

    def setData(self, index, value, role=Qt.EditRole):
        (hexValue, errMsg) = self.input2hex.convert(value, 8)
        if not hexValue:
            if errMsg:
                QtWidgets.QMessageBox.warning(None, self.tr("Input error"), errMsg)
            return False
        item = self.mapToSource(index).internalPointer()
        hexAddress = item.data(0)
        self.sourceModel().setByte(hexAddress, hexValue, True)
        return True


if __name__ == "__main__":
    #
    # To test this module, execute from qtarmsim upper directory the following command:
    #
    #    python3 -m qtarmsim.model.memorydumpproxymodel
    #
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
    # Show main window and enter main loop
    mainWindow.setCentralWidget(memoryDumpView)
    mainWindow.show()
    sys.exit(app.exec_())
