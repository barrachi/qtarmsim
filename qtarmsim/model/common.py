# -*- coding: utf-8 -*-

###########################################################################
#                                                                         #
#  This file is part of Qt ARMSim.                                        #
#                                                                         #
#  Qt ARMSim is free software: you can redistribute it and/or modify      #
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

from PyQt4.Qt import QObject

class InputToHex(QObject):
    """
    Class that handles the conversion between a user input value and an
    hexadecimal representation of that input.
    """
    
    MAX_NEG = -1 << 31
    MAX_POS = (1 << 32) -1


    def html_error(self, err_msg):
        return self.tr("""
        <p>{0}</p>
        <p>Allowed inputs are:</p>
        <ul>
          <li>A string enclosed either on '' or on "". It will be encoded as
          UTF-8. Only the first 4 bytes will be kept.</li>
          
          <li>A number either on decimal, hexadecimal, binary or octal. The
          prefixes '0x', '0b', and '0o' must be used to indicate hexadecimal,
          binary and octal, respectively.</li>
          </li>
        </ul>
        """).format(err_msg)

        
    def convert(self, text):
        """
        Converts the given text to an hexadecimal value with 8 digits.
        
        The following kinds of conversion are supported:
    
         - from a string using the format '[:alnum:]*' or "[:alnum:]*", only the
           first 4 bytes will be returned.
         
         - from a number in base 10, 16, 2, or 8. The number must be between
            [-MAX_NEG, +MAX_POS].
        
        @param text: a string representing the chars or the number to be represented
         
        @return: a pair (hex_value, err_msg) hex_value is an string with the
                                             hexadecimal value if everything went
                                             OK, or None otherwise, err_msg provides
                                             an error message in case something went
                                             wrong
        """
        if type(text) != str:
            err_msg = self.tr("Input value '{}' was not an string").format(text)
            return (None, self.html_error(err_msg))
        if len(text) == 0:
            return (None, '')
        if len(text) >= 2:
            # If starts and ends with ' or ", try to decode it as an string
            if (text[0] == "'" and text[-1] == "'") or (text[0] == '"' and text[-1] == '"'):
                if len(text) == 2:
                    # Empty string, return 0
                    return ('0x00000000', '')
                # Non empty string, convert to bytes, left padding with 0s and reverse (little-endian)
                bytes_list = ["{:02X}".format(b) for b in bytes(text[1:-1], 'utf-8')]
                bytes_list.reverse()
                bytes_list = ["00"]*3 + bytes_list 
                return ("0x{}".format("".join(bytes_list[-4:])), '')
        try:
            num = int(text, base=0)
        except ValueError:
            err_msg = self.tr("No conversion found for input '{}'.").format(text)
            return (None, self.html_error(err_msg))
        if num < self.MAX_NEG:
            err_msg = self.tr("Input '{}' is lower than the maximum negative value that can be represented with 32 bits.").format(text)
            return (None, self.html_error(err_msg))
        if num > self.MAX_POS:
            err_msg = self.tr("Input '{}' is greater than the maximum positive value that can be represented with 32 bits.").format(text)
            return (None, self.html_error(err_msg))
        if num < 0:
            # Make complement to two
            num = self.MAX_POS + num + 1
        return ("0x{:08X}".format(num), '')
        