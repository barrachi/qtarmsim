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

from __future__ import annotations

from typing import cast

from PySide6 import QtGui
from PySide6.QtCore import Qt, QAbstractItemModel, Signal, QModelIndex
from typing_extensions import override

from .memorybank import MemoryBank
from .memorybankitem import MemoryBankItem
from .memoryitem import MemoryItem
from ..utils import getMonoSpacedFont


class MemoryModel(QAbstractItemModel):
    """
    Memory model that manages the memory banks of a given simulation and their contents.
    """

    # memoryEdited signal, parameters are hex address and hex value
    memoryEdited: Signal = Signal(str, str)

    def __init__(self, parent: QAbstractItemModel | None = None) -> None:
        """
        Initializes the memory model.
        """
        super().__init__(parent)
        self.nextSlot: int = 0
        self._memoryBanks: list[MemoryBank] = [MemoryBank(i, 'ROM', '0x10000000', ['0x00']) for i in range(5)]
        self.modifiedBytes: list[tuple[int, int]] = []
        self.previouslyModifiedBytes: list[tuple[int, int]] = []
        # Set fonts
        self.qFont: QtGui.QFont = getMonoSpacedFont()
        self.qFontLast: QtGui.QFont = getMonoSpacedFont()
        self.qFontLast.setWeight(QtGui.QFont.Weight.Black)
        # Set brushes
        self.qBrushPrevious: QtGui.QBrush = QtGui.QBrush(QtGui.QColor(192, 192, 255, 60), Qt.BrushStyle.SolidPattern)
        self.qBrushLast: QtGui.QBrush = QtGui.QBrush(QtGui.QColor(192, 192, 255, 100), Qt.BrushStyle.SolidPattern)

    def appendMemoryBank(self, memType: str, hexStart: str, memBytes: list[str]) -> None:
        """
        Adds a new memory bank to the memory model
        """
        self.layoutAboutToBeChanged.emit()
        self._memoryBanks[self.nextSlot].__init__(self.nextSlot, memType, hexStart, memBytes)
        self.nextSlot += 1
        self.layoutChanged.emit()

    def getMemoryBankWithHexAddress(self, hexAddress: str) -> MemoryBank:
        """
        Returns the memory bank that holds the given memory address.
        """
        for memoryBank in self._memoryBanks:
            if memoryBank.contains(hexAddress):
                return memoryBank
        raise IndexError(f"memory bank for address {hexAddress} not found")

    def getMemoryBankInSlot(self, slot: int) -> MemoryBank:
        """
        Returns the memory bank in the given slot.
        """
        if slot < 0 or slot >= self.nextSlot:
            raise IndexError(f"memory bank in slot {slot} not found")
        return self._memoryBanks[slot]

    def getNumberOfMemoryBanks(self) -> int:
        return self.nextSlot

    def getIndex(self, hexAddress: str) -> QModelIndex:
        """
        Returns the model index that references the given memory address.
        """
        memoryBank = self.getMemoryBankWithHexAddress(hexAddress)
        memoryRow = memoryBank.index(hexAddress)
        return self.createIndex(memoryRow, 0, memoryBank.getMemoryItem(memoryRow))

    def setByte(self, hexAddress: str, hexByte: str, emitMemoryEdited: bool = False) -> None:
        """
        Stores the given byte at the given address.

        :param hexAddress: The hexadecimal address
        :param hexByte: The byte to be stored in hexadecimal
        :param emitMemoryEdited: Whether to emit the memory edited signal or not
        """
        memoryBank = self.getMemoryBankWithHexAddress(hexAddress)
        memoryRow = memoryBank.setByte(hexAddress, hexByte)
        self.modifiedBytes.append((memoryBank.slot, memoryRow))
        topLeft = self.createIndex(memoryRow, 0, memoryBank.getMemoryItem(memoryRow))
        bottomRight = self.createIndex(memoryRow, 0, memoryBank.getMemoryItem(memoryRow))
        if topLeft.isValid() and bottomRight.isValid():
            self.dataChanged.emit(topLeft, bottomRight)
        if emitMemoryEdited:
            self.memoryEdited.emit(hexAddress, hexByte)

    def getByte(self, hexAddress: str) -> str:
        """
        Returns the byte at the given address in hexadecimal format.

        :param hexAddress: The hexadecimal address.
        :return: The byte in hexadecimal format.
        """
        return self.getMemoryBankWithHexAddress(hexAddress).getByte(hexAddress)

    def setWord(self, hexAddress: str, hexWord: str, emitMemoryEdited: bool = False) -> None:
        """
        Stores the given word (4 bytes) at the given address (following Little Endian memory organization).
        """
        memoryBank = self.getMemoryBankWithHexAddress(hexAddress)
        memoryRow = memoryBank.setWord(hexAddress, hexWord)
        self.modifiedBytes.append((memoryBank.slot, memoryRow))
        topLeft = self.createIndex(memoryRow, 0, memoryBank.getMemoryItem(memoryRow))
        bottomRight = self.createIndex(memoryRow + 3, 0, memoryBank.getMemoryItem(memoryRow + 3))
        if topLeft.isValid() and bottomRight.isValid():
            self.dataChanged.emit(topLeft, bottomRight)
        if emitMemoryEdited:
            self.memoryEdited.emit(hexAddress, hexWord)

    def getWord(self, hexAddress: str) -> str:
        """
        Returns the word (4 bytes) at the given address (following the Little Endian memory organization).

        :param hexAddress: The hexadecimal address of the word.
        :return: The word in hexadecimal format.
        """
        return self.getMemoryBankWithHexAddress(hexAddress).getWord(hexAddress)

    def reset(self) -> None:
        """
        Resets the model to its original state in any attached views.
        """
        self.beginResetModel()
        self.nextSlot = 0
        self.clearHistory()
        self.endResetModel()

    def clearHistory(self) -> None:
        """
        Clears the history of previously modified bytes.
        """
        self.previouslyModifiedBytes.clear()
        self.modifiedBytes.clear()

    def stepHistory(self) -> None:
        """
        Advances one step in the history of previously modified bytes.
        """
        copyOfPrevious = self.previouslyModifiedBytes.copy()
        self.previouslyModifiedBytes = self.modifiedBytes.copy()
        self.modifiedBytes.clear()
        for (slot, memoryRow) in copyOfPrevious + self.previouslyModifiedBytes:
            memoryBank = self.getMemoryBankInSlot(slot)
            topLeft = self.createIndex(memoryRow, 0, memoryBank.getMemoryItem(memoryRow))
            bottomRight = self.createIndex(memoryRow, 0, memoryBank.getMemoryItem(memoryRow))
            if topLeft.isValid() and bottomRight.isValid():
                self.dataChanged.emit(topLeft, bottomRight)

    # ======================================================================
    # QAbstractItemModel abstract methods implementations
    # ======================================================================

    # REQUIRED: Return the number of rows
    @override
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # pyright: ignore[reportIncompatibleMethodOverride]
        if not parent.isValid():  # Level 0 (Memory)
            return self.nextSlot
        if not parent.parent().isValid():  # Level 1 (Memory Bank)
            return cast(MemoryBank, cast(object, parent.internalPointer())).length
        # Level 2 Memory Bank contents
        return 0  # no children

    # REQUIRED: Return the number of columns
    @override
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # pyright: ignore[reportIncompatibleMethodOverride]
        if not parent.isValid():  # Level 0 (Memory)
            return 1
        if not parent.parent().isValid():  # Level 1 (Memory Bank)
            return 1
        # Level 2 Memory Bank contents
        return 2

    # REQUIRED: The core method to retrieve data for the view
    @override
    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> str | None:  # pyright: ignore[reportIncompatibleMethodOverride]
        if not index.isValid():
            return None  # Invalid index
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        item: object = cast(object, index.internalPointer())
        if isinstance(item, MemoryBank):
            return str(item)
        return None

    # OPTIONAL: index
    @override
    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:  # pyright: ignore[reportIncompatibleMethodOverride]
        if not self.hasIndex(row, column, parent):
            return QModelIndex()  # invalid index -> return empty QModelIndex()
        if not parent.isValid():  # Level 0: memory
            return self.createIndex(row, 0, MemoryBankItem(self._memoryBanks[row]))
        if not parent.parent().isValid():  # Level 1: memory bank
            memoryBank = cast(MemoryBank, cast(object, parent.internalPointer()))
            return self.createIndex(row, 0, memoryBank.getMemoryItem(row))
        return QModelIndex()

    # OPTIONAL: parent
    @override
    def parent(self, child: QModelIndex = QModelIndex()) -> QModelIndex:  # pyright: ignore[reportIncompatibleMethodOverride]
        if not child.isValid():
            return QModelIndex()
        childItem: object = cast(object, child.internalPointer())
        if childItem is None:
            return QModelIndex()
        if isinstance(childItem, MemoryBank) or isinstance(childItem, MemoryBankItem):
            return QModelIndex()
        if isinstance(childItem, MemoryItem):
            memoryBank = cast(MemoryBank, childItem.parent)
            return self.createIndex(memoryBank.slot, 0, MemoryBankItem(memoryBank))
        return QModelIndex()  # Something went wrong

    # OPTIONAL: flags
    @override
    def flags(self, index: QModelIndex) -> Qt.ItemFlag:  # pyright: ignore[reportIncompatibleMethodOverride]
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    # OPTIONAL: headerData
    @override
    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> str | None:  # pyright: ignore[reportIncompatibleMethodOverride]
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return ('Address', 'Content ')[section]
        return None
