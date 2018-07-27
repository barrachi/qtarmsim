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

from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtCore import Qt

from .common import InputToHex, DataTypes
from .memorymodel import MemoryModel
from ..utils import getMonoSpacedFont


class MemoryByWordProxyModel(QtCore.QSortFilterProxyModel):
    # InputToHex helper object
    input2hex = InputToHex()

    @QtCore.Slot(QtCore.QModelIndex, QtCore.QModelIndex)
    def sourceDataChanged(self, topLeft, bottomRight):
        self.dataChanged.emit(self.mapFromSource(topLeft),
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
        if firstColumnData[0:2] != "0x":
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
                for i in range(3, -1, -1):
                    hexBytes.append(byteMemoryBank.child(byteRow + i).data(1)[2:])
                return '0x' + ''.join(hexBytes)
        elif role == Qt.ToolTipRole:
            if index.column() == 0:
                return None
            hexBytes = []
            byteMemoryBank = sourceModelIndex.parent().internalPointer()
            byteRow = sourceModelIndex.row()
            for i in range(3, -1, -1):
                hexBytes.append(byteMemoryBank.child(byteRow + i).data(1)[2:])
            hex_value = '0x' + ''.join(hexBytes)
            dt = DataTypes(hex_value)
            html = """
                <table>
            """
            html += """
                <tr><th colspan="5" style="color: 'black'; background-color: 'gray'">1 Word</th></tr>
                <tr><td align="right"> Hexadecimal:</td><td colspan="4"><b>{0}</b></td></tr>
                <tr><td align="right">Unsigned int:</td><td colspan="4"><b>{1}</b></td></tr>
                <tr><td align="right">     Integer:</td><td colspan="4"><b>{2}</b></td></tr>
                <tr><td align="right">       ASCII:</td><td colspan="4"><b>{3}</b></td></tr>
                <tr><td align="right">       UTF-8:</td><td colspan="4"><b>{4}</b></td></tr>
                <tr><td align="right">      UTF-32:</td><td colspan="4"><b>{5}</b></td></tr>
                """.format(
                dt.hexadecimal,
                dt.uint,
                dt.int,
                dt.ascii,
                dt.utf8,
                dt.utf32
            )
            half2_hex_value = '0x' + ''.join(hexBytes[0:2])
            half1_hex_value = '0x' + ''.join(hexBytes[2:4])
            dth2 = DataTypes(half2_hex_value)
            dth1 = DataTypes(half1_hex_value)
            html += """
                <tr><th colspan="5" style="color: 'black'; background-color: 'gray'">2 Half-words</th></tr>
                <tr><td align="right"> Hexadecimal:</td> <td colspan="2"><b>{}</b></td> <td colspan="2"><b>{}</b></td></tr>
                <tr><td align="right">Unsigned int:</td> <td colspan="2"><b>{}</b></td> <td colspan="2"><b>{}</b></td></tr>
                <tr><td align="right">     Integer:</td> <td colspan="2"><b>{}</b></td> <td colspan="2"><b>{}</b></td></tr>
                <tr><td align="right">       UTF-8:</td> <td colspan="2"><b>{}</b></td> <td colspan="2"><b>{}</b></td></tr>
                """.format(
                dth1.hexadecimal,
                dth2.hexadecimal,
                dth1.uint,
                dth2.uint,
                dth1.int,
                dth2.int,
                dth1.utf8,
                dth2.utf8,
            )
            byte4_hex_value = '0x' + hexBytes[0]
            byte3_hex_value = '0x' + hexBytes[1]
            byte2_hex_value = '0x' + hexBytes[2]
            byte1_hex_value = '0x' + hexBytes[3]
            dtb4 = DataTypes(byte4_hex_value)
            dtb3 = DataTypes(byte3_hex_value)
            dtb2 = DataTypes(byte2_hex_value)
            dtb1 = DataTypes(byte1_hex_value)
            html += """
                <tr><th colspan="5" style="color: 'black'; background-color: 'gray'">4 bytes</th></tr>
                <tr><td align="right"> Hexadecimal:</td> <td ><b>{}</b></td> <td ><b>{}</b></td> <td ><b>{}</b></td> <td ><b>{}</b></td> </tr>
                <tr><td align="right"> Binary:</td> <td ><b>{}</b></td> <td ><b>{}</b></td> <td ><b>{}</b></td> <td ><b>{}</b></td> </tr>
                <tr><td align="right">Unsigned int:</td> <td ><b>{}</b></td> <td ><b>{}</b></td> <td ><b>{}</b></td> <td ><b>{}</b></td> </tr>
                <tr><td align="right">     Integer:</td> <td ><b>{}</b></td> <td ><b>{}</b></td> <td ><b>{}</b></td> <td ><b>{}</b></td> </tr>
                <tr><td align="right">       ASCII:</td> <td ><b>{}</b></td> <td ><b>{}</b></td> <td ><b>{}</b></td> <td ><b>{}</b></td> </tr>
                """.format(
                dtb1.hexadecimal,
                dtb2.hexadecimal,
                dtb3.hexadecimal,
                dtb4.hexadecimal,
                dtb1.binary,
                dtb2.binary,
                dtb3.binary,
                dtb4.binary,
                dtb1.uint,
                dtb2.uint,
                dtb3.uint,
                dtb4.uint,
                dtb1.int,
                dtb2.int,
                dtb3.int,
                dtb4.int,
                dtb1.ascii,
                dtb2.ascii,
                dtb3.ascii,
                dtb4.ascii,
            )
            html += """
                </table>
            """
            return html
        elif role == Qt.BackgroundRole:
            # If any of the bytes is in modifiedBytes, return qBrushLast
            for i in range(4):
                if (byteMemoryBankRow, byteRow + i) in self.sourceModel().modifiedBytes:
                    return self.qBrushLast
            # If not, if any of the bytes is in previouslyModifiedBytes, return qBrushPrevious
            for i in range(4):
                if (byteMemoryBankRow, byteRow + i) in self.sourceModel().previouslyModifiedBytes:
                    return self.qBrushPrevious
            # If not, return None
            return None
        elif role == Qt.FontRole:
            # If any of the bytes is in modifiedBytes, return qFontLast
            for i in range(4):
                if (byteMemoryBankRow, byteRow + i) in self.sourceModel().modifiedBytes:
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
        if index.column() == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if item.parent().data(0)[:3] == 'ROM':
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def setData(self, index, value, role=Qt.EditRole):
        (hexValue, err_msg) = self.input2hex.convert(value)
        if not hexValue:
            if err_msg:
                QtWidgets.QMessageBox.warning(None, self.tr("Input error"), err_msg)
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
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    # Memory model
    memoryModel = MemoryModel(app)
    memoryModel.appendMemoryBank('ROM', '0x10010000', ['0x{:02X}'.format(i) for i in range(24)])
    memoryModel.appendMemoryBank('RAM', '0x20020000', ['0x{:02X}'.format(i) for i in range(256)])
    # filterProxy
    filterProxy = MemoryByWordProxyModel(app)
    filterProxy.setSourceModel(memoryModel)
    # treeViewMemory
    treeViewMemory = QtWidgets.QTreeView()
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
