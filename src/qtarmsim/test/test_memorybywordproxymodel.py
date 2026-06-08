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

# Run with .venv/bin/python -m unittest src.qtarmsim.test.test_memorybywordproxymodel -v

import sys
import unittest

from PySide6.QtCore import QModelIndex
from PySide6.QtWidgets import QApplication

from ..model.memorybank import MemoryBank
from ..model.memorybankitem import MemoryBankItem
from ..model.memorybank import MemoryItem
from ..model.memorymodel import MemoryModel
from ..model.memorybywordproxymodel import MemoryByWordProxyModel


def _make_models() -> tuple[MemoryModel, MemoryByWordProxyModel]:
    """
    Two 8-byte banks:
      slot 0 — ROM at 0x10000000: bytes 0x00..0x07
      slot 1 — RAM at 0x20000000: bytes 0x00..0x07
    Each bank has 2 words (8 bytes / 4 = 2).
    """
    memModel = MemoryModel()
    bank0 = MemoryBank(0, 'ROM', '0x10000000', ['0x{:02x}'.format(i) for i in range(8)])
    bank1 = MemoryBank(1, 'RAM', '0x20000000', ['0x{:02x}'.format(i) for i in range(8)])
    memModel._memoryBanks = [bank0, bank1]   # instance attr shadows class attr
    memModel.nextSlot = 2
    memModel.modifiedBytes = []              # instance attr to avoid class-level sharing
    memModel.previouslyModifiedBytes = []
    proxy = MemoryByWordProxyModel()
    proxy.setSourceModel(memModel)
    return memModel, proxy


class TestRowAndColumnCount(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self) -> None:
        MemoryItem._instance_cache.clear()
        MemoryBankItem._instance_cache.clear()
        self.memModel, self.proxy = _make_models()

    def test_row_count_root_equals_number_of_banks(self) -> None:
        self.assertEqual(self.proxy.rowCount(QModelIndex()), 2)

    def test_row_count_bank_equals_number_of_words(self) -> None:
        # 8-byte bank → 2 words
        bankIndex = self.proxy.index(0, 0, QModelIndex())
        self.assertEqual(self.proxy.rowCount(bankIndex), 2)

    def test_row_count_word_is_zero(self) -> None:
        # Word rows are leaf nodes: rowCount must be 0 so QTreeView treats
        # double-click as "start editor" rather than "expand row".
        bankIndex = self.proxy.index(0, 0, QModelIndex())
        wordIndex = self.proxy.index(0, 0, bankIndex)
        self.assertEqual(self.proxy.rowCount(wordIndex), 0)

    def test_column_count_is_always_two(self) -> None:
        bankIndex = self.proxy.index(0, 0, QModelIndex())
        wordIndex = self.proxy.index(0, 0, bankIndex)
        self.assertEqual(self.proxy.columnCount(QModelIndex()), 2)
        self.assertEqual(self.proxy.columnCount(bankIndex), 2)
        self.assertEqual(self.proxy.columnCount(wordIndex), 2)


class TestIndex(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self) -> None:
        MemoryItem._instance_cache.clear()
        MemoryBankItem._instance_cache.clear()
        self.memModel, self.proxy = _make_models()

    def test_bank_index_is_valid(self) -> None:
        self.assertTrue(self.proxy.index(0, 0, QModelIndex()).isValid())
        self.assertTrue(self.proxy.index(1, 0, QModelIndex()).isValid())

    def test_bank_index_out_of_range_is_invalid(self) -> None:
        self.assertFalse(self.proxy.index(2, 0, QModelIndex()).isValid())

    def test_bank_index_pointer_is_memorybankitem(self) -> None:
        bankIndex = self.proxy.index(0, 0, QModelIndex())
        self.assertIsInstance(bankIndex.internalPointer(), MemoryBankItem)

    def test_second_bank_index_has_correct_slot(self) -> None:
        bankIndex = self.proxy.index(1, 0, QModelIndex())
        self.assertEqual(bankIndex.internalPointer().slot, 1)

    def test_word_index_is_valid(self) -> None:
        bankIndex = self.proxy.index(0, 0, QModelIndex())
        self.assertTrue(self.proxy.index(0, 0, bankIndex).isValid())
        self.assertTrue(self.proxy.index(1, 0, bankIndex).isValid())

    def test_word_index_out_of_range_is_invalid(self) -> None:
        bankIndex = self.proxy.index(0, 0, QModelIndex())
        self.assertFalse(self.proxy.index(2, 0, bankIndex).isValid())

    def test_word_index_pointer_is_memoryitem(self) -> None:
        bankIndex = self.proxy.index(0, 0, QModelIndex())
        wordIndex = self.proxy.index(0, 0, bankIndex)
        self.assertIsInstance(wordIndex.internalPointer(), MemoryItem)

    def test_first_word_points_to_first_byte(self) -> None:
        bankIndex = self.proxy.index(0, 0, QModelIndex())
        wordIndex = self.proxy.index(0, 0, bankIndex)
        item: MemoryItem = wordIndex.internalPointer()
        self.assertEqual(item.hexAddress, '0x10000000')

    def test_second_word_points_to_fifth_byte(self) -> None:
        bankIndex = self.proxy.index(0, 0, QModelIndex())
        wordIndex = self.proxy.index(1, 0, bankIndex)
        item: MemoryItem = wordIndex.internalPointer()
        self.assertEqual(item.hexAddress, '0x10000004')


class TestParent(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self) -> None:
        MemoryItem._instance_cache.clear()
        MemoryBankItem._instance_cache.clear()
        self.memModel, self.proxy = _make_models()

    def test_parent_of_invalid_index_is_invalid(self) -> None:
        self.assertFalse(self.proxy.parent(QModelIndex()).isValid())

    def test_parent_of_bank_is_invalid(self) -> None:
        bankIndex = self.proxy.index(0, 0, QModelIndex())
        self.assertFalse(self.proxy.parent(bankIndex).isValid())

    def test_parent_of_word_is_valid(self) -> None:
        bankIndex = self.proxy.index(0, 0, QModelIndex())
        wordIndex = self.proxy.index(0, 0, bankIndex)
        self.assertTrue(self.proxy.parent(wordIndex).isValid())

    def test_parent_of_word_is_memorybankitem(self) -> None:
        bankIndex = self.proxy.index(0, 0, QModelIndex())
        wordIndex = self.proxy.index(0, 0, bankIndex)
        self.assertIsInstance(self.proxy.parent(wordIndex).internalPointer(), MemoryBankItem)

    def test_parent_of_word_has_correct_row(self) -> None:
        # Word in bank 1 → parent row must be 1
        bankIndex = self.proxy.index(1, 0, QModelIndex())
        wordIndex = self.proxy.index(0, 0, bankIndex)
        self.assertEqual(self.proxy.parent(wordIndex).row(), 1)


class TestMapFromSource(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self) -> None:
        MemoryItem._instance_cache.clear()
        MemoryBankItem._instance_cache.clear()
        self.memModel, self.proxy = _make_models()

    def test_invalid_source_maps_to_invalid(self) -> None:
        self.assertFalse(self.proxy.mapFromSource(QModelIndex()).isValid())

    def test_source_bank_maps_to_proxy_bank(self) -> None:
        srcBank = self.memModel.index(0, 0, QModelIndex())
        proxyBank = self.proxy.mapFromSource(srcBank)
        self.assertTrue(proxyBank.isValid())
        self.assertIsInstance(proxyBank.internalPointer(), MemoryBankItem)

    def test_source_bank_row_preserved(self) -> None:
        srcBank = self.memModel.index(1, 0, QModelIndex())
        proxyBank = self.proxy.mapFromSource(srcBank)
        self.assertEqual(proxyBank.row(), 1)

    def test_source_byte_row0_maps_to_proxy_word_row0(self) -> None:
        srcBank = self.memModel.index(0, 0, QModelIndex())
        srcByte = self.memModel.index(0, 0, srcBank)
        proxyWord = self.proxy.mapFromSource(srcByte)
        self.assertTrue(proxyWord.isValid())
        self.assertEqual(proxyWord.row(), 0)

    def test_source_byte_row4_maps_to_proxy_word_row1(self) -> None:
        srcBank = self.memModel.index(0, 0, QModelIndex())
        srcByte = self.memModel.index(4, 0, srcBank)
        proxyWord = self.proxy.mapFromSource(srcByte)
        self.assertTrue(proxyWord.isValid())
        self.assertEqual(proxyWord.row(), 1)


class TestMapToSource(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self) -> None:
        MemoryItem._instance_cache.clear()
        MemoryBankItem._instance_cache.clear()
        self.memModel, self.proxy = _make_models()

    def test_invalid_proxy_maps_to_invalid(self) -> None:
        self.assertFalse(self.proxy.mapToSource(QModelIndex()).isValid())

    def test_proxy_bank_maps_to_source_bank(self) -> None:
        proxyBank = self.proxy.index(0, 0, QModelIndex())
        srcBank = self.proxy.mapToSource(proxyBank)
        self.assertTrue(srcBank.isValid())
        self.assertIsInstance(srcBank.internalPointer(), MemoryBankItem)

    def test_proxy_bank_row_preserved(self) -> None:
        proxyBank = self.proxy.index(1, 0, QModelIndex())
        srcBank = self.proxy.mapToSource(proxyBank)
        self.assertEqual(srcBank.row(), 1)

    def test_proxy_word_row0_maps_to_source_byte_row0(self) -> None:
        proxyBank = self.proxy.index(0, 0, QModelIndex())
        proxyWord = self.proxy.index(0, 0, proxyBank)
        srcByte = self.proxy.mapToSource(proxyWord)
        self.assertTrue(srcByte.isValid())
        self.assertEqual(srcByte.row(), 0)

    def test_proxy_word_row1_maps_to_source_byte_row4(self) -> None:
        proxyBank = self.proxy.index(0, 0, QModelIndex())
        proxyWord = self.proxy.index(1, 0, proxyBank)
        srcByte = self.proxy.mapToSource(proxyWord)
        self.assertTrue(srcByte.isValid())
        self.assertEqual(srcByte.row(), 4)


if __name__ == '__main__':
    unittest.main()
