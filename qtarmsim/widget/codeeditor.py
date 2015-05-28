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
#   http://doc.qt.io/qt-5/qtwidgets-widgets-codeeditor-example.html
#   http://doc.qt.io/qt-4.8/qplaintextedit.html
#   http://doc.qt.io/qt-4.8/qtextdocument.html
#   http://doc.qt.io/qt-4.8/qtextcursor.html
#===============================================================================


import sys
import re

from PySide import QtCore, QtGui


class LeftArea(QtGui.QWidget):
    """
    LeftArea widget.

    Its functionality depends on the read only property of the associated code editor. If it is read only, it will mark the current highlighted line number with a blue left arrow, and the lines where there are breakpoints, with a stop sign. It will also accept left click mouse events to ser or unset breakpoints.

    On the other hand, if the associated editor is not read only, it will show the line number of each line of the code editor source.
    """


    def __init__(self, codeEditor):
        "Asociates this LeftArea instance with its CodeEditor parent"
        super(LeftArea, self).__init__(codeEditor)
        self.codeEditor = codeEditor
        self.clearBreakpoints()
    
    def sizeHint(self):
        "Returns the size hint of this widget"
        return QtCore.QSize(self.codeEditor.width(), 0)
    
    def paintEvent(self, event):
        "Repaints (part of) the LeftArea Widget"
        super(LeftArea, self).paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.fillRect(event.rect(), QtGui.QColor('lightGray'))
        block = self.codeEditor.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.codeEditor.blockBoundingGeometry(block).translated(self.codeEditor.contentOffset()).top()
        height = self.codeEditor.blockBoundingRect(block).height()
        bottom = top + height
        if self.codeEditor.isReadOnly():
            width = self.width()
            height = bottom - top
            # A left arrow
            xa = 0.1 * width; xb = 0.4 * width; xc = 0.9 * width
            ya = 0.1 * height; yb = 0.25 * height; yc = 0.5 * height; yd = 0.75 * height; ye = 0.9 * height
            leftArrowPoints = [(xa, yb), (xa, yd), (xb, yd), (xb, ye), (xc, yc), (xb, ya), (xb, yb)]
            # A stop sign
            length = min(width, height) - 0.2 * min(width, height)
            xa = 0.0; xb = length / 4.0; xc = 3 * length / 4.0; xd = length
            ya = 0.0; yb = length / 4.0; yc = 3 * length / 4.0; yd = length
            stopPoints = [(xa, yb), (xa, yc), (xb, yd), (xc, yd), (xd, yc), (xd, yb), (xc, ya), (xb, ya)]
            xOffset = (width - length) / 2
            yOffset = (height - length) / 2
            stopPoints = [(x + xOffset, y + yOffset) for (x, y) in stopPoints]
            while (block.isValid() and top <= event.rect().bottom()):
                if (block.isVisible() and bottom >= event.rect().top()):
                    if blockNumber == self.codeEditor.getCurrentHightlightedLineNumber():
                        painter.setBrush(QtGui.QBrush(QtGui.QColor('blue').lighter(190)))
                        painter.setPen(QtGui.QColor('blue'))
                        arrowQPointsWithOffset = [QtCore.QPointF(x, top + y) for (x, y) in leftArrowPoints]
                        painter.drawPolygon(arrowQPointsWithOffset)
                    if blockNumber in self.breakpoints:
                        stopColor = QtGui.QColor('darkRed').lighter(170)
                        stopColor.setAlpha(100)
                        painter.setBrush(QtGui.QBrush(stopColor))
                        painter.setPen(QtGui.QColor('black'))
                        stopQPointsWithOffset = [QtCore.QPointF(x, top + y) for (x, y) in stopPoints]
                        painter.drawPolygon(stopQPointsWithOffset)
                block = block.next()
                top = bottom
                bottom = top + self.codeEditor.blockBoundingRect(block).height()
                blockNumber += 1
        else:
            while (block.isValid() and top <= event.rect().bottom()):
                if (block.isVisible() and bottom >= event.rect().top()):
                    number = blockNumber + 1
                    painter.setPen(QtGui.QColor('black'))
                    painter.drawText(0, top, self.width(), self.codeEditor.fontMetrics().height(), QtCore.Qt.AlignRight, u"{}".format(number))
                block = block.next()
                top = bottom
                bottom = top + self.codeEditor.blockBoundingRect(block).height()
                blockNumber += 1

    def width(self):
        "Returns the leftArea width based on the number of blocks in the associated editor and the width of the used font"
        if self.codeEditor.isReadOnly():
            width = 5 + self.codeEditor.fontMetrics().width(u"9") * 2
        else:
            digits = 1
            maxLines = max(1, self.codeEditor.blockCount())
            while (maxLines >= 10):
                maxLines /= 10
                digits += 1
            digits = max(2, digits)
            width = 5 + self.codeEditor.fontMetrics().width(u"9") * digits
        return width

    def wheelEvent(self, event):
        "Process the wheel event calling the wheel event on the parent"
        self.codeEditor.wheelEvent(event)

    def mousePressEvent(self, event):
        "Process the mouse press events: if the associated code editor is read only and the left button is clicked, find which line in the source code has been clicked on."
        if self.codeEditor.isReadOnly() and event.button() == QtCore.Qt.LeftButton:
            y = event.posF().y()
            block = self.codeEditor.firstVisibleBlock()
            bottom = self.codeEditor.blockBoundingGeometry(block).translated(self.codeEditor.contentOffset()).bottom()
            height = self.codeEditor.blockBoundingRect(block).height()
            while block.isValid() and bottom < y:
                block = block.next()
                bottom += height
            if block.isValid() and block.text().strip() != "":
                self.setOrClearBreakpoint(block.blockNumber(), block.text())
                self.repaint()
        else:
            super(LeftArea, self).mousePressEvent(event)

    def clearBreakpoints(self):
        try:
            self.breakpoints.clear()
        except AttributeError:
            self.breakpoints = {}

    def setOrClearBreakpoint(self, lineNumber, text):
        if lineNumber in self.breakpoints:
            self.breakpoints.pop(lineNumber)
            self.codeEditor.clearBreakpointSignal.emit(lineNumber, text)
        else:
            self.breakpoints[lineNumber] = text
            self.codeEditor.setBreakpointSignal.emit(lineNumber, text)



class CodeEditor(QtGui.QPlainTextEdit):
    "CodeEditor is a simple code editor that is able to use a syntax highlighter and provides a left line number area."
    
    setBreakpointSignal = QtCore.Signal('int', 'QString')
    clearBreakpointSignal = QtCore.Signal('int', 'QString')

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
        # Add leftArea child
        self.leftArea = LeftArea(self)
        self.updateLeftAreaWidth(0)
        # Set syntax highlighter
        if SyntaxHighlighterClass != None:
            self.syntaxHighlighter = SyntaxHighlighterClass(self.document())
        # Set extra highligth selections (current line and special keywords)
        self.setCurrentHighlightedLineNumber(0)
        self.updateHighlightSelections()
        # Connect signals
        self.connect(self, QtCore.SIGNAL('blockCountChanged(int)'), self.updateLeftAreaWidth)
        self.connect(self, QtCore.SIGNAL('updateRequest(QRect, int)'), self.updateLeftArea)
        self.connect(self, QtCore.SIGNAL('cursorPositionChanged()'), self.updateHighlightSelections)

    def setReadOnly(self, ro):
        """
        Sets the read only property to True or False.
        
        @param ro: The value to be set.
        """
        if ro:
            self.updateLeftAreaWidth()
        return super(CodeEditor, self).setReadOnly(ro)
    
    def clearBreakpoints(self):
        "Calls leftArea clearBreakpoints method"
        self.leftArea.clearBreakpoints()

    def setCurrentHighlightedLineNumber(self, lineNumber):
        """
        Sets the stored currentHighlightedLineNumber variable.

        @param lineNumber: the line number to be set.
        """
        self.currentHighlightedLineNumber = lineNumber
        self.updateHighlightSelections()

    def getCurrentHightlightedLineNumber(self):
        """
        Returns the current highlighted line number.

        The return value depends on whether the editor is read only of not.  If it is read only, it returns the stored currentHighlightedLineNumber. Otherwise, it returns the line number where the current cursor is.
        """
        if self.isReadOnly():
            return self.currentHighlightedLineNumber
        else:
            return self.textCursor().blockNumber()

    def _getCurrentHightlightedLineCursor(self):
        """
        Returns a cursor to the current highlighted line.
        
        The return value depends on whether the editor is read only of not.  If it is read only, it returns a cursor on the stored currentHighlightedLineNumber line. Otherwise, it returns the current cursor. 
        """
        cursor = self.textCursor()
        if self.isReadOnly():
            cursorBlockNumber = cursor.blockNumber()
            if cursorBlockNumber > self.currentHighlightedLineNumber:
                cursor.movePosition(QtGui.QTextCursor.Up, QtGui.QTextCursor.MoveAnchor, cursorBlockNumber - self.currentHighlightedLineNumber)
            else:
                cursor.movePosition(QtGui.QTextCursor.Down, QtGui.QTextCursor.MoveAnchor, self.currentHighlightedLineNumber - cursorBlockNumber)
        return cursor

    def resizeEvent(self, *args, **kwargs):
        "Resizes the leftArea child widget when a resize event is triggered"
        super(CodeEditor, self).resizeEvent(*args, **kwargs)
        cr = self.contentsRect()
        self.leftArea.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.leftArea.width(), cr.height()))

    def updateLeftAreaWidth(self, newBlockCount=None):
        "Changes code editor left margin based on the width of the leftArea child widget"
        self.setViewportMargins(self.leftArea.width(), 0, 0, 0);

    def updateLeftArea(self, rect, dy):
        "Updates the leftArea child widgets when an updateRequest event is triggered"
        if dy:
            self.leftArea.scroll(0, dy);
        else:
            self.leftArea.update(0, rect.y(), self.leftArea.width(), rect.height());
        if rect.contains(self.viewport().rect()):
            self.updateLeftAreaWidth()

    def updateHighlightSelections(self):
        "Sets the selections to be highlighted"
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
        selection.cursor = self._getCurrentHightlightedLineCursor()
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
                if not hcursor.isNull():  # and hcursor.blockNumber() != currentLine:
                    selection = QtGui.QTextEdit.ExtraSelection()
                    selection.format.setBackground(lineColor)
                    selection.cursor = hcursor
                    selections.append(selection)
        return selections
        
    def _getKeywordsToHighlight(self):
        "Returns a list of keywords that should be highlighted when that keyword is under the cursor"
        return []


    def wheelEvent(self, event):
        "Process the wheel event: zooms in and out whenever a CTRL+wheel event is triggered"
        if event.modifiers() == QtCore.Qt.ControlModifier:
            self.myFontPointSize += event.delta() / 120
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
