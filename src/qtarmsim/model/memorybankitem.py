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

from .memorybank import MemoryBank


class MemoryBankItem:
    """
    Used to provide the same functionality as a MemoryBank, but avoiding python changing its
    reference, which leads to memory leaks when using indexes from QAbstractItemModel.createIndex.
    """

    _instance_cache: dict[int, MemoryBankItem] = {}

    def __new__(cls, memoryBank: MemoryBank) -> MemoryBankItem:
        if memoryBank.slot not in cls._instance_cache:
            cls._instance_cache[memoryBank.slot] = super().__new__(cls)
        return cls._instance_cache[memoryBank.slot]

    def __init__(self, memoryBank: MemoryBank) -> None:
        self.slot: int = memoryBank.slot
        self.memoryBank: MemoryBank = memoryBank

    def __getattr__(self, item: str) -> object:
        return getattr(self.memoryBank, item)  # pyright: ignore[reportAny]
