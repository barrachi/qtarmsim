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
#   Sample using QScintilla with PyQt
#   http://eli.thegreenplace.net/2011/04/01/sample-using-qscintilla-with-pyqt/
#===============================================================================

import sys
import re

from PySide import QtCore, QtGui

#from PySide.Qsci import QTextEdit
#from .qscilexerarm import QsciLexerARM


class SimpleARMEditor(QtGui.QTextEdit):

    # breakpoint_changed signal, parameters are if set or unset (True/False) and hex_address
    # breakpoint_changed = QtCore.Signal(int, 'QString')

    # Markers
    #BREAKPOINT_MARKER = QtGui.QTextEdit.Circle
    #PC_MARKER1 = QtGui.QTextEdit.RightArrow
    #PC_MARKER2 = QtGui.QTextEdit.Background
    
    def __init__(self, parent=None, disassemble=False):
        super(SimpleARMEditor, self).__init__(parent)

        # Set the default font
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setStyleHint(QtGui.QFont.Monospace)
        font.setPointSize(10)
        #self.setFont(font)
        #self.setMarginsFont(font)
        #self.setMarginsBackgroundColor(QtGui.QColor("#CCCCCC"))

        # Marker related variables
        self.breakpoints = {}
        self.last_highlighted_line = 0

        if disassemble:
            self.setReadOnly(True)
            # No cursor
            #self.setCaretWidth(0)
            # Brace matching kind
            #self.setBraceMatching(QtGui.QTextEdit.NoBraceMatch)
            # Margin on disassembler
            #self.setMarginType(1, QtGui.QTextEdit.SymbolMargin)
            #self.setMarginSensitivity(1, True)
            # Clickable margin configuration
            #self.connect(self, QtCore.SIGNAL('marginClicked(int, int, Qt::KeyboardModifiers)'), self.on_margin_clicked)
            # Breakpoint marker (white circle filled with red)
            #self.markerDefine(self.BREAKPOINT_MARKER, self.BREAKPOINT_MARKER)
            #self.setMarkerForegroundColor(QtGui.QColor("#DDDDDD"), self.BREAKPOINT_MARKER)
            #self.setMarkerBackgroundColor(QtGui.QColor("#DD5555"), self.BREAKPOINT_MARKER)
            # PC Marker 1 (white right arrow filled with light blue)
            #self.markerDefine(self.PC_MARKER1, self.PC_MARKER1)
            #self.setMarkerForegroundColor(QtGui.QColor("#000000"), self.PC_MARKER1)
            #self.setMarkerBackgroundColor(QtGui.QColor("#E4E4FF"), self.PC_MARKER1)
            # PC Marker 2 (line background with light blue)
            #self.markerDefine(self.PC_MARKER2, self.PC_MARKER2)
            #self.setMarkerForegroundColor(QtGui.QColor("#FFFFFF"), self.PC_MARKER2) # Not used
            #self.setMarkerBackgroundColor(QtGui.QColor("#E4E4FF"), self.PC_MARKER2)
        else:
            # Brace matching kind
            #self.setBraceMatching(QtGui.QTextEdit.SloppyBraceMatch)
            # Margin on editor
            #self.setMarginType(0, QtGui.QTextEdit.NumberMargin)
            #self.setMarginWidth(0, QtGui.QFontMetrics(font).width("0000") + 6)
            #self.setMarginWidth(1, 0)
            # Current line visible with special background color
            #self.setCaretLineVisible(True)
            #self.setCaretLineBackgroundColor(QtGui.QColor("#e4e4ff"))
            # Don't want to see the horizontal scrollbar at all
            #self.SendScintilla(QtGui.QTextEdit.SCI_SETHSCROLLBAR, 0)
            pass
        
        # Set encoding as UTF-8
        #self.setUtf8(True)

        # Set lexer
        #lexer = QsciLexerARM(self)
        #lexer.setDefaultFont(font)
        #self.setLexer(lexer)

        # Not too small
        # self.setMinimumSize(400, 300)

    def on_margin_clicked(self, nmargin, nline, modifiers):
        return
        # Get hex address from nline
        hex_address = self.text(nline).split(" ")[0][1:-1]
        # Toggle marker for the line the margin was clicked on
        if self.breakpoints.get(nline):
            self.markerDelete(nline, self.BREAKPOINT_MARKER)
            self.breakpoints.pop(nline)
            self.breakpoint_changed.emit(False, hex_address)
        else:
            self.markerAdd(nline, self.BREAKPOINT_MARKER)
            self.breakpoints[nline] = True
            self.breakpoint_changed.emit(True, hex_address)

    def highlightPCLine(self, nline):
        return
        #self.setFocus()
        self.setCursorPosition(nline, 0)
        self.ensureLineVisible(nline)
        self.markerDelete(self.last_highlighted_line, self.PC_MARKER1)
        self.markerDelete(self.last_highlighted_line, self.PC_MARKER2)
        self.markerAdd(nline, self.PC_MARKER1)
        self.markerAdd(nline, self.PC_MARKER2)
        self.last_highlighted_line = nline

    def setText(self, text):
        super(SimpleARMEditor, self).setText(text)
        # Restore breakpoints
        #for nline in self.breakpoints.keys():
        #    self.markerAdd(nline, self.BREAKPOINT_MARKER)

    def clearBreakpoints(self):
        return
        for nline in self.breakpoints.keys():
            self.markerDelete(nline, self.BREAKPOINT_MARKER)
        self.breakpoints.clear()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    editor = CodeEditor(highlighterClass = ARMHighlighter)
    editor.appendPlainText(open("../../examples/add.s").read())
    editor.moveCursor(QtGui.QTextCursor.Start)
    editor.setWindowTitle("Code Editor Example");
    editor.show()
    sys.exit(app.exec_())
