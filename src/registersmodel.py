# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from PyQt4.QtCore import Qt
from .simpletreemodel import TreeModel, TreeItem

class RegisterBank():
    def __init__(self, name, registers_data):
        self.name = name
        self.registers_data = registers_data
        
class RegistersModel(TreeModel):

    previously_modified_registers = []
    modified_registers = []
    q_brush_previous = QtGui.QBrush(QtGui.QColor(192, 192, 255, 60), Qt.SolidPattern)
    q_brush_last = QtGui.QBrush(QtGui.QColor(192, 192, 255, 100), Qt.SolidPattern) 
    q_font_last = QtGui.QFont("Courier", weight=100)

    def setupModelData(self):
        register_banks = [ RegisterBank("General", [
                                                    ['r0', '0x00000000'], ['r1', '0x00000000'], ['r2', '0x00000000'], ['r3', '0x00000000'],
                                                    ['r4', '0x00000000'], ['r5', '0x00000000'], ['r6', '0x00000000'], ['r7', '0x00000000'],
                                                    ['r8', '0x00000000'], ['r9', '0x00000000'], ['r10', '0x00000000'], ['r11', '0x00000000'],
                                                    ['r12', '0x00000000'], ['r13 (SP)', '0x00000000'], ['r14 (LR)', '0x00000000'], ['r15 (PC)', '0x00000000'],
                                                    ]),
                          ]
        parent = self.rootItem
        for register_bank in register_banks:
            rbti = TreeItem([register_bank.name, ""], parent) 
            parent.appendChild(rbti)
            for register_data in register_bank.registers_data:
                rti = TreeItem([register_data[0], register_data[1]], rbti)
                rbti.appendChild(rti)

    
    #===========================================================================
    # def data(self, index, role):
    #     if not index.isValid():
    #         print("not index.isValid", index, index.isValid())
    #         return None
    #     if not index.parent().isValid(): # Root level
    #         print("not index.parent().isValid", index, index.isValid())
    #         if role == Qt.DisplayRole and index.column() == 0:
    #             print("index.row() ", index.row(), self.register_banks[index.row()].name)
    #             return self.register_banks[index.row()].name
    #         else:
    #             return None
    #     else:                           # Registers level
    #         register_data = self.register_banks[index.row()].register_data
    #         if role == Qt.DisplayRole:
    #             return register_data[index.row()][index.column()]
    #         elif role == Qt.BackgroundRole and self.modified_registers.count(index.row()):
    #             return self.q_brush_last
    #         elif role == Qt.BackgroundRole and self.previously_modified_registers.count(index.row()):
    #             return self.q_brush_previous
    #         elif role == Qt.FontRole and self.modified_registers.count(index.row()):
    #             return self.q_font_last
    #         else:
    #             return None
    #===========================================================================

    def setRegister(self, i, value):
        self.rootItem.child(0).child(i).setData(1, value)
        self.modified_registers.append(i)
        self.dataChanged.emit(self.createIndex(i, 0, self.rootItem.child(0)), self.createIndex(i, 0, self.rootItem.child(0)))
        
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
                                  self.createIndex(reg, 0, self.rootItem.child(0)))
