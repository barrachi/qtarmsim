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


import sys

from PySide2 import QtCore, QtGui, QtWidgets
from .codeeditor import CodeEditor
from .armsyntaxhighlighter import ARMSyntaxHighlighter
from .csyntaxhighlighter import CSyntaxHighlighter


class ARMCodeEditor(CodeEditor):
    """CodeEditor with ARMSyntaxHighlighter"""

    def __init__(self, parent=None, *args, **kwargs):
        """ARMCodeEditor initialization"""
        self.ARMSyntaxHighlighterClass = ARMSyntaxHighlighter
        self.CSyntaxHighlighterClass = CSyntaxHighlighter
        super(ARMCodeEditor, self).__init__(parent=parent, SyntaxHighlighterClass=self.ARMSyntaxHighlighterClass, *args, **kwargs)

    def _getKeywordsToHighlight(self):
        """Returns which keywords should be highlighted on the text when the same keyword is under the cursor"""
        registers = ['r{}'.format(n) for n in range(0, 16)] + ['sp', 'SP', 'lr', 'LR', 'pc', 'PC']
        # Labels
        labels = []
        labelQRegExp = QtCore.QRegExp('^\\s*[^\\d\\s][\\w]*:')
        cursor = QtGui.QTextCursor(self.document())
        while not cursor.isNull() and not cursor.atEnd():
            cursor = self.document().find(labelQRegExp, cursor, QtGui.QTextDocument.FindWholeWords)
            if cursor.selectedText():
                labels.append(cursor.selectedText()[:-1].strip())
        # Return special keywords
        return registers + labels

    def setARMMode(self):
        self.syntaxHighlighter = self.ARMSyntaxHighlighterClass(self.document())
        self.setTabStopCharacters(8)

    def setCMode(self):
        self.syntaxHighlighter = self.CSyntaxHighlighterClass(self.document())
        self.setTabStopCharacters(3)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    armEditor = ARMCodeEditor()
    armEditor.setPlainText(open("../../examples/add.s").read())
    armEditor.setWindowTitle("ARM Code Editor Example")
    armEditor.setGeometry(QtCore.QRect(200, 200, 600, 400))
    # armEditor.setReadOnly(True)
    armEditor.show()
    sys.exit(app.exec_())
