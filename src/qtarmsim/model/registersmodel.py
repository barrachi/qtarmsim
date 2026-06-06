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


from __future__ import annotations

from typing import TYPE_CHECKING, cast

from typing_extensions import override

if TYPE_CHECKING:
    from typing import ClassVar

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QModelIndex, QPersistentModelIndex

from .common import InputToHex, DataTypes
from .simpletreemodel import TreeModel, TreeItem
from ..utils import getMonoSpacedFont


class RegisterBank:
    def __init__(self, name: str, registers_data: list[list[str]]) -> None:
        self.name: str = name
        self.registers_data: list[list[str]] = registers_data


class RegistersModel(TreeModel):
    previously_modified_registers: list[int] = []
    modified_registers: list[int] = []
    q_brush_previous: ClassVar[QtGui.QBrush] = QtGui.QBrush(QtGui.QColor(192, 192, 255, 60), Qt.BrushStyle.SolidPattern)
    q_brush_last: ClassVar[QtGui.QBrush] = QtGui.QBrush(QtGui.QColor(192, 192, 255, 100), Qt.BrushStyle.SolidPattern)
    q_brush_highlighted: ClassVar[QtGui.QBrush] = QtGui.QBrush(QtGui.QColor(255, 255, 0, 100), Qt.BrushStyle.SolidPattern)

    # register_edited, parameters are register name and hex value
    registerEdited: ClassVar[QtCore.Signal] = QtCore.Signal(str, str)

    # InputToHex object
    input2hex: ClassVar[InputToHex] = InputToHex()

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super(RegistersModel, self).__init__(parent)
        self.rootItem: TreeItem = TreeItem(("Register", "Value"))
        register_banks = [RegisterBank("General", [
            ['r0', '0x00000000'], ['r1', '0x00000000'], ['r2', '0x00000000'], ['r3', '0x00000000'],
            ['r4', '0x00000000'], ['r5', '0x00000000'], ['r6', '0x00000000'], ['r7', '0x00000000'],
            ['r8', '0x00000000'], ['r9', '0x00000000'], ['r10', '0x00000000'], ['r11', '0x00000000'],
            ['r12', '0x00000000'], ['r13 (SP)', '0x00000000'], ['r14 (LR)', '0x00000000'], ['r15 (PC)', '0x00000000'],
        ]),
                          ]
        for register_bank in register_banks:
            rbti = TreeItem([register_bank.name, ""], self.rootItem)
            self.rootItem.appendChild(rbti)
            for register_data in register_bank.registers_data:
                rti = TreeItem([register_data[0], register_data[1]], rbti)
                rbti.appendChild(rti)
        # Set fonts
        self.qFont: QtGui.QFont = getMonoSpacedFont()
        self.qFontLast: QtGui.QFont = getMonoSpacedFont()
        self.qFontLast.setWeight(QtGui.QFont.Weight.Black)
        # highlighted register
        self.highlighted_register: int | None = None

    @override
    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> object:
        if not index.isValid():
            return None
        item: TreeItem = cast(TreeItem, cast(object, index.internalPointer()))
        # Register bank
        if item.parent() == self.rootItem:
            if role == Qt.ItemDataRole.FontRole:
                return self.qFont
            elif role != QtCore.Qt.ItemDataRole.DisplayRole:
                return None
            return cast(object, item.data(index.column()))
        # Register
        if role == Qt.ItemDataRole.DisplayRole:
            return cast(object, item.data(index.column()))
        elif role == Qt.ItemDataRole.ToolTipRole:
            if index.column() == 0:
                return None
            dt: DataTypes = DataTypes(cast(str, item.data(index.column())))
            return """
                <table>
                <tr><td align="right"> Hexadecimal:</td><td><b>{0}</b></td></tr>
                <tr><td align="right">Unsigned int:</td><td align="right"><b>{1}</b></td></tr>
                <tr><td align="right">     Integer:</td><td align="right"><b>{2}</b></td></tr>
                <tr><td align="right">       ASCII:</td><td><b>{3}</b></td></tr>
                <tr><td align="right">       UTF-8:</td><td><b>{4}</b></td></tr>
                <tr><td align="right">      UTF-32:</td><td><b>{5}</b></td></tr>
                </table>
            """.format(
                dt.hexadecimal,
                dt.uint,
                dt.int,
                dt.ascii,
                dt.utf8,
                dt.utf32
            )
        elif role == Qt.ItemDataRole.BackgroundRole:
            if self.highlighted_register == index.row():
                return self.q_brush_highlighted
            elif self.modified_registers.count(index.row()):
                return self.q_brush_last
            elif self.previously_modified_registers.count(index.row()):
                return self.q_brush_previous
            else:
                return None
        elif role == Qt.ItemDataRole.FontRole:
            if self.modified_registers.count(index.row()):
                return self.qFontLast
            else:
                return self.qFont
        else:
            return None

    @override
    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        item: TreeItem = cast(TreeItem, cast(object, index.internalPointer()))
        if item.parent() == self.rootItem:
            return Qt.ItemFlag.ItemIsEnabled
        if index.column() == 0:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        return Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    @override
    def setData(self, index: QModelIndex | QPersistentModelIndex, value: object, role: int = Qt.ItemDataRole.EditRole) -> bool:
        _ = role
        (hex_value, err_msg) = self.input2hex.convert(value)
        if not hex_value:
            if err_msg:
                _ = QtWidgets.QMessageBox.warning(None, self.tr("Input error"), err_msg)
            return False
        item: TreeItem = cast(TreeItem, cast(object, index.internalPointer()))
        item.setData(1, hex_value)
        reg_name: str = cast(str, item.data(0)).split(" ")[0]
        self.registerEdited.emit(reg_name, hex_value)
        return True

    def setRegister(self, reg: int, value: str) -> None:
        # Ignore register numbers above 15 (16 is currently the Application Processor Status Register)
        if reg > 15:
            return
        self.layoutAboutToBeChanged.emit()
        self.rootItem.child(0).child(reg).setData(1, value)
        self.modified_registers.append(reg)
        self.dataChanged.emit(self.createIndex(reg, 0, self.rootItem.child(0)),
                              self.createIndex(reg, 1, self.rootItem.child(0)))
        self.layoutChanged.emit()

    def getRegister(self, i: int) -> str:
        return cast(str, self.rootItem.child(0).child(i).data(1))

    def clearHistory(self) -> None:
        self.previously_modified_registers.clear()
        self.modified_registers.clear()

    def stepHistory(self) -> None:
        copy_of_previous = self.previously_modified_registers[:]
        self.previously_modified_registers = self.modified_registers[:]
        self.modified_registers.clear()
        for reg in copy_of_previous + self.previously_modified_registers:
            self.dataChanged.emit(self.createIndex(reg, 0, self.rootItem.child(0)),
                                  self.createIndex(reg, 1, self.rootItem.child(0)))

    def highlightRegister(self, reg: int) -> None:
        self.highlighted_register = reg
        self.dataChanged.emit(self.createIndex(reg, 0, self.rootItem.child(0)),
                              self.createIndex(reg, 1, self.rootItem.child(0)))

    def unHighlightRegister(self) -> None:
        if self.highlighted_register is not None:
            self.highlighted_register = None
            self.dataChanged.emit(self.createIndex(0, 0, self.rootItem.child(0)),
                                  self.createIndex(15, 1, self.rootItem.child(0)))

    def reset(self) -> None:
        self.beginResetModel()
        # Reset stuff
        self.endResetModel()
