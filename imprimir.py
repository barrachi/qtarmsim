# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'imprimir.ui'
#
# Created: Thu Apr 03 17:16:56 2008
#      by: PyQt4 UI code generator 4-snapshot-20070727
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Imprimir(object):
    def setupUi(self, Imprimir):
        Imprimir.setObjectName("Imprimir")
        Imprimir.resize(QtCore.QSize(QtCore.QRect(0,0,400,300).size()).expandedTo(Imprimir.minimumSizeHint()))

        self.aceptarButton = QtGui.QPushButton(Imprimir)
        self.aceptarButton.setGeometry(QtCore.QRect(300,30,75,23))
        self.aceptarButton.setObjectName("aceptarButton")

        self.cancelarButton = QtGui.QPushButton(Imprimir)
        self.cancelarButton.setGeometry(QtCore.QRect(300,70,75,23))
        self.cancelarButton.setObjectName("cancelarButton")

        self.comboBox = QtGui.QComboBox(Imprimir)
        self.comboBox.setGeometry(QtCore.QRect(30,40,181,21))
        self.comboBox.setObjectName("comboBox")

        self.labelFrom = QtGui.QLabel(Imprimir)
        self.labelFrom.setGeometry(QtCore.QRect(30,110,46,14))
        self.labelFrom.setObjectName("labelFrom")

        self.Tolabel = QtGui.QLabel(Imprimir)
        self.Tolabel.setGeometry(QtCore.QRect(30,170,46,14))
        self.Tolabel.setObjectName("Tolabel")

        self.fromEdit = QtGui.QLineEdit(Imprimir)
        self.fromEdit.setEnabled(False)
        self.fromEdit.setGeometry(QtCore.QRect(30,130,121,20))
        self.fromEdit.setObjectName("fromEdit")

        self.toEdit = QtGui.QLineEdit(Imprimir)
        self.toEdit.setEnabled(False)
        self.toEdit.setGeometry(QtCore.QRect(30,190,121,20))
        self.toEdit.setObjectName("toEdit")

        self.retranslateUi(Imprimir)
        QtCore.QMetaObject.connectSlotsByName(Imprimir)

    def retranslateUi(self, Imprimir):
        Imprimir.setWindowTitle(QtGui.QApplication.translate("Imprimir", "Imprimir valor", None, QtGui.QApplication.UnicodeUTF8))
        self.aceptarButton.setText(QtGui.QApplication.translate("Imprimir", "&Aceptar", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelarButton.setText(QtGui.QApplication.translate("Imprimir", "&Cancelar", None, QtGui.QApplication.UnicodeUTF8))
        self.labelFrom.setText(QtGui.QApplication.translate("Imprimir", "desde:", None, QtGui.QApplication.UnicodeUTF8))
        self.Tolabel.setText(QtGui.QApplication.translate("Imprimir", "hasta:", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Imprimir = QtGui.QDialog()
    ui = Ui_Imprimir()
    ui.setupUi(Imprimir)
    Imprimir.show()
    sys.exit(app.exec_())
