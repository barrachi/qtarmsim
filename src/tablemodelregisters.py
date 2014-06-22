# -*- coding: utf-8 -*-

from PyQt4.QtCore import Qt, QAbstractTableModel

class TableModelRegisters(QAbstractTableModel):

    registers_data = [
        ['r0', '0x00000000'],
        ['r1', '0x00000000'],
        ['r2', '0x00000000'],
        ['r3', '0x00000000'],
        ['r4', '0x00000000'],
        ['r5', '0x00000000'],
        ['r6', '0x00000000'],
        ['r7', '0x00000000'],
        ['r8', '0x00000000'],
        ['r9', '0x00000000'],
        ['r10', '0x00000000'],
        ['r11', '0x00000000'],
        ['r12', '0x00000000'],
        ['r13 (SP)', '0x00000000'],
        ['r14 (LR)', '0x00000000'],
        ['r15 (PC)', '0x00000000'],
    ]

    def rowCount(self, parent):
        return len(self.registers_data)

    def columnCount(self, parent):
        return len(self.registers_data[0])

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.registers_data[index.row()][index.column()]

    def setRegister(self, i, value):
        self.registers_data[i][1] = value
        