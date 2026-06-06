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

# =========================================================================
# References:
#   http://doc.qt.io/qt-5/qtwidgets-widgets-codeeditor-example.html
#   http://doc.qt.io/qt-4.8/qplaintextedit.html
#   http://doc.qt.io/qt-4.8/qtextdocument.html
#   http://doc.qt.io/qt-4.8/qtextcursor.html
# =========================================================================


import sys

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QContextMenuEvent, QKeyEvent, QWheelEvent
from typing import final, cast
from typing_extensions import override


from ..utils import getMonoSpacedFont

@final
class LeftArea(QtWidgets.QWidget):
    """
    LeftArea widget.

    Its functionality depends on the read-only property of the associated code editor. If it is read-only,
    it will mark the current highlighted line number with a blue-left arrow, and the lines where there are
    breakpoints, with a stop sign. It will also accept left click mouse events to set or unset breakpoints.

    On the other hand, if the associated editor is not read-only, it will show the line number of each line
    in the code editor source.
    """

    def __init__(self, codeEditor: 'CodeEditor') -> None:
        """Associates this LeftArea instance with its CodeEditor parent"""
        super(LeftArea, self).__init__(codeEditor)
        # ------------------------------------------------------------
        #  Instance attributes that will be properly initialized later
        # ------------------------------------------------------------
        self.breakpoints: dict[int, str] = {}
        self.linesWithBackground: dict[int, list[QtGui.QColor]] = {}
        self.previousHighlightedLineNumber: int = -1
        self.currentHighlightedLineNumber: int = -1
        self.currentBgColor:QtGui.QColor = QtGui.QColor('blue')
        self.bgColors: list[QtGui.QColor]
        self.previousBlockHeight: float = -1.0
        self.previousSelfWidth: float = -1.0
        self.rightArrowPoints: list[tuple[float,float]] = []
        self.stopPoints: list[tuple[float,float]] = []
        self.middlePointerPoints: list[tuple[float,float]] = []
        self.upPointerPoints: list[tuple[float,float]] = []
        self.downPointerPoints: list[tuple[float,float]] = []
        # ------------------------------------------------------------
        # Colors
        self.rightArrowColor = QtGui.QColor('blue')
        self.stopPenColor = QtGui.QColor('black')
        self.stopFillColor = QtGui.QColor('darkRed').lighter(170)
        self.stopFillColor.setAlpha(100)
        self.pointerColor = QtGui.QColor('red')
        self.pointerColor.setAlpha(100)
        # ------------------------------------------------------------
        self.codeEditor: CodeEditor = codeEditor
        self.clearBreakpoints()
        self.clearLinesWithBackground()

    @override
    def sizeHint(self) -> QtCore.QSize:
        """Returns the size hint of this widget"""
        return QtCore.QSize(self.codeEditor.width(), 0)

    def initializePolygons(self, blockHeight: float, selfWidth: float) -> None:
        """Initializes different polygons based on block height and self-width"""
        self.previousBlockHeight = blockHeight
        self.previousSelfWidth = selfWidth
        # A right arrow
        xa = 6
        xb = 0.4 * selfWidth
        xc = 0.9 * selfWidth
        ya = 0.1 * blockHeight
        yb = 0.25 * blockHeight
        yc = 0.5 * blockHeight
        yd = 0.75 * blockHeight
        ye = 0.9 * blockHeight
        self.rightArrowPoints = [(xa, yb), (xa, yd), (xb, yd), (xb, ye), (xc, yc), (xb, ya), (xb, yb)]
        # A stop sign
        length = min(selfWidth, blockHeight) - 0.2 * min(selfWidth, blockHeight)
        xa = 0.0
        xb = length / 4.0
        xc = 3 * length / 4.0
        xd = length
        ya = 0.0
        yb = length / 4.0
        yc = 3 * length / 4.0
        yd = length
        stopPoints = [(xa, yb), (xa, yc), (xb, yd), (xc, yd), (xd, yc), (xd, yb), (xc, ya), (xb, ya)]
        xOffset = (selfWidth - length) / 2
        yOffset = (blockHeight - length) / 2
        self.stopPoints = [(x + xOffset, y + yOffset) for (x, y) in stopPoints]
        # From the previous line to PC Arrow
        xa = 3
        ya = 0
        offsets = [(-1, 0), (-1, blockHeight), (0, blockHeight), (0, 0)]
        self.middlePointerPoints = [(xa + xo, ya + yo) for (xo, yo) in offsets]
        xa = 3
        ya = 0.5 * blockHeight
        #
        #     xxxx
        #    xoxxx <- (0, 0)
        #    xx
        #    xx
        offsets = [(-1, 0.5 * blockHeight), (-1, 0), (0, -1), (3, -1), (3, 0), (0, 0), (0, 0.5 * blockHeight)]
        self.upPointerPoints = [(xa + xo, ya + yo) for (xo, yo) in offsets]
        #    xx
        #    xx
        #    xxxxx
        #     oxxx <- (0, 0)
        #
        offsets = [(-1, -0.5 * blockHeight), (-1, -1), (0, 0), (3, 0), (3, -1), (0, -1), (0, -0.5 * blockHeight)]
        self.downPointerPoints = [(xa + xo, ya + yo) for (xo, yo) in offsets]

    @override
    def paintEvent(self, event: QtGui.QPaintEvent):
        """Repaints (part of) the LeftArea Widget"""
        super(LeftArea, self).paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.fillRect(event.rect(), QtGui.QColor('lightGray'))
        block = self.codeEditor.firstVisibleBlock()
        blockNumber = block.blockNumber()
        contentOffset = self.codeEditor.contentOffset()
        top = self.codeEditor.blockBoundingGeometry(block).translated(contentOffset).top()
        blockHeight = self.codeEditor.blockBoundingRect(block).height()
        bottom = top + blockHeight
        selfWidth = self.width()
        if self.codeEditor.isReadOnly():
            if self.previousBlockHeight != blockHeight or self.previousSelfWidth != selfWidth:
                self.initializePolygons(blockHeight, selfWidth)
            # Ribbon coordinates
            ribbonX = selfWidth / 8
            ribbonW = 6 * selfWidth / 8 - 1
            ribbonX1 = ribbonX + ribbonW - 1
            while block.isValid() and block.isVisible():
                if top <= event.rect().bottom() and bottom >= event.rect().top():
                    # The next actions will be done only on blocks affected by an event
                    if blockNumber in self.linesWithBackground:
                        for i, color in enumerate(self.linesWithBackground[blockNumber]):
                            ribbonMinX = min(ribbonX + i, ribbonX1)
                            ribbonMaxW = max(ribbonW - i * 2, 1)
                            painter.fillRect(QtCore.QRectF(ribbonMinX, top, ribbonMaxW, blockHeight), color)
                    if blockNumber == self.codeEditor.getCurrentHighlightedLineNumber():
                        painter.setPen(self.rightArrowColor)
                        painter.setBrush(QtGui.QBrush(self.rightArrowColor.lighter(190)))
                        painter.drawPolygon([QtCore.QPointF(x, y + top) for (x, y) in self.rightArrowPoints])
                    if blockNumber in self.breakpoints:
                        painter.setPen(self.stopPenColor)
                        painter.setBrush(QtGui.QBrush(self.stopFillColor))
                        painter.drawPolygon([QtCore.QPointF(x, y + top) for (x, y) in self.stopPoints])
                if self.previousHighlightedLineNumber != self.currentHighlightedLineNumber \
                        and self.previousHighlightedLineNumber != -1:
                    # The next actions will be done on all visible blocks if the previous condition is met
                    # @warning: a call to self.update() must be done in order to the next part to actually repaint
                    #           all the parts of the trace arrow
                    painter.setPen(self.pointerColor)
                    painter.setBrush(QtGui.QBrush(self.pointerColor))
                    points = None
                    if self.previousHighlightedLineNumber < blockNumber < self.currentHighlightedLineNumber \
                            or self.previousHighlightedLineNumber > blockNumber > self.currentHighlightedLineNumber:
                        points = self.middlePointerPoints
                    elif blockNumber == self.currentHighlightedLineNumber:
                        if self.previousHighlightedLineNumber < self.currentHighlightedLineNumber:
                            points = self.downPointerPoints
                        else:
                            points = self.upPointerPoints
                    elif blockNumber == self.previousHighlightedLineNumber:
                        if self.previousHighlightedLineNumber < self.currentHighlightedLineNumber:
                            points = self.upPointerPoints
                        else:
                            points = self.downPointerPoints
                    if points is not None:
                        painter.drawPolygon([QtCore.QPointF(x, top + y) for (x, y) in points])
                block = block.next()
                top = bottom
                bottom = top + self.codeEditor.blockBoundingRect(block).height()
                blockNumber += 1
        else:
            # Code editor is not read-only
            while block.isValid() and top <= event.rect().bottom():
                if block.isVisible() and bottom >= event.rect().top():
                    number = blockNumber + 1
                    painter.setPen(QtGui.QColor('black'))
                    painter.drawText(-4, int(top), self.width(), self.codeEditor.fontMetrics().height(),
                                     Qt.AlignmentFlag.AlignRight, u"{}".format(number))
                block = block.next()
                top = bottom
                bottom = top + blockHeight
                blockNumber += 1
        # https://stackoverflow.com/questions/59605569/pyside2-raises-error-qpaintdevice-cannot-destroy-paint-device-that-is-being-p
        del painter

    @override
    def width(self) -> int:
        """
        Returns the leftArea width. If the code editor is read-only, a fixed width is computed. Otherwise, the width is
        based on how many blocks has the associated editor.
        """
        if self.codeEditor.isReadOnly():
            width = 8 + self.codeEditor.fontMetrics().horizontalAdvance(u"9") * 2
        else:
            digits = 1
            maxLines = max(1, self.codeEditor.blockCount())
            while maxLines >= 10:
                maxLines /= 10
                digits += 1
            digits = max(2, digits)
            width = 8 + self.codeEditor.fontMetrics().horizontalAdvance(u"9") * digits
        return width

    @override
    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        """Process the wheel event calling the wheel event on the parent"""
        self.codeEditor.wheelEvent(event)

    @override
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        """
        Process the mouse press events: if the associated code editor is read-only and the left button is clicked,
        find which line in the source code has been clicked on.
        """
        if self.codeEditor.isReadOnly() and event.button() == Qt.MouseButton.LeftButton:
            y = int(event.position().y())
            block = self.codeEditor.firstVisibleBlock()
            bottom = self.codeEditor.blockBoundingGeometry(block).translated(self.codeEditor.contentOffset()).bottom()
            blockHeight = self.codeEditor.blockBoundingRect(block).height()
            while block.isValid() and bottom < y:
                block = block.next()
                bottom += blockHeight
            if block.isValid() and block.text().strip() != "":
                self.setOrClearBreakpoint(block.blockNumber(), block.text())
                self.update()
        else:
            super(LeftArea, self).mousePressEvent(event)

    def clearBreakpoints(self) -> None:
        self.breakpoints.clear()

    def setOrClearBreakpoint(self, lineNumber: int, text: str) -> None:
        if lineNumber in self.breakpoints:
            self.breakpoints.pop(lineNumber)
            self.codeEditor.clearBreakpointSignal.emit(lineNumber, text)
        else:
            self.breakpoints[lineNumber] = text
            self.codeEditor.setBreakpointSignal.emit(lineNumber, text)

    def clearLinesWithBackground(self) -> None:
        self.linesWithBackground.clear()
        self.previousHighlightedLineNumber = -1
        self.currentHighlightedLineNumber = -1
        self.currentBgColor = QtGui.QColor('blue').lighter(140)
        self.bgColors = [QtGui.QColor(self.currentBgColor)]  # @warning: a new instance, no the color

    def setCurrentHighlightedLineNumber(self, lineNumber: int):
        """
        Sets the previously highlighted line background properties.

        @param lineNumber: the line number of the current highlighted number.
        """
        if self.currentHighlightedLineNumber == -1:
            # After a reset
            self.previousHighlightedLineNumber = lineNumber
            self.currentHighlightedLineNumber = lineNumber
        elif self.currentHighlightedLineNumber != lineNumber:
            # Moved to an address different of the next one
            if self.currentHighlightedLineNumber != lineNumber - 1:
                # A branch has been done
                # 1) Compute a new background color
                (h, s, v, a) = cast(tuple[int, int, int, int], self.currentBgColor.getHsv())
                self.currentBgColor.setHsv((h - 50) % 360, s, v, a)
                if self.currentHighlightedLineNumber in self.linesWithBackground:
                    # If the current line has already been traced, change the last background color
                    self.bgColors[-1] = QtGui.QColor(self.currentBgColor)
                else:
                    # Else, append a new background color
                    self.bgColors.append(QtGui.QColor(self.currentBgColor))
                # Set this line background colors to the list of background colors
                self.linesWithBackground[self.currentHighlightedLineNumber] = self.bgColors[:]
            else:
                # The next address is being executed
                if self.currentHighlightedLineNumber in self.linesWithBackground:
                    # If the current line has already been traced, add the new background color or change its last one
                    if len(self.bgColors) > len(self.linesWithBackground[self.currentHighlightedLineNumber]):
                        self.linesWithBackground[self.currentHighlightedLineNumber].append(
                            QtGui.QColor(self.currentBgColor))
                    else:
                        self.linesWithBackground[self.currentHighlightedLineNumber][-1] = QtGui.QColor(
                            self.currentBgColor)
                else:
                    # Else, set the background colors to the current list minus the first one not null
                    try:
                        self.bgColors[-2] = QtGui.QColor(self.currentBgColor)
                    except IndexError:
                        pass
                    self.linesWithBackground[self.currentHighlightedLineNumber] = self.bgColors[:]
            self.previousHighlightedLineNumber = self.currentHighlightedLineNumber
            self.currentHighlightedLineNumber = lineNumber
        # Due to the need of repainting the trace arrow, which can involve more regions than the ones that
        # should be marked to repaint, self.update() should be called to be able to repaint the whole
        # visible part of the widget, not only those regions marked as dirty.
        self.update()


class CodeEditor(QtWidgets.QPlainTextEdit):
    """CodeEditor is a simple code editor that is able to use a syntax highlighter and provides a left line number
    area. """

    setBreakpointSignal = QtCore.Signal(int, str)
    clearBreakpointSignal = QtCore.Signal(int, str)
    highlightedWordSignal = QtCore.Signal(str)

    def __init__(self, parent: QtWidgets.QWidget | None = None, SyntaxHighlighterClass=None, *args, **kwargs) -> None:
        """CodeEditor initialization"""
        super().__init__(parent, *args, **kwargs)
        # ------------------------------------------------------------
        #  Instance attributes that will be properly initialized later
        # ------------------------------------------------------------
        self.currentHighlightedLineNumber: int = 0
        # ------------------------------------------------------------
        # Set the default font and tab distance
        self.myFont = getMonoSpacedFont()
        self.setFont(self.myFont)
        self.setTabStopCharacters(8)
        # Disable wrap mode
        self.setLineWrapMode(QtWidgets.QPlainTextEdit.LineWrapMode.NoWrap)
        # Add leftArea child
        self.leftArea = LeftArea(self)
        self.updateLeftAreaWidth(0)
        # Set syntax highlighter
        if SyntaxHighlighterClass is not None:
            self.syntaxHighlighter = SyntaxHighlighterClass(self.document())
        # Set extra highlight selections (current line and special keywords)
        self.setCurrentHighlightedLineNumber(0)
        self.updateHighlightSelections()
        # Set scrollLock to False
        self.scrollLock = False
        # Set show tabs and spaces to False
        self.showTabsAndSpaces = False
        # Connect signals
        _ = self.blockCountChanged.connect(self.updateLeftAreaWidth)
        _ = self.updateRequest.connect(self.updateLeftArea)
        _ = self.cursorPositionChanged.connect(self.updateHighlightSelections)

    def setReadOnly(self, ro: bool):
        """
        Sets the read-only property to True or False.

        @param ro: The value to be set.
        """
        if ro:
            self.updateLeftAreaWidth()
        return super().setReadOnly(ro)

    def setTabStopWidth(self, _distance: float):  # pyright: ignore[reportUnusedParameter]
        raise Exception("Use setTabStopCharacters instead")

    def setTabStopDistance(self, _distance: float):  # pyright: ignore[reportUnusedParameter]
        raise Exception("Use setTabStopCharacters instead")

    def setTabStopCharacters(self, characters: int) -> None:
        length = characters * self.fontMetrics().horizontalAdvance(' ' * 10000) / 10000
        super().setTabStopDistance(length)

    @QtCore.Slot()  # pyright: ignore[reportAny]
    def toggleShowTabsAndSpaces(self):
        """
        Toggles ShowTabsAndSpaces option
        """
        self.showTabsAndSpaces = not self.showTabsAndSpaces
        options = self.document().defaultTextOption()
        if self.showTabsAndSpaces:
            options.setFlags(QtGui.QTextOption.Flag.ShowTabsAndSpaces)
        else:
            flags = options.flags() & ~QtGui.QTextOption.Flag.ShowTabsAndSpaces
            options.setFlags(flags)
        self.document().setDefaultTextOption(options)

    def clearBreakpoints(self) -> None:
        """Calls leftArea clearBreakpoints method"""
        self.leftArea.clearBreakpoints()

    def clearDecorations(self) -> None:
        """Calls leftArea clearLinesWithBackground method"""
        self.leftArea.clearLinesWithBackground()

    def setCurrentHighlightedLineNumber(self, lineNumber: int) -> None:
        """
        Sets the stored currentHighlightedLineNumber variable.

        @param lineNumber: the line number to be set.
        """
        self.currentHighlightedLineNumber = lineNumber
        self.leftArea.setCurrentHighlightedLineNumber(lineNumber)
        self.updateHighlightSelections()

    def getCurrentHighlightedLineNumber(self) -> int:
        """
        Returns the current highlighted line number.

        The return value depends on whether the editor is read-only of not.  If it is read-only, it returns the
        stored currentHighlightedLineNumber. Otherwise, it returns the line number where the current cursor is.
        """
        if self.isReadOnly():
            return self.currentHighlightedLineNumber
        else:
            return self.textCursor().blockNumber()

    def _getCurrentHighlightedLineCursor(self) -> QtGui.QTextCursor:
        """
        Returns a cursor to the current highlighted line.

        The return value depends on whether the editor is read-only of not.  If it is read-only, it returns a cursor
        on the stored currentHighlightedLineNumber line. Otherwise, it returns the current cursor.
        """
        cursor = self.textCursor()
        if self.isReadOnly():
            cursorBlockNumber = cursor.blockNumber()
            if cursorBlockNumber > self.currentHighlightedLineNumber:
                cursor.movePosition(QtGui.QTextCursor.MoveOperation.Up, QtGui.QTextCursor.MoveMode.MoveAnchor,
                                    cursorBlockNumber - self.currentHighlightedLineNumber)
            else:
                cursor.movePosition(QtGui.QTextCursor.MoveOperation.Down, QtGui.QTextCursor.MoveMode.MoveAnchor,
                                    self.currentHighlightedLineNumber - cursorBlockNumber)
            self.setTextCursor(cursor)
        return cursor

    def contextMenuEvent(self, event: QContextMenuEvent):
        menu = self.createStandardContextMenu()
        menu.addSeparator()
        txt = "Hide tabs and spaces" if self.showTabsAndSpaces else "Show tabs and spaces"
        menu.addAction(txt, self.toggleShowTabsAndSpaces)
        menu.exec(event.globalPos())

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        """Resize the leftArea child widget when a resize event is triggered"""
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.leftArea.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.leftArea.width(), cr.height()))

    # noinspection PyUnusedLocal
    def updateLeftAreaWidth(self, _newBlockCount: int | None = None) -> None:  # pyright: ignore[reportUnusedParameter]
        """Changes the code editor left margin based on the width of the leftArea child widget"""
        self.setViewportMargins(self.leftArea.width(), 0, 0, 0)

    def updateLeftArea(self, rect: QtCore.QRect, dy: int) -> None:
        """Updates the leftArea child widgets when an updateRequest event is triggered"""
        if dy:
            self.leftArea.scroll(0, dy)
        else:
            self.leftArea.update(0, rect.y(), self.leftArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLeftAreaWidth()

    def updateHighlightSelections(self) -> None:
        """Sets the selections to be highlighted"""
        extraSelections = [self._getCurrentLineHighlightSelection()]
        extraSelections += self._getCurrentWordHighlightSelections()
        self.setExtraSelections(extraSelections)

    def _getCurrentLineHighlightSelection(self) -> QtWidgets.QTextEdit.ExtraSelection:
        """Returns the current line highlight selection"""
        lineColor = QtGui.QColor('blue').lighter(190)
        selection = QtWidgets.QTextEdit.ExtraSelection()
        selection.format.setBackground(lineColor)
        selection.format.setProperty(QtGui.QTextFormat.Property.FullWidthSelection, True)
        selection.cursor = self._getCurrentHighlightedLineCursor()
        selection.cursor.clearSelection()
        return selection

    def _getCurrentWordHighlightSelections(self) -> list[QtWidgets.QTextEdit.ExtraSelection]:
        """Returns highlight selections for those words in the document that match the current word under the cursor
        (only if the current word is a special keyword) """
        words = self._getKeywordsToHighlight()
        cursor = self.textCursor()
        cursor.select(QtGui.QTextCursor.SelectionType.WordUnderCursor)
        currentWord = cursor.selectedText()
        lineColor = QtGui.QColor('yellow')
        selections = []
        if currentWord in words:
            cursor_ = QtGui.QTextCursor(self.document())
            while not cursor_.isNull() and not cursor_.atEnd():
                cursor_ = self.document().find(currentWord, cursor_, QtGui.QTextDocument.FindFlag.FindWholeWords)
                if not cursor_.isNull():  # and cursor_.blockNumber() != currentLine:
                    selection = QtWidgets.QTextEdit.ExtraSelection()
                    selection.format.setBackground(lineColor)
                    selection.cursor = cursor_
                    selections.append(selection)
            self.highlightedWordSignal.emit(currentWord)
        else:
            self.highlightedWordSignal.emit('')
        return selections

    def _getKeywordsToHighlight(self) -> list[str]:
        """Returns a list of keywords that should be highlighted when that keyword is under the cursor"""
        return []

    def increaseFontSize(self, inc: int):
        """
        Increases (decreases) the font size
        :param inc: number of points to increase the font
        """
        myFontPointSize = self.myFont.pointSize()
        myFontPointSize += inc
        if myFontPointSize < 10:
            myFontPointSize = 10
        self.myFont.setPointSize(myFontPointSize)
        self.setFont(self.myFont)
        self.setTabStopCharacters(8)

    def keyPressEvent(self, event: QKeyEvent):
        """
        Processes the CTRL++ and CTRL+- events
        """
        if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
            if event.text() == '+':
                self.increaseFontSize(1)
                return
            elif event.text() == '-':
                self.increaseFontSize(-1)
                return
        super().keyPressEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        """
        Processes the wheel event: zooms in and out whenever a CTRL+wheel event is triggered
        """
        if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
            self.increaseFontSize(event.angleDelta().y() // 120)
        else:
            super().wheelEvent(event)

    def scrollContentsBy(self, dx: int, dy: int) -> None:
        """Overrides scrollContentsBy to allow appending text without scrolling"""
        if not self.scrollLock:
            super().scrollContentsBy(dx, dy)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    editor = CodeEditor()
    editor.setPlainText(open("../../examples/add.s").read())
    editor.setWindowTitle("Code Editor Example")
    editor.setGeometry(QtCore.QRect(200, 200, 600, 400))
    editor.show()
    sys.exit(app.exec())
