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

from PySide import QtGui, QtCore
from PySide.QtCore import Qt
from qtarmsim.widget.myqtreeview import MyQTreeView

from . memorymodel import MemoryModel
from . common import InputToHex, getMonoSpacedFont


class MemoryByWordProxyModel(QtGui.QSortFilterProxyModel):
    
    # InputToHex helper object
    input2hex = InputToHex()

    @QtCore.Slot(QtCore.QModelIndex, QtCore.QModelIndex)
    def sourceDataChanged(self, topLeft, bottomRight):
        self.dataChanged.emit(self.mapFromSource(topLeft), \
                              self.mapFromSource(bottomRight))

    def __init__(self, parent=None):
        super(MemoryByWordProxyModel, self).__init__(parent)
        # Set fonts
        self.qFont = getMonoSpacedFont()
        self.qFontLast = getMonoSpacedFont()
        self.qFontLast.setWeight(QtGui.QFont.Black)
        # Set brushes
        self.qBrushPrevious = QtGui.QBrush(QtGui.QColor(192, 192, 255, 60), Qt.SolidPattern)
        self.qBrushLast = QtGui.QBrush(QtGui.QColor(192, 192, 255, 100), Qt.SolidPattern) 

    def setSourceModel(self, model):
        super(MemoryByWordProxyModel, self).setSourceModel(model)
        self.sourceModel().dataChanged.connect(self.sourceDataChanged)

    def filterAcceptsRow(self, sourceRow, sourceParent):
        try:
            firstColumnData = sourceParent.internalPointer().child(sourceRow).data(0)
        except AttributeError:
            return True
        if  firstColumnData[0:2] != "0x":
            return True
        elif firstColumnData[-1:] in ('0', '4', '8', 'C', 'c'):
            return True
        else:
            return False
         
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        sourceModelIndex = self.mapToSource(index)
        item = sourceModelIndex.internalPointer()
        byteMemoryBankRow = sourceModelIndex.parent().row()
        byteRow = sourceModelIndex.row()
        # Memory bank
        if item.parent() == self.sourceModel().rootItem:
            if role == Qt.DisplayRole:
                return item.data(index.column())
            elif role == Qt.FontRole:
                return self.qFont
            return None
        # Memory address
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return item.data(0)
            else:
                hexBytes = []
                byteMemoryBank = sourceModelIndex.parent().internalPointer()
                byteRow = sourceModelIndex.row()
                for i in range(3,-1,-1):
                    hexBytes.append(byteMemoryBank.child(byteRow + i).data(1)[2:])
                return '0x' + ''.join(hexBytes)
        elif role == Qt.BackgroundRole:
            # If any of the bytes is in modifiedBytes, return qBrushLast
            for i in range(4):
                if (byteMemoryBankRow, byteRow+i) in self.sourceModel().modifiedBytes:
                    return self.qBrushLast
            # If not, if any of the bytes is in previouslyModifiedBytes, return qBrushPrevious
            for i in range(4):
                if (byteMemoryBankRow, byteRow+i) in self.sourceModel().previouslyModifiedBytes:
                    return self.qBrushPrevious
            # If not, return None
            return None
        elif role == Qt.FontRole:
            # If any of the bytes is in modifiedBytes, return qFontLast
            for i in range(4):
                if (byteMemoryBankRow, byteRow+i) in self.sourceModel().modifiedBytes:
                    return self.qFontLast
            else:
                return self.qFont
        else:
            return None

    def flags(self, index):
        if not index.isValid():
            return False
        sourceModelIndex = self.mapToSource(index)
        item = sourceModelIndex.internalPointer()
        if item.parent() == self.sourceModel().rootItem:
            return Qt.ItemIsEnabled
        if  index.column() == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if item.parent().data(0)[:3] == 'ROM':
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def setData(self, index, value, role = Qt.EditRole):
        (hexValue, err_msg) = self.input2hex.convert(value)
        if not hexValue:
            if err_msg:
                QtGui.QMessageBox.warning(None, self.trUtf8("Input error"), err_msg)
            return False
        sourceModelIndex = self.mapToSource(index)
        item = sourceModelIndex.internalPointer()
        hexAddress = item.data(0)
        self.sourceModel().setWord(hexAddress, hexValue, True)
        return True


if __name__ == "__main__":
    #
    # To test this module, execute from qtarmsim upper directory the following command:
    #
    #    python3 -m qtarmsim.model.memorybywordproxymodel
    #
    app = QtGui.QApplication(sys.argv)
    mainWindow = QtGui.QMainWindow()
    # Memory model
    memoryModel = MemoryModel(app)
    memoryModel.appendMemoryBank('ROM', '0x10010000', ['0x{:02X}'.format(i) for i in range(24)])
    memoryModel.appendMemoryBank('RAM', '0x20020000', ['0x{:02X}'.format(i) for i in range(256)])
    # filterProxy
    filterProxy = MemoryByWordProxyModel(app)
    filterProxy.setSourceModel(memoryModel)
    # treeViewMemory
    treeViewMemory = QtGui.QTreeView()
    treeViewMemory.setModel(filterProxy)
    treeViewMemory.expandAll()
    treeViewMemory.resizeColumnToContents(0)
    treeViewMemory.resizeColumnToContents(1)
    # modify memoryModel data after setting the proxy and the view
    memoryModel.appendMemoryBank('RAM', '0x40040000', ['0x{:02X}'.format(i) for i in range(256)])
    memoryModel.setWord('0x10010000', '0xCCDDEEFF')
    memoryModel.stepHistory()
    memoryModel.setWord('0x10010004', '0xCCDDEEFF')
    # Show main window and enter main loop
    mainWindow.setCentralWidget(treeViewMemory)
    mainWindow.show()
    sys.exit(app.exec_())
