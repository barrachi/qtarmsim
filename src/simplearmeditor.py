# -*- coding: utf-8 -*-

#===============================================================================
# References:
#   Sample using QScintilla with PyQt
#   http://eli.thegreenplace.net/2011/04/01/sample-using-qscintilla-with-pyqt/
#===============================================================================

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qsci import QsciScintilla, QsciLexerPython
from .qscilexerarm import QsciLexerARM

class SimpleARMEditor(QsciScintilla):
    ARROW_MARKER_NUM = 8

    def __init__(self, parent=None):
        super(SimpleARMEditor, self).__init__(parent)

        # Set the coding to utf8
        self.setUtf8(True)
        
        # Set the default font
        font = QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.setFont(font)
        self.setMarginsFont(font)

        # Margin 0 is used for line numbers
        fontmetrics = QFontMetrics(font)
        self.setMarginsFont(font)
        self.setMarginWidth(0, fontmetrics.width("000") + 6)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor("#cccccc"))

        # Clickable margin 1 for showing markers
        self.setMarginSensitivity(1, True)
        self.connect(self, SIGNAL('marginClicked(int, int, Qt::KeyboardModifiers)'), self.on_margin_clicked)
        self.markerDefine(QsciScintilla.CircledPlus, self.ARROW_MARKER_NUM)
        self.setMarkerForegroundColor(QColor("#dd0000"), self.ARROW_MARKER_NUM)
        self.setMarkerBackgroundColor(QColor("#cccccc"), self.ARROW_MARKER_NUM)

        # Brace matching: enable for a brace immediately before or after the current position
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        # Current line visible with special background color
        self.setCaretLineVisible(True)
        #self.setCaretLineBackgroundColor(QColor("#ffe4e4"))
        self.setCaretLineBackgroundColor(QColor("#e4e4ff"))

        # Set lexer
        lexer = QsciLexerARM(self)
        lexer.setDefaultFont(font)
        self.setLexer(lexer)

        #self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, 1, font.family())

        # Don't want to see the horizontal scrollbar at all
        # Use raw message to Scintilla here (all messages are documented here: http://www.scintilla.org/ScintillaDoc.html)
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)

        # Not too small
        self.setMinimumSize(600, 450)

    
    def on_margin_clicked(self, nmargin, nline, modifiers):
        # Toggle marker for the line the margin was clicked on
        if self.markersAtLine(nline) != 0:
            self.markerDelete(nline, self.ARROW_MARKER_NUM)
        else:
            self.markerAdd(nline, self.ARROW_MARKER_NUM)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = SimpleARMEditor()
    editor.show()
    editor.setText(open("hello_world.asm").read())
    app.exec_()
