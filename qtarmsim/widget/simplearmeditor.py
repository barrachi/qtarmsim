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
    ARROW_MARKER_NUM = 8

    def __init__(self, parent=None, disassemble=False):
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
        self.setMarginsBackgroundColor(QColor("#bbbbbb"))

        if disassemble:
            self.setReadOnly(True)
            self.setCaretWidth(0)
            self.setBraceMatching(QsciScintilla.NoBraceMatch)
            self.setMarginType(1, QsciScintilla.SymbolMargin)
            self.setMarginSensitivity(1, True)
            # Clickable margin configuration
            self.connect(self, SIGNAL('marginClicked(int, int, Qt::KeyboardModifiers)'), self.on_margin_clicked)
            self.markerDefine(QsciScintilla.CircledPlus, self.ARROW_MARKER_NUM)
            self.setMarkerForegroundColor(QColor("#dd0000"), self.ARROW_MARKER_NUM)
            self.setMarkerBackgroundColor(QColor("#cccccc"), self.ARROW_MARKER_NUM)
        else:
            self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
            self.setMarginType(0, QsciScintilla.NumberMargin)
            self.setMarginWidth(0, QFontMetrics(font).width("0000") + 6)
            self.setMarginWidth(1, 0)
            # Don't want to see the horizontal scrollbar at all
            self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)
        
        # Set encoding as UTF-8
        self.setUtf8(True)
        
        # Current line visible with special background color
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#e4e4ff"))

        # Set lexer
        lexer = QsciLexerARM(self)
        lexer.setDefaultFont(font)
        self.setLexer(lexer)


        # Not too small
        # self.setMinimumSize(400, 300)

    
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
