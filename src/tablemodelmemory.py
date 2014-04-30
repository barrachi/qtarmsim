# -*- coding: utf-8 -*-

from PyQt4.QtCore import Qt, QAbstractTableModel

class TableModelMemory(QAbstractTableModel):

    memoryData = [
        ['0x00000000', '0x00000000'],
        ['0x00000000', '0x12345678'],
        ['0x00000000', '0x00000000'],
        ['0x00000000', '0x00000000'],
        ['0x00000000', '0x00000000'],
        ['0x00000000', '0x00000000'],
        ['0x00000000', '0x00000000'],
        ['0x00000000', '0x00000000'],
        ['0x00000000', '0x00000000'],
        ['0x00000000', '0x00000000'],
        ['0x00000000', '0x00000000'],
        ['0x00000000', '0x00000000'],
    ]

    def rowCount(self, parent):
        return len(self.memoryData)

    def columnCount(self, parent):
        return len(self.memoryData[0])

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.memoryData[index.row()][index.column()]
