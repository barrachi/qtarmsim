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


import sys
import re

from PySide import QtCore, QtGui


# LineNumberArea based on:
#   http://doc.qt.io/qt-5/qtwidgets-widgets-codeeditor-example.html
#
class LineNumberArea(QtGui.QWidget):
    "LineNumberArea widget"

    def __init__(self, codeEditor):
        "Asociates this LineNumberArea instance with its CodeEditor parent"
        super(LineNumberArea, self).__init__(codeEditor)
        self.codeEditor = codeEditor
    
    def sizeHint(self):
        "Returns the size hint of this widget"
        return QtCore.QSize(self.codeEditor.lineNumberAreaWidth(), 0)
    
    def paintEvent(self, event):
        "Repaints (part of) the LineNumberArea Widget"
        super(LineNumberArea, self).paintEvent(event)
        return self.codeEditor.lineNumberAreaPaintEvent(event)


#
# CodeEditor based on:
#   http://doc.qt.io/qt-5/qtwidgets-widgets-codeeditor-example.html
#
class CodeEditor(QtGui.QPlainTextEdit):
    "CodeEditor is a simple code editor that is able to use a syntax highlighter and provides a left line number area"
    
    def __init__(self, parent=None, SyntaxHighlighterClass=None, *args, **kwargs):
        "CodeEditor initialization"
        super(CodeEditor, self).__init__(parent, *args, **kwargs)
        # Set the default font and tab width
        self.myFont = QtGui.QFont()
        self.myFontPointSize = 10
        self.myFont.setFamily('Courier')
        self.myFont.setStyleHint(QtGui.QFont.Monospace)
        self.myFont.setPointSize(self.myFontPointSize)
        self.setFont(self.myFont)
        self.setTabStopWidth(8 * self.fontMetrics().width('9'));
        # Disable wrap mode
        self.setLineWrapMode(self.NoWrap)
        # Add lineNumberArea
        self.lineNumberArea = LineNumberArea(self)
        self.updateLineNumberAreaWidth(0)
        # Set syntax highlighter
        if SyntaxHighlighterClass != None:
            self.syntaxHighlighter = SyntaxHighlighterClass(self.document())
        # Set extra highligth selections (current line and special keywords)
        self.setHighlightSelections()
        # Connect signals
        self.connect(self, QtCore.SIGNAL('blockCountChanged(int)'), self.updateLineNumberAreaWidth)
        self.connect(self, QtCore.SIGNAL('updateRequest(QRect, int)'), self.updateLineNumberArea)
        self.connect(self, QtCore.SIGNAL('cursorPositionChanged()'), self.setHighlightSelections)
        
        #@todelete:
        #self.setGeometry(QtCore.QRect(200, 200, 600, 400))

    def lineNumberAreaWidth(self):
        "Returns the lineNumberArea width based on the number of rows and the width of the used font"
        digits = 1
        maxLines = max(1, self.blockCount())
        while (maxLines >= 10):
            maxLines /= 10
            digits += 1
        width = 5 + self.fontMetrics().width(u"9") * digits
        return width
    
    def resizeEvent(self, *args, **kwargs):
        "Resizes the lineNumberArea child widget when a resize event is triggered"
        super(CodeEditor, self).resizeEvent(*args, **kwargs)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def updateLineNumberAreaWidth(self, newBlockCount):
        "Changes code editor left margin based on the width of the child lineNumberArea widget"
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0);

    def updateLineNumberArea(self, rect, dy):
        "Updates the child lineNumberArea widget when an updateRequest event is triggered"
        if dy:
            self.lineNumberArea.scroll(0, dy);
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberAreaWidth(), rect.height());
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def setHighlightSelections(self):
        "Sets the selections that have to be highlighted"
        extraSelections = []
        extraSelections.append(self._getCurrentLineHighlightSelection())
        extraSelections += self._getCurrentWordHighlightSelections()
        self.setExtraSelections(extraSelections)
        
    def _getCurrentLineHighlightSelection(self):
        "Returns the current line highlight selection"
        lineColor = QtGui.QColor('blue').lighter(190)
        selection = QtGui.QTextEdit.ExtraSelection()
        selection.format.setBackground(lineColor)
        selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        return selection
    
    def _getCurrentWordHighlightSelections(self):
        "Returns highlight selections for those word in the document that match the current word under the cursor (only if the current word is a special keyword)"
        words = self._getKeywordsToHighlight()
        cursor = self.textCursor()
        currentLine = cursor.blockNumber()
        cursor.select(QtGui.QTextCursor.WordUnderCursor)
        currentWord = cursor.selectedText()
        lineColor = QtGui.QColor('yellow')
        selections = []
        if currentWord in words:
            hcursor = QtGui.QTextCursor(self.document())
            while not hcursor.isNull() and not hcursor.atEnd():
                hcursor = self.document().find(currentWord, hcursor, QtGui.QTextDocument.FindWholeWords)
                if not hcursor.isNull() and hcursor.blockNumber() != currentLine:
                    selection = QtGui.QTextEdit.ExtraSelection()
                    selection.format.setBackground(lineColor)
                    selection.cursor = hcursor
                    selections.append(selection)
        return selections
        
    def _getKeywordsToHighlight(self):
        "Returns which keywords should be highlighted on the text when the same keyword is under the cursor"
        return []
    
#===============================================================================
#     def highlightCurrentLine(self):
#         "Highlights the current line"
#         extraSelections = []
#         lineColor = QtGui.QColor('blue').lighter(190)
#         selection = QtGui.QTextEdit.ExtraSelection()
#         selection.format.setBackground(lineColor)
#         selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
#         selection.cursor = self.textCursor()
#         selection.cursor.clearSelection()
#         extraSelections.append(selection)
#         self.setExtraSelections([selection,])
#         self.highlightRegisterUnderCursor()
# 
#     def highlightRegisterUnderCursor(self):
#         "If the text cursor is on a register, highlights other occurrences in the text of that register"
#         self.regpattern = re.compile('^r([0-9]|1[0-5])$')
#         self.previousSelectedRegister = None
# 
#         if self.previousSelectedRegister:
#             self._mergeCharFormat(self.previousSelectedRegister, QtGui.QColor('white'))
#             self.previousSelectedRegister == None
#         cursor = self.textCursor()
#         cursor.select(QtGui.QTextCursor.WordUnderCursor)
#         if not cursor.selectedText() or not self.regpattern.search(cursor.selectedText()):
#             return
#         register = cursor.selectedText()
#         self._mergeCharFormat(register, QtGui.QColor('yellow'))
#         self.previousSelectedRegister = register
# 
#     def _mergeCharFormat(self, register, color):
#         "Highlights all occurrences of the given text with the supplied color, except those in the current line."
#         currentLine = self.textCursor().block()
#         hcursor = QtGui.QTextCursor(self.document())
#         colorFormat = QtGui.QTextCharFormat(hcursor.charFormat())
#         colorFormat.setBackground(color)
#         while not hcursor.isNull() and not hcursor.atEnd():
#             hcursor = self.document().find(register, hcursor, QtGui.QTextDocument.FindWholeWords)
#             if not hcursor.isNull() and hcursor.block() != currentLine:
#                 hcursor.mergeCharFormat(colorFormat)
#===============================================================================
        

    def lineNumberAreaPaintEvent(self, event): # (QPaintEvent *event)
        painter = QtGui.QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QtGui.QColor('lightGray'))
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        while (block.isValid() and top <= event.rect().bottom()):
            if (block.isVisible() and bottom >= event.rect().top()):
                number = blockNumber + 1
                painter.setPen(QtGui.QColor('black'))
                painter.drawText(0, top, self.lineNumberArea.width(), self.fontMetrics().height(), QtCore.Qt.AlignRight, u"{}".format(number))
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber+=1

    def wheelEvent(self, event):
        if event.modifiers() == QtCore.Qt.ControlModifier:
            self.myFontPointSize += event.delta()/120 
            if self.myFontPointSize < 10:
               self.myFontPointSize = 10
            self.myFont.setPointSize(self.myFontPointSize)
            self.setFont(self.myFont)
            self.setTabStopWidth(8 * self.fontMetrics().width('9'));
        else:
            super(CodeEditor, self).wheelEvent(event)





if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    editor = CodeEditor()
    editor.setPlainText(open("../../examples/add.s").read())
    editor.setWindowTitle("Code Editor Example")
    editor.setGeometry(QtCore.QRect(200, 200, 600, 400))
    editor.show()
    sys.exit(app.exec_())
