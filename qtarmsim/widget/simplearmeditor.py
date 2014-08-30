# -*- coding: utf-8 -*-

#===============================================================================
# References:
#   Sample using QScintilla with PyQt
#   http://eli.thegreenplace.net/2011/04/01/sample-using-qscintilla-with-pyqt/
#===============================================================================

import sys

from PyQt4 import QtCore, QtGui
from PyQt4.Qsci import QsciScintilla

from .qscilexerarm import QsciLexerARM


class SimpleARMEditor(QsciScintilla):

    # breakpoint_changed signal, parameters are if set or unset (True/False) and hex_address
    breakpoint_changed = QtCore.pyqtSignal(int, 'QString')

    # Markers
    BREAKPOINT_MARKER = QsciScintilla.Circle
    PC_MARKER1 = QsciScintilla.RightArrow
    PC_MARKER2 = QsciScintilla.Background
    
    def __init__(self, parent=None, disassemble=False):
        super(SimpleARMEditor, self).__init__(parent)

        # Set the default font
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.setFont(font)
        self.setMarginsFont(font)
        self.setMarginsBackgroundColor(QtGui.QColor("#CCCCCC"))

        # Marker related variables
        self.breakpoints = {}
        self.last_highlighted_line = 0

        if disassemble:
            self.setReadOnly(True)
            # No cursor
            self.setCaretWidth(0)
            # Brace matching kind
            self.setBraceMatching(QsciScintilla.NoBraceMatch)
            # Margin on disassembler
            self.setMarginType(1, QsciScintilla.SymbolMargin)
            self.setMarginSensitivity(1, True)
            # Clickable margin configuration
            self.connect(self, QtCore.SIGNAL('marginClicked(int, int, Qt::KeyboardModifiers)'), self.on_margin_clicked)
            # Breakpoint marker (white circle filled with red)
            self.markerDefine(self.BREAKPOINT_MARKER, self.BREAKPOINT_MARKER)
            self.setMarkerForegroundColor(QtGui.QColor("#DDDDDD"), self.BREAKPOINT_MARKER)
            self.setMarkerBackgroundColor(QtGui.QColor("#DD5555"), self.BREAKPOINT_MARKER)
            # PC Marker 1 (white right arrow filled with light blue)
            self.markerDefine(self.PC_MARKER1, self.PC_MARKER1)
            self.setMarkerForegroundColor(QtGui.QColor("#000000"), self.PC_MARKER1)
            self.setMarkerBackgroundColor(QtGui.QColor("#E4E4FF"), self.PC_MARKER1)
            # PC Marker 2 (line background with light blue)
            self.markerDefine(self.PC_MARKER2, self.PC_MARKER2)
            self.setMarkerForegroundColor(QtGui.QColor("#FFFFFF"), self.PC_MARKER2) # Not used
            self.setMarkerBackgroundColor(QtGui.QColor("#E4E4FF"), self.PC_MARKER2)
        else:
            # Brace matching kind
            self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
            # Margin on editor
            self.setMarginType(0, QsciScintilla.NumberMargin)
            self.setMarginWidth(0, QtGui.QFontMetrics(font).width("0000") + 6)
            self.setMarginWidth(1, 0)
            # Current line visible with special background color
            self.setCaretLineVisible(True)
            self.setCaretLineBackgroundColor(QtGui.QColor("#e4e4ff"))
            # Don't want to see the horizontal scrollbar at all
            self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)
        
        # Set encoding as UTF-8
        self.setUtf8(True)

        # Set lexer
        lexer = QsciLexerARM(self)
        lexer.setDefaultFont(font)
        self.setLexer(lexer)

        # Not too small
        # self.setMinimumSize(400, 300)

    def on_margin_clicked(self, nmargin, nline, modifiers):
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
        for nline in self.breakpoints.keys():
            self.markerAdd(nline, self.BREAKPOINT_MARKER)

    def clearBreakpoints(self):
        for nline in self.breakpoints.keys():
            self.markerDelete(nline, self.BREAKPOINT_MARKER)
        self.breakpoints.clear()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    editor = SimpleARMEditor()
    editor.show()
    editor.setText(open("hello_world.asm").read())
    app.exec_()
