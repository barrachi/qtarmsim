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

import math
from PySide6 import QtCore


class InputToHex(QtCore.QObject):
    """
    Class that handles the conversion between a user input value and a
    hexadecimal representation of that input.
    """

    def html_error(self, err_msg: str) -> str:
        return self.tr("""
        <p>{0}</p>
        <p>Allowed inputs are:</p>
        <ul>
          <li>A number either on decimal, hexadecimal, binary or octal. The
          prefixes '0x', '0b', and '0o' should be used to indicate hexadecimal,
          binary and octal, respectively.</li>
          </li>
          <li>A string enclosed either on '' or on "". The string will be encoded
          using UTF-8.</li>
        </ul>
        """).format(err_msg)

    def convert(self, text: str | object, bits: int = 32) -> tuple[str | None, str]:
        """
        Converts the given text to a hexadecimal value with 8 digits.

        The following kinds of conversion are supported:

         - From a number in base 10, 16, 2, or 8. The number must be between
            [-MAX_NEG, +MAX_POS].

         - From an UTF8 string using the format '[:alnum:]*' or "[:alnum:]*".

        @param text: a string representing the chars or the number to be represented
        @param bits: number of bits allowed

        @return: a pair (hex_value, err_msg) hex_value is a string with the
                                             hexadecimal value if everything went
                                             OK, or None otherwise, err_msg provides
                                             an error message in case something went
                                             wrong
        """
        MAX_NEG = -1 << bits - 1
        MAX_POS = (1 << bits) - 1
        HEX_DIGITS = int(math.ceil(bits / 4))
        BYTES = int(HEX_DIGITS / 2)
        if type(text) is not str:
            err_msg = self.tr("Input value '{}' was not an string").format(text)
            return None, self.html_error(err_msg)
        if len(text) == 0:
            return None, ''
        if len(text) >= 2:
            # If starts and ends with quote or double quote, try to decode it as a string
            if (text[0] == "'" and text[-1] == "'") or (text[0] == '"' and text[-1] == '"'):
                if len(text) == 2:
                    # Empty string, return 0
                    return '0x' + '0' * HEX_DIGITS, ''
                # Non-empty string, convert to bytes, left padding with zeros
                bytes_list = ["{:02X}".format(b) for b in bytes(text[1:-1], 'utf-8')]
                if len(bytes_list) > bits / 8:
                    err_msg = self.tr("The UTF-8 string '{}' can not been represented with {} bits.").format(text, bits)
                    return None, self.html_error(err_msg)
                bytes_list = ["00"] * BYTES + bytes_list
                return "0x{}".format("".join(bytes_list[-BYTES:])), ''
        try:
            num = int(text, base=0)
        except ValueError:
            err_msg = self.tr("No conversion found for input '{}'.").format(text)
            return None, self.html_error(err_msg)
        if num < MAX_NEG:
            err_msg = self.tr(
                "Input '{}' is lower than the maximum negative value that can be represented with {} bits.").format(
                text, bits)
            return None, self.html_error(err_msg)
        if num > MAX_POS:
            err_msg = self.tr(
                "Input '{}' is greater than the maximum positive value that can be represented with {} bits.").format(
                text, bits)
            return None, self.html_error(err_msg)
        if num < 0:
            # Make complement to two
            num = MAX_POS + num + 1
        return "0x{:0{}X}".format(num, HEX_DIGITS), ''


class DataTypes:

    MAX_POSITIVE: tuple[int, int, int, int, int, int, int, int, int] = (0, 0, 127, 0, 32767, 0, 0, 0, 2147483647)
    CA2_VALUE: tuple[int, int, int, int, int, int, int, int, int] = (0, 0, 256, 0, 65536, 0, 0, 0, 4294967296)

    def __init__(self, hex_value: str) -> None:
        self.hexadecimal: str = hex_value
        hex_digits: int = len(self.hexadecimal) - 2 # - "0x"
        if hex_digits not in (2, 4, 8):
            raise RuntimeError("DataTypes class received an hexadecimal value of a length not supported")
        # Unsigned integer
        self.uint: int = int(self.hexadecimal, 16)
        # Integer
        self.int: int = self.uint if self.uint <= self.MAX_POSITIVE[hex_digits] else self.uint - self.CA2_VALUE[hex_digits]
        # binary
        if hex_digits == 2:
            self.binary: str = "{:08b}".format(self.uint)
        elif hex_digits == 4:
            self.binary = "{:016b}".format(self.uint)
        else:
            self.binary = "{:032b}".format(self.uint)
        self.binary = '0b' + self.binary
        # ASCII
        try:
            self.ascii: str = self.uint.to_bytes(1, "big").decode("ascii", "replace")
        except OverflowError:
            self.ascii = "<small>Out of range</small>"
        if not self.ascii.isprintable():
            self.ascii = '·'
        # UTF-8
        try:
            utf8_bytes = self.uint.to_bytes(4, "big").lstrip(b'\x00')
        except ValueError:
            self.utf8 = "<small>Not UTF-8</small>"
        except OverflowError:
            self.utf8 = "<small>Out of range</small>"
        else:
            if len(utf8_bytes) == 0:
                utf8_bytes = b'\x00'
            self.utf8: str = utf8_bytes.decode("utf-8", "replace")
            if len(self.utf8) != 1:
                self.utf8 = "<small>Not a UTF-8 char</small>"
        if not self.utf8.isprintable():
            self.utf8 = '·'
        # UTF-32
        try:
            self.utf32: str = chr(self.uint)
        except ValueError:
            self.utf32 = "<small>Not a UTF-32 char</small>"
        except OverflowError:
            self.utf32 = "<small>Out of range</small>"
        if not self.utf32.isprintable():
            self.utf32 = '·'
