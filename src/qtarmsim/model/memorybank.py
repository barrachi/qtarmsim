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

from typing_extensions import override


class MemoryItem:
    """Stores the information of a memory item."""

    _instance_cache: dict[str, MemoryItem] = {}

    def __new__(cls, parent: MemoryBank, hexAddress: str, hexValue: str) -> MemoryItem:
        _ = parent, hexValue  # not used in __new__; handled by __init__
        if hexAddress not in cls._instance_cache:
            instance = super().__new__(cls)
            cls._instance_cache[hexAddress] = instance
        return cls._instance_cache[hexAddress]

    def __init__(self, parent: MemoryBank, hexAddress: str, hexValue: str) -> None:
        self.parent: MemoryBank = parent
        self.hexAddress: str = hexAddress
        self.hexValue: str = hexValue

    @property
    def memoryBank(self) -> MemoryBank:
        return self.parent


class MemoryBank:

    def __init__(self, slot: int, memType: str, hexStartAddress: str, memBytes: list[str]) -> None:
        """Initializes a memory bank instance.

        @parma slot: The slot this memory bank has been inserted into.
        @param memType: The memory type, one of RAM or ROM.
        @param hexStartAddress: The starting address in hexadecimal.
        @param memBytes: The bytes to be stored in this memory bank.
        """
        self.slot: int = slot
        self.memType: str = memType
        self.hexStartAddress: str = hexStartAddress
        self.bytes: list[str] = memBytes
        self.bytes += ['0x00'] * ((4 - len(self.bytes) % 4) % 4)  # Round data to the next word boundary
        self.startAddress: int = int(hexStartAddress, 16)
        self.endAddress: int = self.startAddress + self.length - 1

    @override
    def __str__(self) -> str:
        return f"{self.memType} {self.hexStartAddress}"

    @property
    def length(self) -> int:
        return len(self.bytes)

    def index(self, hexAddress: str) -> int:
        """Given a hexadecimal hexAddress, returns the corresponding row"""
        intAddress = int(hexAddress, 16)
        index = intAddress - self.startAddress
        if index < 0 or index >= self.length:
            raise IndexError(f"memory bank at slot {self.slot}: {hexAddress} is out of range")
        return index

    def getByte(self, hexAddress: str) -> str:
        index = self.index(hexAddress)
        return self.bytes[index]

    def setByte(self, hexAddress: str, hexByte: str) -> int:
        index = self.index(hexAddress)
        self.bytes[index] = hexByte
        return index

    def getWord(self, hexAddress: str) -> str:
        index = self.index(hexAddress)
        hexWord = "0x"
        for i in range(4):
            indexByte = index + 3 - i  # 3-i due to Little Endian
            hexWord += self.bytes[indexByte][2:]
        return hexWord

    def setWord(self, hexAddress: str, hexWord: str) -> int:
        index = self.index(hexAddress)
        for i in range(4):
            hexByte = "0x{}".format(hexWord[2 + i * 2:4 + i * 2])
            indexByte = index + 3 - i  # 3-i due to Little Endian
            self.bytes[indexByte] = hexByte
        return index

    def getMemoryItem(self, row: int) -> MemoryItem:
        # The return value must persist to avoid the next error:
        #     terminated by signal SIGSEGV (Address boundary error)
        return MemoryItem(self, f"0x{self.startAddress + row:08x}", self.bytes[row])

    def contains(self, hexAddress: str) -> bool:
        intAddress = int(hexAddress, 16)
        return self.startAddress <= intAddress <= self.endAddress
