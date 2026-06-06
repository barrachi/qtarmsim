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

# Run with .venv/bin/python -m unittest src.qtarmsim.test.test_memorybank -v 2>&1

import unittest

from ..model.memorybank import MemoryBank
from ..model.memoryitem import MemoryItem


class TestMemoryBankInit(unittest.TestCase):

    def setUp(self) -> None:
        MemoryItem._instance_cache.clear()

    def test_attributes(self) -> None:
        bank = MemoryBank(1, "RAM", "0x00001000", ["0xAA", "0xBB", "0xCC", "0xDD"])
        self.assertEqual(bank.slot, 1)
        self.assertEqual(bank.memType, "RAM")
        self.assertEqual(bank.hexStartAddress, "0x00001000")
        self.assertEqual(bank.startAddress, 0x1000)

    def test_padding_unaligned(self) -> None:
        # 3 bytes → padded to 4
        bank = MemoryBank(0, "RAM", "0x00000000", ["0x01", "0x02", "0x03"])
        self.assertEqual(bank.length, 4)
        self.assertEqual(bank.bytes[3], "0x00")

    def test_no_extra_padding_when_aligned(self) -> None:
        # 4 bytes already word-aligned → length stays 4
        bank = MemoryBank(0, "RAM", "0x00000000", ["0x01", "0x02", "0x03", "0x04"])
        self.assertEqual(bank.length, 4)

    def test_end_address(self) -> None:
        bank = MemoryBank(0, "RAM", "0x00001000", ["0x00"] * 4)
        self.assertEqual(bank.endAddress, 0x1003)

    def test_str(self) -> None:
        bank = MemoryBank(0, "RAM", "0x00001000", ["0x00"] * 4)
        self.assertEqual(str(bank), "RAM 0x00001000")

    def test_str_rom(self) -> None:
        bank = MemoryBank(0, "ROM", "0x00008000", ["0x00"] * 4)
        self.assertEqual(str(bank), "ROM 0x00008000")


class TestMemoryBankByteAccess(unittest.TestCase):
    """Bank: [0xAA, 0xBB, 0xCC, 0xDD] at 0x1000."""

    def setUp(self) -> None:
        MemoryItem._instance_cache.clear()
        self.bank = MemoryBank(0, "RAM", "0x00001000", ["0xAA", "0xBB", "0xCC", "0xDD"])

    def test_get_byte_first(self) -> None:
        self.assertEqual(self.bank.getByte("0x00001000"), "0xAA")

    def test_get_byte_middle(self) -> None:
        self.assertEqual(self.bank.getByte("0x00001001"), "0xBB")
        self.assertEqual(self.bank.getByte("0x00001002"), "0xCC")

    def test_get_byte_last(self) -> None:
        self.assertEqual(self.bank.getByte("0x00001003"), "0xDD")

    def test_set_byte_returns_index(self) -> None:
        self.assertEqual(self.bank.setByte("0x00001001", "0xFF"), 1)

    def test_set_byte_modifies_value(self) -> None:
        self.bank.setByte("0x00001000", "0xDE")
        self.assertEqual(self.bank.getByte("0x00001000"), "0xDE")

    def test_get_byte_before_start_raises(self) -> None:
        with self.assertRaises(IndexError):
            self.bank.getByte("0x00000fff")

    def test_get_byte_past_end_raises(self) -> None:
        with self.assertRaises(IndexError):
            self.bank.getByte("0x00001004")


class TestMemoryBankWordAccess(unittest.TestCase):
    """Bank: [0x10..0x80] (8 bytes) at 0x1000."""

    def setUp(self) -> None:
        MemoryItem._instance_cache.clear()
        self.bank = MemoryBank(0, "RAM", "0x00001000",
                               ["0x10", "0x20", "0x30", "0x40",
                                "0x50", "0x60", "0x70", "0x80"])

    def test_get_word_little_endian(self) -> None:
        # bytes[0..3] = [0x10, 0x20, 0x30, 0x40] → 0x40302010
        self.assertEqual(self.bank.getWord("0x00001000"), "0x40302010")

    def test_get_word_second_word(self) -> None:
        # bytes[4..7] = [0x50, 0x60, 0x70, 0x80] → 0x80706050
        self.assertEqual(self.bank.getWord("0x00001004"), "0x80706050")

    def test_set_word_stores_little_endian(self) -> None:
        self.bank.setWord("0x00001000", "0xAABBCCDD")
        self.assertEqual(self.bank.bytes[0], "0xDD")
        self.assertEqual(self.bank.bytes[1], "0xCC")
        self.assertEqual(self.bank.bytes[2], "0xBB")
        self.assertEqual(self.bank.bytes[3], "0xAA")

    def test_set_word_returns_index(self) -> None:
        self.assertEqual(self.bank.setWord("0x00001000", "0x12345678"), 0)

    def test_get_word_roundtrip(self) -> None:
        self.bank.setWord("0x00001000", "0x12345678")
        self.assertEqual(self.bank.getWord("0x00001000"), "0x12345678")


class TestMemoryBankContains(unittest.TestCase):
    """Bank: 4 bytes at 0x1000 (addresses 0x1000–0x1003)."""

    def setUp(self) -> None:
        MemoryItem._instance_cache.clear()
        self.bank = MemoryBank(0, "RAM", "0x00001000", ["0x00"] * 4)

    def test_contains_start(self) -> None:
        self.assertTrue(self.bank.contains("0x00001000"))

    def test_contains_end(self) -> None:
        self.assertTrue(self.bank.contains("0x00001003"))

    def test_contains_middle(self) -> None:
        self.assertTrue(self.bank.contains("0x00001001"))

    def test_not_contains_before(self) -> None:
        self.assertFalse(self.bank.contains("0x00000fff"))

    def test_not_contains_after(self) -> None:
        self.assertFalse(self.bank.contains("0x00001004"))


class TestMemoryBankGetMemoryItem(unittest.TestCase):

    def setUp(self) -> None:
        MemoryItem._instance_cache.clear()
        self.bank = MemoryBank(0, "RAM", "0x00001000", ["0xAA", "0xBB", "0xCC", "0xDD"])

    def test_address_row0(self) -> None:
        self.assertEqual(self.bank.getMemoryItem(0).hexAddress, "0x00001000")

    def test_value_row0(self) -> None:
        self.assertEqual(self.bank.getMemoryItem(0).hexValue, "0xAA")

    def test_address_row2(self) -> None:
        self.assertEqual(self.bank.getMemoryItem(2).hexAddress, "0x00001002")

    def test_value_row2(self) -> None:
        self.assertEqual(self.bank.getMemoryItem(2).hexValue, "0xCC")

    def test_same_instance_from_cache(self) -> None:
        item1 = self.bank.getMemoryItem(0)
        item2 = self.bank.getMemoryItem(0)
        self.assertIs(item1, item2)


if __name__ == "__main__":
    unittest.main()
