# -*- coding: utf-8 -*-

from PyQt4.QtCore import Qt, QAbstractTableModel

class TableModelMemory(QAbstractTableModel):

    header_labels = ["Address", "Value"]
    
    memory_data = {}
        
    def rowCount(self, parent):
        return len(self.memory_data)

    def columnCount(self, parent):
        return len(self.header_labels)

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.memory_data[index.row()][index.column()]

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_labels[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)
    
    def clearMemoryData(self):
        self.memory_data.clear()
    
    def appendMemoryRange(self, start, end):
        for pos in range(start, end, 4):
            self.memory_data["0x{0:0{1}X}".format(pos, 8)] = '0x00000000'
        
    def setMemoryWord(self, address, value):
        self.memory_data[address] = value
