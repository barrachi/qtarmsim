# -*- coding: utf-8 -*-

from PyQt4.QtCore import Qt, QAbstractTableModel, QVariant

class TableModelRegisters(QAbstractTableModel):

    registersData = [
        ['r0', '0x00000000'],
        ['r1', '0x12345678'],
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
