# -*- coding: utf-8 -*-

###########################################################################
#                                                                         #
#  This file is part of QtARMSim.                                         #
#                                                                         #
#  QtARMSim is free software: you can redistribute it and/or modify       #
#  it under the terms of the GNU General Public License as published by   #
#  the Free Software Foundation; either version 3 of the License or       #
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
#    python3 -m qtarmsim.model.memorybywordproxymodel
# -------------------------------------------------------------------------

from __future__ import annotations

import sys
from typing import cast

from PySide6 import QtGui, QtCore, QtWidgets
from PySide6.QtCore import Qt, QModelIndex
from typing_extensions import override

from .common import InputToHex, DataTypes
from .memorybank import MemoryBank
from .memorybank import MemoryItem
from .memorymodel import MemoryModel
from .memorybankitem import MemoryBankItem
from ..utils import getMonoSpacedFont


class MemoryByWordProxyModel(QtCore.QAbstractProxyModel):

    @QtCore.Slot(QtCore.QModelIndex, QtCore.QModelIndex)  # pyright: ignore[reportAny]
    def sourceDataChanged(self, topLeft: QModelIndex, bottomRight: QModelIndex) -> None:
        if not topLeft.isValid() or not bottomRight.isValid():
            return
        mwTopLeft = self.mapFromSource(topLeft)
        mwBottomRight = self.mapFromSource(bottomRight)
        if mwTopLeft.isValid() and mwBottomRight.isValid():
            # Extend to column 1 so the data column refreshes too
            mwBottomRight = self.index(mwBottomRight.row(), 1, mwBottomRight.parent())
            self.dataChanged.emit(mwTopLeft, mwBottomRight)

    # InputToHex helper object
    input2hex: InputToHex = InputToHex()

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        # Set fonts
        self.qFont: QtGui.QFont = getMonoSpacedFont()
        self.qFontLast: QtGui.QFont = getMonoSpacedFont()
        self.qFontLast.setWeight(QtGui.QFont.Weight.Black)
        # Set brushes
        self.qBrushPrevious: QtGui.QBrush = QtGui.QBrush(QtGui.QColor(192, 192, 255, 60), Qt.BrushStyle.SolidPattern)
        self.qBrushLast: QtGui.QBrush = QtGui.QBrush(QtGui.QColor(192, 192, 255, 100), Qt.BrushStyle.SolidPattern)

    def applyFontSize(self, size: int) -> None:
        self.qFont.setPointSize(size)
        self.qFontLast.setPointSize(size)
        self.layoutChanged.emit()

    @override
    def sourceModel(self) -> MemoryModel:
        model = super().sourceModel()
        return model if isinstance(model, MemoryModel) else MemoryModel(self)

    @override
    def setSourceModel(self, model: MemoryModel) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        super().setSourceModel(model)
        _ = self.sourceModel().dataChanged.connect(self.sourceDataChanged)  # pyright: ignore[reportAny]

    @override
    def mapFromSource(self, index: QModelIndex, /) -> QModelIndex:  # pyright: ignore[reportIncompatibleMethodOverride]
        if not index.isValid():
            return QModelIndex()
        item: object = cast(object, index.internalPointer())
        if isinstance(item, MemoryBankItem):
            newRow, newColumn = index.row(), index.column()
        elif isinstance(item, MemoryItem):
            newRow = index.row() // 4
            newColumn = index.column()
        else:
            raise RuntimeError(
                'MemoryByWordProxyModel mapFromSource() only supports MemoryBankItem and MemoryItem items')
        return self.index(newRow, newColumn, self.mapFromSource(index.parent()))

    @override
    def mapToSource(self, index: QModelIndex) -> QModelIndex:  # pyright: ignore[reportIncompatibleMethodOverride]
        if not index.isValid():
            return QModelIndex()
        item: object = cast(object, index.internalPointer())
        if isinstance(item, MemoryBankItem):
            newRow = index.row()
        elif isinstance(item, MemoryItem):
            newRow = index.row() * 4
        else:
            raise RuntimeError(
                'MemoryByWordProxyModel mapToSource() only supports MemoryBankItem and MemoryItem items')
        return self.sourceModel().index(newRow, 0, self.mapToSource(index.parent()))

    @override
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # pyright: ignore[reportIncompatibleMethodOverride]
        if not parent.isValid():
            return self.sourceModel().getNumberOfMemoryBanks()
        item: object = cast(object, parent.internalPointer())
        if isinstance(item, MemoryBankItem):
            return self.sourceModel().getMemoryBankInSlot(cast(int, item.slot)).length // 4
        elif isinstance(item, MemoryItem):
            return 1
        raise RuntimeError(
            'MemoryByWordProxyModel rowCount() only supports MemoryBankItem and MemoryItem items')

    @override
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # pyright: ignore[reportIncompatibleMethodOverride]
        _ = parent
        return 2

    @override
    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:  # pyright: ignore[reportIncompatibleMethodOverride]
        if not self.hasIndex(row, column, parent):
            return QModelIndex()  # invalid index -> return empty QModelIndex()
        if not parent.isValid():
            return self.createIndex(row, column, MemoryBankItem(self.sourceModel().getMemoryBankInSlot(row)))
        else:
            memoryBankItem: object = cast(object, parent.internalPointer())
            if isinstance(memoryBankItem, MemoryBankItem):
                return self.createIndex(row, column, cast(MemoryBank, memoryBankItem.memoryBank).getMemoryItem(row * 4))
        raise RuntimeError('MemoryByWordProxyModel index() only supports MemoryBankItem and MemoryItem items')

    @override
    def parent(self, index: QModelIndex = QModelIndex()) -> QModelIndex:  # pyright: ignore[reportIncompatibleMethodOverride]
        if not index.isValid():
            return QModelIndex()
        item: object = cast(object, index.internalPointer())
        if isinstance(item, MemoryBankItem):
            return QModelIndex()
        elif isinstance(item, MemoryItem):
            bank = cast(MemoryBank, item.parent)
            return self.createIndex(bank.slot, 0, MemoryBankItem(self.sourceModel().getMemoryBankInSlot(bank.slot)))
        raise RuntimeError('MemoryByWordProxyModel parent() only supports MemoryBankItem and MemoryItem items')

    @override
    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> object:  # pyright: ignore[reportIncompatibleMethodOverride]
        if not index.isValid():
            return None
        sourceModelIndex = self.mapToSource(index)
        if not sourceModelIndex.isValid():
            return None
        item: object = cast(object, sourceModelIndex.internalPointer())
        if item is None:
            return None
        # Memory bank
        if isinstance(item, MemoryBankItem):
            if role == Qt.ItemDataRole.DisplayRole:
                memoryBank = self.sourceModel().getMemoryBankInSlot(cast(int, item.slot))
                return (memoryBank.memType, memoryBank.hexStartAddress)[index.column()]
            elif role == Qt.ItemDataRole.FontRole:
                return self.qFont
            return None
        # Raise error if not memory item
        if not isinstance(item, MemoryItem):
            raise RuntimeError('MemoryByWordProxyModel pdata() only supports MemoryBank and MemoryItem items')
        # Memory item
        byteMemoryBank: MemoryBank = cast(MemoryBank, sourceModelIndex.parent().internalPointer())
        byteRow = sourceModelIndex.row()
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return item.hexAddress
            else:
                hexBytes: list[str] = []
                for i in range(3, -1, -1):
                    hexBytes.append(byteMemoryBank.bytes[byteRow + i][2:])
                return '0x' + ''.join(hexBytes)
        elif role == Qt.ItemDataRole.ToolTipRole:
            if index.column() == 0:
                return None
            hexBytes = []
            for i in range(3, -1, -1):
                hexBytes.append(byteMemoryBank.bytes[byteRow + i][2:])
            hexValue = '0x' + ''.join(hexBytes)
            dt = DataTypes(hexValue)
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
        elif role == Qt.ItemDataRole.BackgroundRole:
            # If any of the bytes is in modifiedBytes, return qBrushLast
            for i in range(4):
                if (byteMemoryBank.slot, byteRow + i) in self.sourceModel().modifiedBytes:
                    return self.qBrushLast
            # If not, if any of the bytes is in previouslyModifiedBytes, return qBrushPrevious
            for i in range(4):
                if (byteMemoryBank.slot, byteRow + i) in self.sourceModel().previouslyModifiedBytes:
                    return self.qBrushPrevious
            # If not, return None
            return None
        elif role == Qt.ItemDataRole.FontRole:
            # If any of the bytes is in modifiedBytes, return qFontLast
            for i in range(4):
                if (byteMemoryBank.slot, byteRow + i) in self.sourceModel().modifiedBytes:
                    return self.qFontLast
            else:
                return self.qFont
        else:
            return None

    # def flags(self, index):
    #     if not index.isValid():
    #         return False
    #     sourceModelIndex = self.mapToSource(index)
    #     item = sourceModelIndex.internalPointer()
    #     if isinstance(item, MemoryBankItem):
    #         return Qt.ItemFlag.ItemIsEnabled
    #     # Raise error if not memory item
    #     if not isinstance(item, MemoryItem):
    #         raise RuntimeError('MemoryByWordProxyModel pdata() only supports MemoryBank and MemoryItem items')
    #     if index.column() == 0:
    #         return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
    #     if item.parent().memType == 'ROM':
    #         return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
    #     return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable

    @override
    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> str | None:  # pyright: ignore[reportIncompatibleMethodOverride]
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return ('Address', 'Data')[section]
        return None

    @override
    def setData(self, index: QModelIndex, value: str, role: Qt.ItemDataRole = Qt.ItemDataRole.EditRole) -> bool:  # pyright: ignore[reportIncompatibleMethodOverride]
        _ = role
        (hexValue, err_msg) = self.input2hex.convert(value)
        if not hexValue:
            if err_msg:
                _ = QtWidgets.QMessageBox.warning(None, self.tr("Input error"), err_msg)
            return False
        sourceModelIndex = self.mapToSource(index)
        item: object = cast(object, sourceModelIndex.internalPointer())
        hexAddress = cast(MemoryItem, item).hexAddress
        self.sourceModel().setWord(hexAddress, hexValue, True)
        return True


if __name__ == "__main__":
    # To test this model, see the note in the header of this file
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    # Memory model
    memoryModel = MemoryModel()
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
    # # modify memoryModel data after setting the proxy and the view
    # memoryModel.appendMemoryBank('RAM', '0x40040000', ['0x{:02X}'.format(i) for i in range(256)])
    # memoryModel.setWord('0x10010000', '0xCCDDEEFF')
    # memoryModel.stepHistory()
    # memoryModel.setWord('0x10010004', '0xCCDDEEFF')
    # Show main window and enter the main loop
    mainWindow.setCentralWidget(treeViewMemory)
    mainWindow.show()
    sys.exit(app.exec())
