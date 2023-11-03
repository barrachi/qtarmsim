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
from abc import ABC, abstractmethod

class HighlightingRule:
    """A highlighting rule consists of a QRegularExpression pattern and its associated QTextCharFormat"""
    def __init__(self, patternTxt, hrFormat):
        self.pattern = QtCore.QRegularExpression(patternTxt)
        self.format = hrFormat

class PostInitCaller(type):
    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)
        obj.__post_init__()
        return obj


class SyntaxHighlighter(ABC, QtGui.QSyntaxHighlighter, metaclass=PostInitCaller):
    """Class that can be used to parse and highlight a given code"""

    def __init__(self, parent):
        """Initializes the different patterns and their respective formats"""
        super().__init__(parent)
        self.highlightingRules = None  # To be defined on __post_init__() method

    @abstractmethod
    def __post_init__(self):
        # self.highlightingRules = generateHighlightingRules()
        pass

    def highlightBlock(self, text):
        """Parses a given block and applies the corresponding formats to the matched patterns"""
        # First, apply the patterns and formats from self.highlightingRules
        # ------------------------------------------------
        for rule in self.highlightingRules:
            print(rule)
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
