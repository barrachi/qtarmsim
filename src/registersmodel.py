# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

class RegisterBank():
    def __init__(self, name, register_data):
        self.name = name
        self.register_data = register_data
        
class TreeModelRegisters(QtCore.QAbstractItemModel):

    register_banks = [
                      RegisterBank("General purpose", [
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
                                                      ]),
                     ]

    previously_modified_registers = []
    modified_registers = []
    
    q_brush_previous = QtGui.QBrush(QtGui.QColor(192, 192, 255, 60), Qt.SolidPattern)
    q_brush_last = QtGui.QBrush(QtGui.QColor(192, 192, 255, 100), Qt.SolidPattern) 
    
    q_font_last = QtGui.QFont("Courier", weight=100)

    def rowCount(self, parent):
        if parent.isValid():
            print("----> ", parent.row(), parent.column(), parent.parent().isValid())
            if parent.row() == 0 and parent.column() == 0 and parent.parent().isValid() == False:
                print("***parent.isValid parent.row()", parent, "rowCount: ", len(self.register_banks[parent.row()].register_data))
                return len(self.register_banks[parent.row()].register_data)
            else:
                return 0
        else:
            print("not parent.isValid rowCount: ", len(self.register_banks))
            return len(self.register_banks)

    def columnCount(self, parent):
        return 2

    def index(self, row, column, parent):
        return self.createIndex(row, column, 0)
        
    def data(self, index, role):
        if not index.isValid():
            print("not index.isValid", index, index.isValid())
            return None
        if not index.parent().isValid(): # Root level
            print("not index.parent().isValid", index, index.isValid())
            if role == Qt.DisplayRole and index.column() == 0:
                print("index.row() ", index.row(), self.register_banks[index.row()].name)
                return self.register_banks[index.row()].name
            else:
                return None
        else:                           # Registers level
            register_data = self.register_banks[index.row()].register_data
            if role == Qt.DisplayRole:
                return register_data[index.row()][index.column()]
            elif role == Qt.BackgroundRole and self.modified_registers.count(index.row()):
                return self.q_brush_last
            elif role == Qt.BackgroundRole and self.previously_modified_registers.count(index.row()):
                return self.q_brush_previous
            elif role == Qt.FontRole and self.modified_registers.count(index.row()):
                return self.q_font_last
            else:
                return None

    #def headerData(self, section, orientation, role = Qt.DisplayRole):
    #    if role == Qt.DisplayRole and orientation == Qt.Vertical:
    #        return self.register_data[section][0]
    #    return QtGui.QStandardItemModel.headerData(self, section, orientation, role)

    def setRegister(self, i, value):
        return
        self.register_banks[0].register_data[i][1] = value
        self.modified_registers.append(i)
        self.dataChanged.emit(self.createIndex(i, 0, self.createIndex(0,0)), self.createIndex(i, 0, self.createIndex(0,0)))
        
    def getRegister(self, i):
        return self.register_banks[0].register_data[i][1]
    
    def clearHistory(self):
        return
        self.previously_modified_registers.clear()
        self.modified_registers.clear()
        
    def stepHistory(self):
        return
        copy_of_previous = self.previously_modified_registers[:]
        self.previously_modified_registers = self.modified_registers[:]
        self.modified_registers.clear()
        for reg in copy_of_previous + self.previously_modified_registers:
            self.dataChanged.emit(self.createIndex(reg, 0, self.createIndex(0,0)), self.createIndex(reg, 0, self.createIndex(0,0)))
    