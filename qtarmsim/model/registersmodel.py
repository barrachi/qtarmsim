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


from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import Qt

from .common import InputToHex, DataTypes
from .simpletreemodel import TreeModel, TreeItem
from ..utils import getMonoSpacedFont


class RegisterBank:
    def __init__(self, name, registers_data):
        self.name = name
        self.registers_data = registers_data


class RegistersModel(TreeModel):
    previously_modified_registers = []
    modified_registers = []
    q_brush_previous = QtGui.QBrush(QtGui.QColor(192, 192, 255, 60), Qt.SolidPattern)
    q_brush_last = QtGui.QBrush(QtGui.QColor(192, 192, 255, 100), Qt.SolidPattern)

    # register_edited, parameters are register name and hex value
    register_edited = QtCore.Signal('QString', 'QString')

    # InputToHex object
    input2hex = InputToHex()

    def __init__(self, parent=None):
        super(RegistersModel, self).__init__(parent)
        self.rootItem = TreeItem(("Register", "Value"))
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
        self.q_font = getMonoSpacedFont()
        self.q_font_last = getMonoSpacedFont()
        self.q_font_last.setWeight(QtGui.QFont.Black)

    def data(self, index, role):
        if not index.isValid():
            return None
        item = index.internalPointer()
        # Register bank
        if item.parent() == self.rootItem:
            if role == Qt.FontRole:
                return self.q_font
            elif role != QtCore.Qt.DisplayRole:
                return None
            return item.data(index.column())
        # Register
        if role == Qt.DisplayRole:
            return item.data(index.column())
        elif role == Qt.ToolTipRole:
            if index.column() == 0:
                return None
            dt = DataTypes(item.data(index.column()))
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
        elif role == Qt.BackgroundRole and self.modified_registers.count(index.row()):
            return self.q_brush_last
        elif role == Qt.BackgroundRole and self.previously_modified_registers.count(index.row()):
            return self.q_brush_previous
        elif role == Qt.FontRole:
            if self.modified_registers.count(index.row()):
                return self.q_font_last
            else:
                return self.q_font
        else:
            return None

    def flags(self, index):
        if not index.isValid():
            return False
        item = index.internalPointer()
        if item.parent() == self.rootItem:
            return Qt.ItemIsEnabled
        if index.column() == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def setData(self, index, value, role=Qt.EditRole):
        (hex_value, err_msg) = self.input2hex.convert(value)
        if not hex_value:
            if err_msg:
                QtWidgets.QMessageBox.warning(None, self.tr("Input error"), err_msg)
            return False
        item = index.internalPointer()
        item.setData(1, hex_value)
        reg_name = item.data(0).split(" ")[0]
        self.register_edited.emit(reg_name, hex_value)
        return True

    def setRegister(self, reg, value):
        # Ignore register numbers above 15 (16 is currently the Application Processor Status Register)
        if reg > 15:
            return
        self.rootItem.child(0).child(reg).setData(1, value)
        self.modified_registers.append(reg)
        self.dataChanged.emit(self.createIndex(reg, 0, self.rootItem.child(0)),
                              self.createIndex(reg, 1, self.rootItem.child(0)))

    def getRegister(self, i):
        return self.rootItem.child(0).child(i).data(1)

    def clearHistory(self):
        self.previously_modified_registers.clear()
        self.modified_registers.clear()

    def stepHistory(self):
        copy_of_previous = self.previously_modified_registers[:]
        self.previously_modified_registers = self.modified_registers[:]
        self.modified_registers.clear()
        for reg in copy_of_previous + self.previously_modified_registers:
            self.dataChanged.emit(self.createIndex(reg, 0, self.rootItem.child(0)),
                                  self.createIndex(reg, 1, self.rootItem.child(0)))

    def reset(self):
        self.beginResetModel()
        # Reset stuff
        self.endResetModel()
