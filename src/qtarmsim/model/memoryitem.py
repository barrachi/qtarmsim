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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .memorybank import MemoryBank


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
