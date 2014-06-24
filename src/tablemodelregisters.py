# -*- coding: utf-8 -*-

from PyQt4.QtCore import Qt, QAbstractTableModel
from PyQt4 import QtGui

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

    previously_modified_registers = []
    modified_registers = []
    
    q_brush_previous = QtGui.QBrush(QtGui.QColor(192, 192, 255, 60), Qt.SolidPattern)
    q_brush_last = QtGui.QBrush(QtGui.QColor(192, 192, 255, 100), Qt.SolidPattern) 
    
    q_font_last = QtGui.QFont("Courier", weight=100)

    def rowCount(self, parent):
        return len(self.registers_data)

    def columnCount(self, parent):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role == Qt.DisplayRole:
            return self.registers_data[index.row()][1]
        elif role == Qt.BackgroundRole and self.modified_registers.count(index.row()):
            return self.q_brush_last
        elif role == Qt.BackgroundRole and self.previously_modified_registers.count(index.row()):
            return self.q_brush_previous
        elif role == Qt.FontRole and self.modified_registers.count(index.row()):
            return self.q_font_last
        else:
            return None

    def headerData(self, section, orientation, role = Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Vertical:
            return self.registers_data[section][0]
        return QAbstractTableModel.headerData(self, section, orientation, role)

    def setRegister(self, i, value):
        self.registers_data[i][1] = value
        self.modified_registers.append(i)
        self.dataChanged.emit(self.createIndex(i, 0), self.createIndex(i, 0))
        
    def getRegister(self, i):
        return self.registers_data[i][1]
    
    def clearHistory(self):
        self.previously_modified_registers.clear()
        self.modified_registers.clear()
        
    def stepHistory(self):
        copy_of_previous = self.previously_modified_registers[:]
        self.previously_modified_registers = self.modified_registers[:]
        self.modified_registers.clear()
        for reg in copy_of_previous + self.previously_modified_registers:
            self.dataChanged.emit(self.createIndex(reg, 0), self.createIndex(reg, 0))
    