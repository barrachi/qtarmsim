# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'value.ui'
#
# Created: Wed Mar 26 22:33:02 2008
#      by: PyQt4 UI code generator 4-snapshot-20070727
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Value(object):
    def setupUi(self, Value):
        Value.setObjectName("Value")
        Value.resize(QtCore.QSize(QtCore.QRect(0,0,400,142).size()).expandedTo(Value.minimumSizeHint()))

        self.direcLabel = QtGui.QLabel(Value)
        self.direcLabel.setGeometry(QtCore.QRect(20,20,151,16))
        self.direcLabel.setObjectName("direcLabel")

        self.direcLineEdit = QtGui.QLineEdit(Value)
        self.direcLineEdit.setGeometry(QtCore.QRect(20,40,201,20))
        self.direcLineEdit.setObjectName("direcLineEdit")

        self.valueLabel = QtGui.QLabel(Value)
        self.valueLabel.setGeometry(QtCore.QRect(20,80,46,14))
        self.valueLabel.setObjectName("valueLabel")

        self.valueLineEdit = QtGui.QLineEdit(Value)
        self.valueLineEdit.setGeometry(QtCore.QRect(20,100,201,20))
        self.valueLineEdit.setObjectName("valueLineEdit")

        self.aceptarButton = QtGui.QPushButton(Value)
        self.aceptarButton.setGeometry(QtCore.QRect(290,20,75,23))
        self.aceptarButton.setObjectName("aceptarButton")

        self.cancelarButton = QtGui.QPushButton(Value)
        self.cancelarButton.setGeometry(QtCore.QRect(290,60,75,23))
        self.cancelarButton.setObjectName("cancelarButton")

        self.retranslateUi(Value)
        QtCore.QMetaObject.connectSlotsByName(Value)

    def retranslateUi(self, Value):
        Value.setWindowTitle(QtGui.QApplication.translate("Value", "Asignar valor a registro", None, QtGui.QApplication.UnicodeUTF8))
        self.direcLabel.setText(QtGui.QApplication.translate("Value", "Dirección o nombre de registro:", None, QtGui.QApplication.UnicodeUTF8))
        self.valueLabel.setText(QtGui.QApplication.translate("Value", "Valor:", None, QtGui.QApplication.UnicodeUTF8))
        self.aceptarButton.setText(QtGui.QApplication.translate("Value", "&Aceptar", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelarButton.setText(QtGui.QApplication.translate("Value", "&Cancelar", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Value = QtGui.QDialog()
    ui = Ui_Value()
    ui.setupUi(Value)
    Value.show()
    sys.exit(app.exec_())
