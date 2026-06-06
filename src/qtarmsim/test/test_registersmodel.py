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

# Run with: .venv/bin/python -m unittest src.qtarmsim.test.test_registersmodel -v

import sys
import unittest

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import QApplication

from ..model.registersmodel import RegistersModel


def _make_model() -> RegistersModel:
    model = RegistersModel()
    # Override class-level mutable lists with instance-level ones
    model.modified_registers = []
    model.previously_modified_registers = []
    return model


class TestRegistersModelStructure(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self) -> None:
        self.model = _make_model()

    def test_root_row_count_is_one_bank(self) -> None:
        self.assertEqual(self.model.rowCount(QModelIndex()), 1)

    def test_bank_row_count_is_sixteen(self) -> None:
        bankIndex = self.model.index(0, 0, QModelIndex())
        self.assertEqual(self.model.rowCount(bankIndex), 16)

    def test_column_count_is_two(self) -> None:
        self.assertEqual(self.model.columnCount(QModelIndex()), 2)

    def test_bank_index_is_valid(self) -> None:
        self.assertTrue(self.model.index(0, 0, QModelIndex()).isValid())

    def test_register_index_is_valid(self) -> None:
        bankIndex = self.model.index(0, 0, QModelIndex())
        self.assertTrue(self.model.index(0, 0, bankIndex).isValid())

    def test_register_out_of_range_is_invalid(self) -> None:
        bankIndex = self.model.index(0, 0, QModelIndex())
        self.assertFalse(self.model.index(16, 0, bankIndex).isValid())

    def test_parent_of_register_is_valid(self) -> None:
        bankIndex = self.model.index(0, 0, QModelIndex())
        registerIndex = self.model.index(0, 0, bankIndex)
        self.assertTrue(self.model.parent(registerIndex).isValid())

    def test_parent_of_register_has_bank_row(self) -> None:
        bankIndex = self.model.index(0, 0, QModelIndex())
        registerIndex = self.model.index(0, 0, bankIndex)
        self.assertEqual(self.model.parent(registerIndex).row(), 0)

    def test_parent_of_bank_is_invalid(self) -> None:
        bankIndex = self.model.index(0, 0, QModelIndex())
        self.assertFalse(self.model.parent(bankIndex).isValid())


class TestRegistersModelData(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self) -> None:
        self.model = _make_model()
        self.bankIndex = self.model.index(0, 0, QModelIndex())

    def test_bank_name(self) -> None:
        self.assertEqual(self.model.data(self.bankIndex), 'General')

    def test_invalid_index_returns_none(self) -> None:
        self.assertIsNone(self.model.data(QModelIndex()))

    def test_r0_name(self) -> None:
        idx = self.model.index(0, 0, self.bankIndex)
        self.assertEqual(self.model.data(idx), 'r0')

    def test_r13_name(self) -> None:
        idx = self.model.index(13, 0, self.bankIndex)
        self.assertEqual(self.model.data(idx), 'r13 (SP)')

    def test_r14_name(self) -> None:
        idx = self.model.index(14, 0, self.bankIndex)
        self.assertEqual(self.model.data(idx), 'r14 (LR)')

    def test_r15_name(self) -> None:
        idx = self.model.index(15, 0, self.bankIndex)
        self.assertEqual(self.model.data(idx), 'r15 (PC)')

    def test_initial_register_value_is_zero(self) -> None:
        idx = self.model.index(0, 1, self.bankIndex)
        self.assertEqual(self.model.data(idx), '0x00000000')

    def test_all_initial_values_are_zero(self) -> None:
        for reg in range(16):
            idx = self.model.index(reg, 1, self.bankIndex)
            self.assertEqual(self.model.data(idx), '0x00000000', f"r{reg} not zero")

    def test_non_display_role_on_register_returns_none(self) -> None:
        idx = self.model.index(0, 0, self.bankIndex)
        self.assertIsNone(self.model.data(idx, Qt.ItemDataRole.DecorationRole))

    def test_non_display_role_on_bank_returns_none(self) -> None:
        self.assertIsNone(self.model.data(self.bankIndex, Qt.ItemDataRole.DecorationRole))


class TestRegistersModelFlags(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self) -> None:
        self.model = _make_model()
        self.bankIndex = self.model.index(0, 0, QModelIndex())

    def test_invalid_index_returns_no_flags(self) -> None:
        self.assertEqual(self.model.flags(QModelIndex()), Qt.ItemFlag.NoItemFlags)

    def test_bank_is_enabled_only(self) -> None:
        flags = self.model.flags(self.bankIndex)
        self.assertTrue(flags & Qt.ItemFlag.ItemIsEnabled)
        self.assertFalse(flags & Qt.ItemFlag.ItemIsEditable)
        self.assertFalse(flags & Qt.ItemFlag.ItemIsSelectable)

    def test_register_name_column_not_editable(self) -> None:
        idx = self.model.index(0, 0, self.bankIndex)
        flags = self.model.flags(idx)
        self.assertTrue(flags & Qt.ItemFlag.ItemIsEnabled)
        self.assertTrue(flags & Qt.ItemFlag.ItemIsSelectable)
        self.assertFalse(flags & Qt.ItemFlag.ItemIsEditable)

    def test_register_value_column_is_editable(self) -> None:
        idx = self.model.index(0, 1, self.bankIndex)
        flags = self.model.flags(idx)
        self.assertTrue(flags & Qt.ItemFlag.ItemIsEnabled)
        self.assertTrue(flags & Qt.ItemFlag.ItemIsSelectable)
        self.assertTrue(flags & Qt.ItemFlag.ItemIsEditable)


class TestRegistersModelSetRegister(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self) -> None:
        self.model = _make_model()

    def test_set_register_updates_value(self) -> None:
        self.model.setRegister(0, '0x12345678')
        self.assertEqual(self.model.getRegister(0), '0x12345678')

    def test_set_register_adds_to_modified(self) -> None:
        self.model.setRegister(3, '0xDEADBEEF')
        self.assertIn(3, self.model.modified_registers)

    def test_set_register_above_15_ignored(self) -> None:
        self.model.setRegister(16, '0x12345678')
        self.assertEqual(len(self.model.modified_registers), 0)

    def test_get_register_initial_value(self) -> None:
        self.assertEqual(self.model.getRegister(0), '0x00000000')

    def test_get_register_all_initial(self) -> None:
        for i in range(16):
            self.assertEqual(self.model.getRegister(i), '0x00000000', f"r{i} not zero")


class TestRegistersModelHistory(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self) -> None:
        self.model = _make_model()

    def test_clear_history_empties_modified(self) -> None:
        self.model.setRegister(0, '0x00000001')
        self.model.clearHistory()
        self.assertEqual(len(self.model.modified_registers), 0)

    def test_clear_history_empties_previously_modified(self) -> None:
        self.model.setRegister(0, '0x00000001')
        self.model.stepHistory()
        self.model.clearHistory()
        self.assertEqual(len(self.model.previously_modified_registers), 0)

    def test_step_history_moves_modified_to_previous(self) -> None:
        self.model.setRegister(2, '0x00000001')
        self.model.stepHistory()
        self.assertIn(2, self.model.previously_modified_registers)

    def test_step_history_clears_modified(self) -> None:
        self.model.setRegister(2, '0x00000001')
        self.model.stepHistory()
        self.assertEqual(len(self.model.modified_registers), 0)

    def test_step_history_twice_clears_old_previous(self) -> None:
        self.model.setRegister(1, '0x00000001')
        self.model.stepHistory()
        self.model.setRegister(2, '0x00000002')
        self.model.stepHistory()
        self.assertNotIn(1, self.model.previously_modified_registers)
        self.assertIn(2, self.model.previously_modified_registers)


class TestRegistersModelHighlight(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self) -> None:
        self.model = _make_model()

    def test_initial_highlight_is_none(self) -> None:
        self.assertIsNone(self.model.highlighted_register)

    def test_highlight_sets_register(self) -> None:
        self.model.highlightRegister(5)
        self.assertEqual(self.model.highlighted_register, 5)

    def test_unhighlight_clears_register(self) -> None:
        self.model.highlightRegister(5)
        self.model.unHighlightRegister()
        self.assertIsNone(self.model.highlighted_register)

    def test_unhighlight_when_none_does_not_raise(self) -> None:
        self.model.unHighlightRegister()  # should not raise


if __name__ == '__main__':
    unittest.main()
