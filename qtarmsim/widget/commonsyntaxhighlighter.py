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


from PySide6 import QtCore, QtGui


class HighlightingRule:
    """A highlighting rule consists of a QRegularExpression derived from pattern and its associated QTextCharFormat"""

    def __init__(self, patternTxt, hrFormat):
        self.re = QtCore.QRegularExpression(patternTxt)
        self.format = hrFormat


class CommonSyntaxHighlighter(QtGui.QSyntaxHighlighter):
    """Class that can be used to parse and highlight a given code"""

    def __init__(self, parent):
        """Initializes the different patterns and their respective formats"""
        super().__init__(parent)
        self.highlightingRules = []  # To be defined on the derived classes

    def highlightBlock(self, text):
        """Parses a given block and applies the corresponding formats to the matched patterns"""
        # First, apply the patterns and formats from self.highlightingRules
        # ------------------------------------------------
        for rule in self.highlightingRules:
            i = rule.re.globalMatch(text)
            while i.hasNext():
                match = i.next()
                start = match.capturedStart()
                length = match.capturedLength()
                self.setFormat(start, length, rule.format)
        # Then, deal with multiline comments
        # ------------------------------------------------
        commentStartExpression = QtCore.QRegularExpression('/\\*')
        commentEndExpression = QtCore.QRegularExpression('\\*/')
        multilineCommentFormat = QtGui.QTextCharFormat()
        multilineCommentFormat.setForeground(QtGui.QColor('gray'))
        startIndex = 0
        self.setCurrentBlockState(0)
        if self.previousBlockState() != 1:
            startIndex = commentStartExpression.match(text[startIndex:]).capturedStart()
        while startIndex >= 0:
            endIndex = commentEndExpression.match(text[startIndex:]).capturedStart()
            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
            else:
                commentLength = endIndex - startIndex + 2
            self.setFormat(startIndex, commentLength, multilineCommentFormat)
            startIndex = commentStartExpression.match(text[startIndex + commentLength:]).capturedStart()
