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

# Run with: .venv/bin/python -m unittest src.qtarmsim.test.test_common -v

import sys
import unittest

from PySide6.QtWidgets import QApplication

from ..model.common import DataTypes, InputToHex


class TestInputToHexNonString(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication(sys.argv)
        cls.c = InputToHex()

    def test_integer_input_returns_none(self) -> None:
        value, _ = self.c.convert(42)  # type: ignore[arg-type]
        self.assertIsNone(value)

    def test_integer_input_returns_error_msg(self) -> None:
        _, err = self.c.convert(42)  # type: ignore[arg-type]
        self.assertTrue(len(err) > 0)

    def test_none_input_returns_none(self) -> None:
        value, _ = self.c.convert(None)  # type: ignore[arg-type]
        self.assertIsNone(value)


class TestInputToHexEmpty(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication(sys.argv)
        cls.c = InputToHex()

    def test_empty_string_returns_none(self) -> None:
        value, _ = self.c.convert('')
        self.assertIsNone(value)

    def test_empty_string_returns_no_error(self) -> None:
        _, err = self.c.convert('')
        self.assertEqual(err, '')


class TestInputToHexIntegers(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication(sys.argv)
        cls.c = InputToHex()

    def test_decimal(self) -> None:
        value, err = self.c.convert('42')
        self.assertEqual(value, '0x0000002A')
        self.assertEqual(err, '')

    def test_hex_prefix(self) -> None:
        value, err = self.c.convert('0x1F')
        self.assertEqual(value, '0x0000001F')
        self.assertEqual(err, '')

    def test_binary_prefix(self) -> None:
        value, err = self.c.convert('0b1010')
        self.assertEqual(value, '0x0000000A')
        self.assertEqual(err, '')

    def test_octal_prefix(self) -> None:
        value, err = self.c.convert('0o17')
        self.assertEqual(value, '0x0000000F')
        self.assertEqual(err, '')

    def test_zero(self) -> None:
        value, _ = self.c.convert('0')
        self.assertEqual(value, '0x00000000')

    def test_max_unsigned(self) -> None:
        value, err = self.c.convert('4294967295')
        self.assertEqual(value, '0xFFFFFFFF')
        self.assertEqual(err, '')

    def test_negative_minus_one(self) -> None:
        value, err = self.c.convert('-1')
        self.assertEqual(value, '0xFFFFFFFF')
        self.assertEqual(err, '')

    def test_negative_max(self) -> None:
        value, err = self.c.convert('-2147483648')
        self.assertEqual(value, '0x80000000')
        self.assertEqual(err, '')

    def test_too_large_positive_returns_none(self) -> None:
        value, err = self.c.convert('4294967296')
        self.assertIsNone(value)
        self.assertTrue(len(err) > 0)

    def test_too_small_negative_returns_none(self) -> None:
        value, err = self.c.convert('-2147483649')
        self.assertIsNone(value)
        self.assertTrue(len(err) > 0)

    def test_invalid_text_returns_none(self) -> None:
        value, err = self.c.convert('notanumber')
        self.assertIsNone(value)
        self.assertTrue(len(err) > 0)


class TestInputToHexStrings(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication(sys.argv)
        cls.c = InputToHex()

    def test_single_quoted_char(self) -> None:
        value, err = self.c.convert("'A'")
        self.assertEqual(value, '0x00000041')
        self.assertEqual(err, '')

    def test_double_quoted_char(self) -> None:
        value, err = self.c.convert('"A"')
        self.assertEqual(value, '0x00000041')
        self.assertEqual(err, '')

    def test_empty_quoted_string(self) -> None:
        value, err = self.c.convert("''")
        self.assertEqual(value, '0x00000000')
        self.assertEqual(err, '')

    def test_two_char_string_packed_right(self) -> None:
        value, err = self.c.convert("'AB'")
        self.assertEqual(value, '0x00004142')
        self.assertEqual(err, '')

    def test_four_char_string_fills_word(self) -> None:
        value, err = self.c.convert("'ABCD'")
        self.assertEqual(value, '0x41424344')
        self.assertEqual(err, '')

    def test_string_too_long_returns_none(self) -> None:
        value, err = self.c.convert("'ABCDE'")
        self.assertIsNone(value)
        self.assertTrue(len(err) > 0)


class TestInputToHexBits(unittest.TestCase):
    """Test with non-default bit widths."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication(sys.argv)
        cls.c = InputToHex()

    def test_8bit_max(self) -> None:
        value, err = self.c.convert('255', bits=8)
        self.assertEqual(value, '0xFF')
        self.assertEqual(err, '')

    def test_8bit_negative_one(self) -> None:
        value, err = self.c.convert('-1', bits=8)
        self.assertEqual(value, '0xFF')
        self.assertEqual(err, '')

    def test_8bit_too_large(self) -> None:
        value, err = self.c.convert('256', bits=8)
        self.assertIsNone(value)
        self.assertTrue(len(err) > 0)

    def test_16bit_max(self) -> None:
        value, err = self.c.convert('65535', bits=16)
        self.assertEqual(value, '0xFFFF')
        self.assertEqual(err, '')

    def test_16bit_negative_one(self) -> None:
        value, err = self.c.convert('-1', bits=16)
        self.assertEqual(value, '0xFFFF')
        self.assertEqual(err, '')


class TestDataTypesInvalidInput(unittest.TestCase):

    def test_wrong_hex_length_raises(self) -> None:
        with self.assertRaises(RuntimeError):
            DataTypes('0x000')  # 3 hex digits

    def test_one_hex_digit_raises(self) -> None:
        with self.assertRaises(RuntimeError):
            DataTypes('0xF')

    def test_six_hex_digits_raises(self) -> None:
        with self.assertRaises(RuntimeError):
            DataTypes('0x000041')


class TestDataTypesByte(unittest.TestCase):
    """Tests for 8-bit (2 hex digit) values."""

    def test_hexadecimal_preserved(self) -> None:
        self.assertEqual(DataTypes('0x41').hexadecimal, '0x41')

    def test_uint_positive(self) -> None:
        self.assertEqual(DataTypes('0x41').uint, 65)

    def test_int_positive(self) -> None:
        self.assertEqual(DataTypes('0x41').int, 65)

    def test_int_max_positive(self) -> None:
        # 0x7F = 127, which is MAX_POSITIVE[2]
        self.assertEqual(DataTypes('0x7F').int, 127)

    def test_int_min_negative(self) -> None:
        # 0x80 = 128 > MAX_POSITIVE[2]=127 → int = 128 - 256 = -128
        self.assertEqual(DataTypes('0x80').int, -128)

    def test_int_negative_one(self) -> None:
        # 0xFF = 255 → 255 - 256 = -1
        self.assertEqual(DataTypes('0xFF').int, -1)

    def test_binary_format(self) -> None:
        self.assertEqual(DataTypes('0x0F').binary, '0b00001111')

    def test_binary_all_ones(self) -> None:
        self.assertEqual(DataTypes('0xFF').binary, '0b11111111')

    def test_ascii_printable(self) -> None:
        self.assertEqual(DataTypes('0x41').ascii, 'A')

    def test_ascii_non_printable(self) -> None:
        self.assertEqual(DataTypes('0x00').ascii, '·')

    def test_utf8_printable(self) -> None:
        self.assertEqual(DataTypes('0x41').utf8, 'A')

    def test_utf32_printable(self) -> None:
        self.assertEqual(DataTypes('0x41').utf32, 'A')

    def test_utf32_non_printable(self) -> None:
        self.assertEqual(DataTypes('0x00').utf32, '·')


class TestDataTypesHalfword(unittest.TestCase):
    """Tests for 16-bit (4 hex digit) values."""

    def test_uint(self) -> None:
        self.assertEqual(DataTypes('0x0041').uint, 65)

    def test_int_positive(self) -> None:
        self.assertEqual(DataTypes('0x0041').int, 65)

    def test_int_max_positive(self) -> None:
        # 0x7FFF = 32767 = MAX_POSITIVE[4]
        self.assertEqual(DataTypes('0x7FFF').int, 32767)

    def test_int_min_negative(self) -> None:
        # 0x8000 = 32768 > 32767 → 32768 - 65536 = -32768
        self.assertEqual(DataTypes('0x8000').int, -32768)

    def test_int_negative_one(self) -> None:
        self.assertEqual(DataTypes('0xFFFF').int, -1)

    def test_binary_format(self) -> None:
        self.assertEqual(DataTypes('0x000F').binary, '0b0000000000001111')


class TestDataTypesWord(unittest.TestCase):
    """Tests for 32-bit (8 hex digit) values."""

    def test_uint(self) -> None:
        self.assertEqual(DataTypes('0x00000041').uint, 65)

    def test_int_positive(self) -> None:
        self.assertEqual(DataTypes('0x00000041').int, 65)

    def test_int_max_positive(self) -> None:
        # 0x7FFFFFFF = 2147483647 = MAX_POSITIVE[8]
        self.assertEqual(DataTypes('0x7FFFFFFF').int, 2147483647)

    def test_int_min_negative(self) -> None:
        # 0x80000000 = 2147483648 → 2147483648 - 4294967296 = -2147483648
        self.assertEqual(DataTypes('0x80000000').int, -2147483648)

    def test_int_negative_one(self) -> None:
        self.assertEqual(DataTypes('0xFFFFFFFF').int, -1)

    def test_binary_format(self) -> None:
        self.assertEqual(DataTypes('0x0000000F').binary, '0b00000000000000000000000000001111')

    def test_utf8_ascii_char(self) -> None:
        self.assertEqual(DataTypes('0x00000041').utf8, 'A')

    def test_utf32_ascii_char(self) -> None:
        self.assertEqual(DataTypes('0x00000041').utf32, 'A')

    def test_utf32_non_printable(self) -> None:
        self.assertEqual(DataTypes('0x00000000').utf32, '·')


if __name__ == '__main__':
    unittest.main()
