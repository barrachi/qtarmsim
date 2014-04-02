# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'consola.ui'
#
# Created: Tue Mar 18 16:43:14 2008
#      by: PyQt4 UI code generator 4-snapshot-20070727
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Consola(object):
    def setupUi(self, Consola):
        Consola.setObjectName("Consola")
        Consola.resize(QtCore.QSize(QtCore.QRect(0,0,295,302).size()).expandedTo(Consola.minimumSizeHint()))



        self.retranslateUi(Consola)
        QtCore.QMetaObject.connectSlotsByName(Consola)

    def retranslateUi(self, Consola):
        pass



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Consola = QtGui.QWidget()
    ui = Ui_Consola()
    ui.setupUi(Consola)
    Consola.show()
    sys.exit(app.exec_())
