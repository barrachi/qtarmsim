# -*- coding: utf-8 -*-

from PyQt4.QtCore import Qt, QAbstractTableModel
from PyQt4.Qt import SIGNAL

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
        address = int(address, 16)
        return int(address/4) - self.start
    
    def loadWord(self, address):
        index = self.addressToIndex(address)
        return self.loadWordByIndex(index)

    def storeWord(self, address, word):
        index = self.addressToIndex(address)
        return self.storeWordByIndex(index, word)
    
    def loadWords(self, words):
        for i in range(len(words)):
            self.memory[i] = words[i]
    
    
class TableModelMemory(QAbstractTableModel):
 
    def rowCount(self, parent):
        try:
            return self.memory.length
        except AttributeError:
            return 0

    def columnCount(self, parent):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.memory.loadWordByIndex(index.row())

    def headerData(self, section, orientation, role = Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Vertical:
            return self.memory.indexToAddress(section)
        return QAbstractTableModel.headerData(self, section, orientation, role)
    
    def appendMemoryRange(self, memtype, start, end):
        self.emit(SIGNAL("layoutAboutToBeChanged()")) 
        self.memory = Memory(memtype, start, end)
        self.emit(SIGNAL("layoutChanged()"))
        # self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        # self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
    
    def loadWords(self, words):
        self.emit(SIGNAL("layoutAboutToBeChanged()")) 
        self.memory.loadWords(words)     
        self.emit(SIGNAL("layoutChanged()"))

    #def setMemoryWord(self, address, value):
    #    self.memory_data[address] = value
