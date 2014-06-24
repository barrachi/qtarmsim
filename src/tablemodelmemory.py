# -*- coding: utf-8 -*-

from PyQt4.QtCore import Qt, QAbstractTableModel
from PyQt4.Qt import SIGNAL
from PyQt4 import QtGui

class Memory():
    
    def __init__(self, memtype, start, end):
        """Initializes the memory class.
        
        @param start: The starting address in hexadecimal.
        @param end: The last address in hexadecimal.
        @param memtype: The memory type, one of RAM or ROM.  
        """
        self.key = "{} - {}".format(start, end)
        self.start = int(start, 16)
        self.end = int(end, 16)
        self.memtype = memtype
        self.length = int((self.end-self.start)/4) + 1
        self.memory = ['0x00000000']*self.length

    def loadWordByIndex(self, index):
        return self.memory[index]
    
    def storeWordByIndex(self, index, word):
        self.memory[index] = word
    
    def indexToAddress(self, index):
        "Given an index, it returns the corresponding hexadecimal address"
        return "0x{0:0{1}X}".format(self.start + index*4, 8)
        
    def addressToIndex(self, address):
        "Given an hexadecimal address, it returns the corresponding index"
        address_n = int(address, 16)
        return int((address_n - self.start)/4)
    
    def loadWord(self, address):
        index = self.addressToIndex(address)
        return self.loadWordByIndex(index)

    def storeWord(self, address, word):
        index = self.addressToIndex(address)
        self.storeWordByIndex(index, word)
    
    def storeByte(self, address, byte):
        index = self.addressToIndex(address)
        word = self.loadWordByIndex(index)
        address_n = int(address, 16)
        pos = 3 - address_n % 4
        word_bytes = [word[2:4], word[4:6], word[6:8], word[8:10]]
        word_bytes[pos] = byte[2:]
        word = "0x" + "".join(word_bytes)
        self.storeWordByIndex(index, word)
    
    def loadWords(self, words):
        for i in range(len(words)):
            self.memory[i] = words[i]
    
    
class TableModelMemory(QAbstractTableModel):

    q_brush_previous = QtGui.QBrush(QtGui.QColor(192, 192, 255, 60), Qt.SolidPattern)
    q_brush_last = QtGui.QBrush(QtGui.QColor(192, 192, 255, 100), Qt.SolidPattern) 
    
    q_font_last = QtGui.QFont("Courier", weight=100)
 
    def __init__(self, parent = None):
        if parent == None:
            self._parent = None
            self.memory_banks = []
            self.total_row_count = 0
        else:
            self._parent = parent
            self.memory = None
            self.previously_modified_words = []
            self.modified_words = []
    
        super(TableModelMemory, self).__init__(parent)
        
    def rowCount(self, parent):
        if self.memory:
            return self.memory.length
        if self._parent == None:
            return self.total_row_count
        return 0

    def columnCount(self, parent):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role == Qt.DisplayRole and self.memory:
            return self.memory.loadWordByIndex(index.row())
        elif role == Qt.BackgroundRole and self.modified_words.count(index.row()):
            return self.q_brush_last
        elif role == Qt.BackgroundRole and self.previously_modified_words.count(index.row()):
            return self.q_brush_previous
        elif role == Qt.FontRole and self.modified_words.count(index.row()):
            return self.q_font_last
        else:
            return None
    
    def headerData(self, section, orientation, role = Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Vertical:
            return self.memory.indexToAddress(section)
        return QAbstractTableModel.headerData(self, section, orientation, role)
    
    def appendMemoryRange(self, memtype, start, end):
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        if not self._parent:
            raise RuntimeError("This method can not be called from a root TableModelMemory")
        self.memory = Memory(memtype, start, end)
        self._parent.memory_banks.append([self.memory.start, self.memory.end, self])
        self._parent.total_row_count += self.memory.length
        self.emit(SIGNAL("layoutChanged()"))
        # self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        # self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
    
    def loadWords(self, words):
        if not self._parent:
            raise RuntimeError("This method can not be called from a root TableModelMemory")
        self.emit(SIGNAL("layoutAboutToBeChanged()")) 
        self.memory.loadWords(words)     
        self.emit(SIGNAL("layoutChanged()"))

    def setByte(self, address, byte):
        if self._parent == None:
            address_n = int(address, 16)
            for memory_bank in self.memory_banks:
                if memory_bank[0] <= address_n <= memory_bank[1]:
                    memory_bank[2].setByte(address, byte)
                    break
        else:
            self.memory.storeByte(address, byte)
            row = self.memory.addressToIndex(address)
            self.modified_words.append(row)
            self.dataChanged.emit(self.createIndex(row, 0), self.createIndex(row, 0))
             
                        
    #def setMemoryWord(self, address, value):
    #    self.memory_data[address] = value

    def clear(self):
        if self._parent == None:
            self.memory_banks.clear()
            self.total_row_count = 0

    def clearHistory(self):
        if self._parent == None:
            for memory_bank in self.memory_banks:
                memory_bank[2].clearHistory()
        else:
            self.previously_modified_words.clear()
            self.modified_words.clear()
        
    def stepHistory(self):
        if self._parent == None:
            for memory_bank in self.memory_banks:
                memory_bank[2].stepHistory()
        else:
            copy_of_previous = self.previously_modified_words[:]
            self.previously_modified_words = self.modified_words[:]
            self.modified_words.clear()
            for address in copy_of_previous + self.previously_modified_words:
                self.dataChanged.emit(self.createIndex(address, 0), self.createIndex(address, 0))
