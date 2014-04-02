# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ayuda.ui'
#
# Created: Tue May 06 00:23:28 2008
#      by: PyQt4 UI code generator 4-snapshot-20070727
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Ayuda(object):
    def setupUi(self, Ayuda):
        Ayuda.setObjectName("Ayuda")
        Ayuda.resize(QtCore.QSize(QtCore.QRect(0,0,562,524).size()).expandedTo(Ayuda.minimumSizeHint()))

        self.retranslateUi(Ayuda)
        QtCore.QMetaObject.connectSlotsByName(Ayuda)

    def retranslateUi(self, Ayuda):
        Ayuda.setWindowTitle(QtGui.QApplication.translate("Ayuda", "Ayuda", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Ayuda = QtGui.QWidget()
    ui = Ui_Ayuda()
    ui.setupUi(Ayuda)
    Ayuda.show()
    sys.exit(app.exec_())
