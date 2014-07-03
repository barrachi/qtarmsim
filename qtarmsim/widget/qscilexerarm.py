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

#===============================================================================
# References:
#  uni-projekt / debugger / asmeditor.py
#  https://github.com/svenstaro/uni-projekt/blob/master/debugger/asmeditor.py
#===============================================================================

import re

from PyQt4.Qsci import QsciLexerCustom
from PyQt4.QtGui import QColor


class QsciLexerARM(QsciLexerCustom):

    def __init__(self, parent):
        super(QsciLexerARM, self).__init__(parent)
        self._styles = {
            0: 'Default',
            1: 'Comment',
            2: 'Instruction',
            3: 'Register',
            4: 'Immediate',
            5: 'Label',
            6: 'Data',
            7: 'Directive',
        }
        for key, value in self._styles.items():
            setattr(self, value, key)

    def language(self):
        return "ARM Assembler"

    def description(self, style):
        return self._styles.get(style, '')

    def defaultColor(self, style):
        if style == self.Default:
            return QColor('#000000')
        elif style == self.Comment:
            return QColor('#898887')
        elif style == self.Instruction:
            return QColor('#000000')
        elif style == self.Register:
            return QColor('#00C0C0')
        elif style == self.Immediate:
            return QColor('#00CC00')
        elif style == self.Label:
            return QColor('#006E28')
        elif style == self.Data:
            return QColor('#FEDCBA')
        elif style == self.Directive:
            return QColor('#FF8000')
        return super(QsciLexerARM, self).defaultColor(style)

    def defaultFont(self, style):
        font = super(QsciLexerARM, self).defaultFont(style)
        if style == self.Instruction:
            font.setBold(True)
        return font

    def defaultPaper(self, style):
        return QColor('#FFFFFF')

        
    def styleText(self, start, end):
        editor = self.editor()
        if editor is None:
            return

        # scintilla works with encoded bytes, not decoded characters.
        # this matters if the source contains non-ascii characters and
        # a multi-byte encoding is used (e.g. utf-8)
        source = ''
        if end >= editor.length():
            end = editor.length()-1
        if end > start:
            source = bytearray(end - start)
            editor.SendScintilla(editor.SCI_GETTEXTRANGE, start, end, source)
        if not source:
            return

        self.startStyling(start, 0x1f)

        for line in source.splitlines(False):
            length = len(line)
            
            # Search the beginning of a comment
            comment_marks=(b';', b'@', b'#if', b'#else', b'#end')
            try:
                commentStart = min([line.find(c) for c in comment_marks if line.find(c)!=-1])
            except ValueError:
                commentStart = -1
            
            # Process now the part of the line that is before the comment mark
            cmd = line if commentStart == -1 else line[:commentStart]

            # If there is part of the line unprocessed, check first if there is a label on it
            if cmd != '':
                # If there is a ':', then the first part of the line is marked as a label
                pos = cmd.find(b':')
                if pos != -1:
                    self.setStyling(pos+1, self.Label)
                    cmd = cmd[pos+1:]
            
            # If there is still a part of the line unprocessed, then process it
            firstWord = True
            while cmd != b'':
                searchWord = re.search(b'([^ ,]+)', cmd)
                if searchWord != None:
                    word = searchWord.groups()[0]
                    style = self.Default
                    if word.startswith(b'.'):
                        style = self.Directive
                        firstWord = False
                    elif firstWord:
                        style = self.Instruction
                        firstWord = False
                    elif word.startswith(b'r'):
                        style = self.Register
                    elif word.startswith(b'#'):
                        style = self.Immediate
                    startpos = searchWord.start()
                    endpos = searchWord.end()
                    if startpos != 0:
                        self.setStyling(startpos, self.Default)
                    self.setStyling(endpos-startpos, style)
                    cmd = cmd[endpos:]
                else:
                    # Consume the cmd string
                    self.setStyling(len(cmd), self.Default)
                    cmd = b''
                
            # Finally, set the style of the comment
            if commentStart != -1:
                self.setStyling(length - commentStart, self.Comment)

            # And the style of the newline character
            self.setStyling(1, self.Default)
