# -*- coding: utf-8 -*-

###########################################################################
#                                                                         #
#  This file is part of QtARMSim.                                         #
#                                                                         #
#  QtARMSim is free software: you can redistribute it and/or modify       #
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

from PySide2 import QtGui, QtCore
from PySide2.QtCore import Qt

from .simpletreemodel import TreeModel, TreeItem
from ..utils import getMonoSpacedFont


class MemoryBank:

    def __init__(self, memType, start, nBytes):
        """Initializes a memory bank instance.
        
        @param memType: The memory type, one of RAM or ROM.
        @param start: The starting address in hexadecimal.
        @param nBytes: The number of bytes.
        """
        self.memType = memType
        self.start = int(start, 16)
        self.length = nBytes
        # Round memory size to a word boundary
        if nBytes % 4:
            self.length += (4 - nBytes % 4)
        self.end = self.start + self.length - 1

    def addressToRow(self, hexAddress):
        """Given an hexadecimal hexAddress, returns the corresponding row"""
        intAddress = int(hexAddress, 16)
        return intAddress - self.start


class MemoryModel(TreeModel):
    """
    Tree model that manages the memory banks of a given simulation and their contents.
    """

    memoryBanks = []

    modifiedBytes = []
    previouslyModifiedBytes = []

    # memoryEdited signal, parameters are hex address and hex value
    memoryEdited = QtCore.Signal('QString', 'QString')

    def __init__(self, parent=None):
        """
        Initializes the memory model.
        """
        super(MemoryModel, self).__init__(parent)
        self.rootItem = TreeItem(("Address", "Value"))
        # Set fonts
        self.qFont = getMonoSpacedFont()
        self.qFontLast = getMonoSpacedFont()
        self.qFontLast.setWeight(QtGui.QFont.Black)
        # Set brushes
        self.qBrushPrevious = QtGui.QBrush(QtGui.QColor(192, 192, 255, 60), Qt.SolidPattern)
        self.qBrushLast = QtGui.QBrush(QtGui.QColor(192, 192, 255, 100), Qt.SolidPattern)

    def appendMemoryBank(self, memType, hex_start, membytes):
        """
        Adds a new memory bank to the memory model and populates it.
        """
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self.memoryBanks.append(MemoryBank(memType, hex_start, len(membytes)))
        memory_bank_item = TreeItem(("{} {}".format(memType, hex_start), ""), self.rootItem)
        self.rootItem.appendChild(memory_bank_item)
        address = self.memoryBanks[-1].start
        # Round memory bytes to a word boundary
        if len(membytes) % 4 != 0:
            membytes += ['0x00'] * (4 - len(membytes) % 4)
        # Add the bytes to the model
        for hexByte in membytes:
            hexAddress = "0x{0:0{1}X}".format(address, 8)
            memory_item = TreeItem([hexAddress, hexByte], memory_bank_item)
            memory_bank_item.appendChild(memory_item)
            address += 1
        self.emit(QtCore.SIGNAL("layoutChanged()"))

    def getMemoryBank(self, hexAddress):
        """
        Returns the memory bank that holds the given memory address.
        """
        intAddress = int(hexAddress, 16)
        mbRow = 0
        for memoryBank in self.memoryBanks:
            if memoryBank.start <= intAddress <= memoryBank.end:
                return mbRow, memoryBank
            mbRow += 1
        return -1, None

    def getIndex(self, hexAddress):
        """
        Returns the model index that references the given memory address.
        """
        (mbRow, memoryBank) = self.getMemoryBank(hexAddress)
        memoryRow = memoryBank.addressToRow(hexAddress)
        return self.createIndex(memoryRow, 0, self.rootItem.child(mbRow).child(memoryRow))

    def setByte(self, hexAddress, hexByte, emitMemoryEdited=False):
        """
        Stores the given byte at the given address.
        """
        (mbRow, memoryBank) = self.getMemoryBank(hexAddress)
        memoryRow = memoryBank.addressToRow(hexAddress)
        memoryItem = self.rootItem.child(mbRow).child(memoryRow)
        memoryItem.setData(1, hexByte)
        self.modifiedBytes.append((mbRow, memoryRow))
        self.dataChanged.emit(self.createIndex(memoryRow, 0, self.rootItem.child(mbRow)),
                              self.createIndex(memoryRow, 1, self.rootItem.child(mbRow)))
        if emitMemoryEdited:
            self.memoryEdited.emit(hexAddress, hexByte)

    def setWord(self, hexAddress, hexWord, emitMemoryEdited=False):
        """
        Stores the given word (4 bytes) at the given address (following Little Endian memory organization).
        """
        (mbRow, memoryBank) = self.getMemoryBank(hexAddress)
        memoryRowStart = memoryBank.addressToRow(hexAddress)
        for i in range(4):
            hexByte = "0x{}".format(hexWord[2 + i * 2:4 + i * 2])
            memoryRow = memoryRowStart + 3 - i  # 3-i due to Little Endian
            memoryItem = self.rootItem.child(mbRow).child(memoryRow)
            memoryItem.setData(1, hexByte)
            self.modifiedBytes.append((mbRow, memoryRow))
        # noinspection PyUnboundLocalVariable
        self.dataChanged.emit(self.createIndex(memoryRow, 0, self.rootItem.child(mbRow)),
                              self.createIndex(memoryRow + 3, 1, self.rootItem.child(mbRow)))
        if emitMemoryEdited:
            self.memoryEdited.emit(hexAddress, hexWord)

    def getWord(self, hexAddress):
        """
        Returns the word (4 bytes) at the given address (following Little Endian memory organization).
        """
        (mbRow, memoryBank) = self.getMemoryBank(hexAddress)
        memoryRowStart = memoryBank.addressToRow(hexAddress)
        hexWord = "0x"
        for i in range(4):
            memoryRow = memoryRowStart + 3 - i  # 3-i due to Little Endian
            memoryItem = self.rootItem.child(mbRow).child(memoryRow)
            hexWord += memoryItem.data(1)[2:]

    def reset(self):
        """
        Resets the model to its original state in any attached views.
        """
        self.beginResetModel()
        self.memoryBanks.clear()
        self.rootItem.childItems.clear()
        self.clearHistory()
        self.endResetModel()

    def clearHistory(self):
        """
        Clears the history of previously modified bytes.
        """
        self.previouslyModifiedBytes.clear()
        self.modifiedBytes.clear()

    def stepHistory(self):
        """
        Steps one the history of previously modified bytes.
        """
        copyOfPrevious = self.previouslyModifiedBytes[:]
        self.previouslyModifiedBytes = self.modifiedBytes[:]
        self.modifiedBytes.clear()
        for (mbRow, memoryRow) in copyOfPrevious + self.previouslyModifiedBytes:
            self.dataChanged.emit(self.createIndex(memoryRow, 0, self.rootItem.child(mbRow)),
                                  self.createIndex(memoryRow, 1, self.rootItem.child(mbRow)))
