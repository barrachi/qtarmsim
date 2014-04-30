# -*- coding: utf-8 -*-

from PyQt4.QtCore import Qt, QAbstractTableModel

class TableModelRegisters(QAbstractTableModel):

    registersData = [
        ['r0', '0x00000000'],
        ['r1', '0x12345678'],
        ['r2', '0x00000000'],
        ['r3', '0x00000000'],
        ['r4', '0x00000000'],
        ['r5', '0x00000000'],
        ['r6', '0x00000000'],
        ['r7', '0x00000000'],
        ['PC', '0x00000000'],
        ['SP', '0x00000000'],
        ['LR', '0x00000000'],
        ['CPSR', '0x00000000'],
    ]

    def rowCount(self, parent):
        return len(self.registersData)

    def columnCount(self, parent):
        return len(self.registersData[0])

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.registersData[index.row()][index.column()]
