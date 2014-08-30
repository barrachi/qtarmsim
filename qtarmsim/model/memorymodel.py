# -*- coding: utf-8 -*-

###########################################################################
#                                                                         #
#  This file is part of Qt ARMSim.                                        #
#                                                                         #
#  Qt ARMSim is free software: you can redistribute it and/or modify      #
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

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

from . simpletreemodel import TreeModel, TreeItem
from . common import InputToHex


class MemoryBank():
    
    def __init__(self, memtype, start, nbytes):
        """Initializes the memory bank class.
        
        @param start: The starting address in hexadecimal.
        @param end: The last address in hexadecimal.
        @param memtype: The memory type, one of RAM or ROM.  
        """
        self.memtype = memtype
        self.start = int(start, 16)
        self.end = self.start + nbytes - 1
        if nbytes % 4:
            self.end += 4 - nbytes % 4
        self.length = int((self.end-self.start)/4) + 1

    def addressToRow(self, hex_address):
        "Given an hexadecimal hex_address, it returns the corresponding row"
        int_address = int(hex_address, 16)
        return int((int_address - self.start)/4)
    

class MemoryModel(TreeModel):

    memory_banks = []
    
    previously_modified_words = []
    modified_words = []
    q_brush_previous = QtGui.QBrush(QtGui.QColor(192, 192, 255, 60), Qt.SolidPattern)
    q_brush_last = QtGui.QBrush(QtGui.QColor(192, 192, 255, 100), Qt.SolidPattern) 
    q_font_last = QtGui.QFont("Courier 10 Pitch", weight=100)

    # memory_edited, parameters are hex address and hex value
    memory_edited = QtCore.pyqtSignal('QString', 'QString')

    # InputToHex object
    input2hex = InputToHex()

    def __init__(self, parent=None):
        super(MemoryModel, self).__init__(parent)
        self.rootItem = TreeItem(("Address", "Value"))

    def data(self, index, role):
        if not index.isValid():
            return None
        item = index.internalPointer()
        # Memory bank
        if item.parent() == self.rootItem:
            if role != QtCore.Qt.DisplayRole:
                return None
            return item.data(index.column())
        # Register
        if role == Qt.DisplayRole:
            return item.data(index.column())
        elif role == Qt.BackgroundRole and self.modified_words.count((index.parent().row(), index.row())):
            return self.q_brush_last
        elif role == Qt.BackgroundRole and self.previously_modified_words.count((index.parent().row(), index.row())):
            return self.q_brush_previous
        elif role == Qt.FontRole and self.modified_words.count((index.parent().row(), index.row())):
            return self.q_font_last
        else:
            return None

    def flags(self, index):
        if not index.isValid():
            return False
        item = index.internalPointer()
        if item.parent() == self.rootItem:
            return Qt.ItemIsEnabled
        if  index.column() == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if item.parent().data(0)[:3] == 'ROM':
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def setData(self, index, value, role = Qt.EditRole):
        (hex_value, err_msg) = self.input2hex.convert(value)
        if not hex_value:
            if err_msg:
                QtGui.QMessageBox.warning(None, self.tr("Input error"), err_msg)
            return False
        item = index.internalPointer()
        hex_address = item.data(0)
        item.setData(1, hex_value)
        self.memory_edited.emit(hex_address, hex_value)
        return True

    def appendMemoryBank(self, memtype, hex_start, membytes):
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self.memory_banks.append(MemoryBank(memtype, hex_start, len(membytes)))
        memory_bank_item = TreeItem(("{} {}".format(memtype, hex_start), ""), self.rootItem)
        self.rootItem.appendChild(memory_bank_item)
        word = []
        address = self.memory_banks[-1].start
        for byte in membytes:
            word.append(byte[2:])
            if len(word) == 4:
                hex_address = "0x{0:0{1}X}".format(address, 8)
                hex_word = '0x{}{}{}{}'.format(word[3], word[2], word[1], word[0])
                memory_item = TreeItem([hex_address, hex_word], memory_bank_item)
                memory_bank_item.appendChild(memory_item)
                word.clear()
                address += 4
        # Form the last word with the remaining 1-3 membytes, if any 
        if len(word):
            while len(word) < 4:
                word.append('00')
            hex_address = "0x{0:0{1}X}".format(address, 8) 
            hex_word = '0x{}{}{}{}'.format(word[3], word[2], word[1], word[0])
            memory_item = TreeItem([hex_address, hex_word], memory_bank_item)
            memory_bank_item.appendChild(memory_item)
        self.emit(QtCore.SIGNAL("layoutChanged()"))


    def getMemoryBank(self, hex_address):
        int_address = int(hex_address, 16)
        mb_row = 0
        for memory_bank in self.memory_banks:
            if memory_bank.start <= int_address <= memory_bank.end:
                return (mb_row, memory_bank)
            mb_row += 1
        return (-1, None)
    
    def getIndex(self, hex_address):
        (mb_row, memory_bank) = self.getMemoryBank(hex_address)
        memory_row = memory_bank.addressToRow(hex_address)
        return self.createIndex(memory_row, 0, self.rootItem.child(mb_row).child(memory_row))

    def setByte(self, hex_address, hex_byte):
        (mb_row, memory_bank) = self.getMemoryBank(hex_address)
        memory_row = memory_bank.addressToRow(hex_address)
        memory_item = self.rootItem.child(mb_row).child(memory_row)
        hex_word = memory_item.data(1)
        pos = 3 - int(hex_address, 16) % 4
        word_bytes = [hex_word[2:4], hex_word[4:6], hex_word[6:8], hex_word[8:10]]
        word_bytes[pos] = hex_byte[2:]
        hex_word = "0x" + "".join(word_bytes)
        memory_item.setData(1, hex_word)
        self.modified_words.append((mb_row, memory_row))
        self.dataChanged.emit(self.createIndex(memory_row, 0, self.rootItem.child(mb_row)), self.createIndex(memory_row, 1, self.rootItem.child(mb_row)))

    def setWord(self, hex_address, hex_word):
        (mb_row, memory_bank) = self.getMemoryBank(hex_address)
        memory_row = memory_bank.addressToRow(hex_address)
        memory_item = self.rootItem.child(mb_row).child(memory_row)
        memory_item.setData(1, hex_word)
        self.modified_words.append((mb_row, memory_row))
        self.dataChanged.emit(self.createIndex(memory_row, 0, self.rootItem.child(mb_row)), self.createIndex(memory_row, 1, self.rootItem.child(mb_row)))

    def getWord(self, hex_address):
        (mb_row, memory_bank) = self.getMemoryBank(hex_address)
        memory_row = memory_bank.addressToRow(hex_address)
        memory_item = self.rootItem.child(mb_row).child(memory_row)
        return memory_item.data(1)
    
    def reset(self):
        """
        Resets the model to its original state in any attached views.
        """
        self.beginResetModel()
        self.memory_banks.clear()
        self.rootItem.childItems.clear()
        self.clearHistory()
        self.endResetModel()
        
    def clearHistory(self):
        self.previously_modified_words.clear()
        self.modified_words.clear()
        
    def stepHistory(self):
        copy_of_previous = self.previously_modified_words[:]
        self.previously_modified_words = self.modified_words[:]
        self.modified_words.clear()
        for (mb_row, memory_row) in copy_of_previous + self.previously_modified_words:
            self.dataChanged.emit(self.createIndex(memory_row, 0, self.rootItem.child(mb_row)), self.createIndex(memory_row, 1, self.rootItem.child(mb_row)))
