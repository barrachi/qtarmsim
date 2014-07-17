# -*- coding: utf-8 -*-

#===============================================================================
# References:
#   Sample using QScintilla with PyQt
#   http://eli.thegreenplace.net/2011/04/01/sample-using-qscintilla-with-pyqt/
#===============================================================================

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qsci import QsciScintilla
from .qscilexerarm import QsciLexerARM

class SimpleARMEditor(QsciScintilla):
    BREAKPOINT_MARKER = QsciScintilla.Circle
    PC_MARKER1 = QsciScintilla.RightArrow
    PC_MARKER2 = QsciScintilla.Background
    
    def __init__(self, parent=None, disassemble=False):
        super(SimpleARMEditor, self).__init__(parent)

        # Set the default font
        font = QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.setFont(font)
        self.setMarginsFont(font)
        self.setMarginsBackgroundColor(QColor("#CCCCCC"))

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
            self.connect(self, SIGNAL('marginClicked(int, int, Qt::KeyboardModifiers)'), self.on_margin_clicked)
            # Breakpoint marker (white circle filled with red)
            self.markerDefine(self.BREAKPOINT_MARKER, self.BREAKPOINT_MARKER)
            self.setMarkerForegroundColor(QColor("#DDDDDD"), self.BREAKPOINT_MARKER)
            self.setMarkerBackgroundColor(QColor("#DD5555"), self.BREAKPOINT_MARKER)
            # PC Marker 1 (white right arrow filled with light blue)
            self.markerDefine(self.PC_MARKER1, self.PC_MARKER1)
            self.setMarkerForegroundColor(QColor("#000000"), self.PC_MARKER1)
            self.setMarkerBackgroundColor(QColor("#E4E4FF"), self.PC_MARKER1)
            # PC Marker 2 (line background with light blue)
            self.markerDefine(self.PC_MARKER2, self.PC_MARKER2)
            self.setMarkerForegroundColor(QColor("#FFFFFF"), self.PC_MARKER2) # Not used
            self.setMarkerBackgroundColor(QColor("#E4E4FF"), self.PC_MARKER2)
        else:
            # Brace matching kind
            self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
            # Margin on editor
            self.setMarginType(0, QsciScintilla.NumberMargin)
            self.setMarginWidth(0, QFontMetrics(font).width("0000") + 6)
            self.setMarginWidth(1, 0)
            # Current line visible with special background color
            self.setCaretLineVisible(True)
            self.setCaretLineBackgroundColor(QColor("#e4e4ff"))
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
        # Toggle marker for the line the margin was clicked on
        if self.breakpoints.get(nline):
            self.markerDelete(nline, self.BREAKPOINT_MARKER)
            self.breakpoints.pop(nline)
        else:
            self.markerAdd(nline, self.BREAKPOINT_MARKER)
            self.breakpoints[nline] = True

    def highlightPCLine(self, nline):
        #self.setFocus()
        self.setCursorPosition(nline, 0)
        self.ensureLineVisible(nline)
        self.markerDelete(self.last_highlighted_line, self.PC_MARKER1)
        self.markerDelete(self.last_highlighted_line, self.PC_MARKER2)
        self.markerAdd(nline, self.PC_MARKER1)
        self.markerAdd(nline, self.PC_MARKER2)
        self.last_highlighted_line = nline

    def setText(self, txt):
        super(SimpleARMEditor, self).setText(txt)
        # Restore breakpoints
        for nline in self.breakpoints.keys():
            self.markerAdd(nline, self.BREAKPOINT_MARKER)
            
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = SimpleARMEditor()
    editor.show()
    editor.setText(open("hello_world.asm").read())
    app.exec_()
