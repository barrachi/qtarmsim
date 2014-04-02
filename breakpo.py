# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'breakpo.ui'
#
# Created: Wed Apr 30 20:40:24 2008
#      by: PyQt4 UI code generator 4-snapshot-20070727
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Break(object):
    def setupUi(self, Break):
        Break.setObjectName("Break")
        Break.resize(QtCore.QSize(QtCore.QRect(0,0,400,300).size()).expandedTo(Break.minimumSizeHint()))

        self.retranslateUi(Break)
        QtCore.QMetaObject.connectSlotsByName(Break)

    def retranslateUi(self, Break):
        Break.setWindowTitle(QtGui.QApplication.translate("Break", "Puntos de ruptura", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Break = QtGui.QDialog()
    ui = Ui_Break()
    ui.setupUi(Break)
    Break.show()
    sys.exit(app.exec_())
