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

# Run with .venv/bin/python -m unittest src.qtarmsim.test.test_memorybankitem -v

import unittest

from ..model.memorybank import MemoryBank
from ..model.memorybankitem import MemoryBankItem
from ..model.memorybank import MemoryItem


class TestMemoryBankItemAttributes(unittest.TestCase):

    def setUp(self) -> None:
        MemoryBankItem._instance_cache.clear()
        MemoryItem._instance_cache.clear()

    def test_slot(self) -> None:
        bank = MemoryBank(2, "RAM", "0x00001000", ["0x00"] * 4)
        item = MemoryBankItem(bank)
        self.assertEqual(item.slot, 2)

    def test_memorybank(self) -> None:
        bank = MemoryBank(0, "RAM", "0x00001000", ["0x00"] * 4)
        item = MemoryBankItem(bank)
        self.assertIs(item.memoryBank, bank)


class TestMemoryBankItemCache(unittest.TestCase):

    def setUp(self) -> None:
        MemoryBankItem._instance_cache.clear()
        MemoryItem._instance_cache.clear()

    def test_same_slot_returns_same_instance(self) -> None:
        bank = MemoryBank(0, "RAM", "0x00001000", ["0x00"] * 4)
        item1 = MemoryBankItem(bank)
        item2 = MemoryBankItem(bank)
        self.assertIs(item1, item2)

    def test_same_slot_updates_memorybank(self) -> None:
        bank1 = MemoryBank(0, "RAM", "0x00001000", ["0x00"] * 4)
        bank2 = MemoryBank(0, "ROM", "0x00002000", ["0xFF"] * 4)
        item = MemoryBankItem(bank1)
        item = MemoryBankItem(bank2)
        self.assertIs(item.memoryBank, bank2)

    def test_same_slot_slot_unchanged_on_update(self) -> None:
        bank1 = MemoryBank(0, "RAM", "0x00001000", ["0x00"] * 4)
        bank2 = MemoryBank(0, "ROM", "0x00002000", ["0xFF"] * 4)
        MemoryBankItem(bank1)
        item = MemoryBankItem(bank2)
        self.assertEqual(item.slot, 0)

    def test_different_slots_different_instances(self) -> None:
        bank0 = MemoryBank(0, "RAM", "0x00001000", ["0x00"] * 4)
        bank1 = MemoryBank(1, "ROM", "0x00002000", ["0xFF"] * 4)
        item0 = MemoryBankItem(bank0)
        item1 = MemoryBankItem(bank1)
        self.assertIsNot(item0, item1)


class TestMemoryBankItemGetattr(unittest.TestCase):

    def setUp(self) -> None:
        MemoryBankItem._instance_cache.clear()
        MemoryItem._instance_cache.clear()
        self.bank = MemoryBank(0, "ROM", "0x00008000", ["0xAA"] * 4)
        self.item = MemoryBankItem(self.bank)

    def test_delegates_memtype(self) -> None:
        self.assertEqual(self.item.memType, "ROM")

    def test_delegates_hex_start_address(self) -> None:
        self.assertEqual(self.item.hexStartAddress, "0x00008000")

    def test_delegates_start_address(self) -> None:
        self.assertEqual(self.item.startAddress, 0x8000)

    def test_delegates_length(self) -> None:
        self.assertEqual(self.item.length, 4)


if __name__ == "__main__":
    unittest.main()
