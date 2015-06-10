# -*- coding: utf-8 -*-

##Módulo va
#
#Construir el diálogo que asocia un valor a un registro o posición de memoria

import sys
from PySide import QtCore, QtGui
from ..ui.value import Ui_Value

##Clase que define el diálogo asignar valor que hereda de la clase QDialog del módulo QtGui
class Valor(QtGui.QDialog):
    ##Constructor del diálogo asignar valor
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        self.ui=Ui_Value()
        self.ui.setupUi(self)
        
        layoutH=QtGui.QHBoxLayout(self)
        
        layoutV=QtGui.QVBoxLayout()
        layoutV.addWidget(self.ui.aceptarButton)
        layoutV.addWidget(self.ui.cancelarButton)
        layoutV.setAlignment(QtCore.Qt.AlignTop)
        
        layout=QtGui.QVBoxLayout()
        layout.insertStretch(1)
        layout.addWidget(self.ui.direcLabel)
        layout.addWidget(self.ui.direcLineEdit)
        layout.insertStretch(4)
        layout.addWidget(self.ui.valueLabel)
        layout.addWidget(self.ui.valueLineEdit)
        layout.insertStretch(7)
        
        layoutH.addLayout(layout)
        layoutH.insertStretch(2)
        layoutH.addLayout(layoutV)
        
        self.createActions()
        
        self.adjustSize()
        layoutH.setSizeConstraint(QtGui.QLayout.SetFixedSize)
     
    ##Función que traduce una cadena dada a codificación UTF8
    #
    #Recibe como parámetro la cadena a traducir
    def tr(self, string):
        return QtGui.QApplication.translate("MainWindow", string, None, QtGui.QApplication.UnicodeUTF8)
     
    ##Método para asociar signals de los botones del diálogo y slots 
    def createActions(self):
        self.aceptarButton = QtGui.QAction(self.trUtf8("Aceptar"), self)
        self.connect(self.ui.aceptarButton,QtCore.SIGNAL("clicked()"),self.valor_accept)
        
        self.cancelarButton = QtGui.QAction(self.trUtf8("Cancelar"), self)
        self.connect(self.ui.cancelarButton,QtCore.SIGNAL("clicked()"),self.reject)
    
    ##Método asociado a aceptarButton
    #
    #Si los valores introducidos son correctos asocia el valor dado al registro o dirección especificada
    def valor_accept(self):
        if (self.ui.direcLineEdit.text()=="") or (self.ui.valueLineEdit.text()==""):
            QtGui.QMessageBox.information(self, self.trUtf8("Error"), self.trUtf8("Los valores introducidos no son correctos"))
        else:
            cad=self.trUtf8("Asignando a ") + self.ui.direcLineEdit.text() + self.trUtf8(" el valor ") + self.ui.valueLineEdit.text()
            padre=self.parentWidget()
            padre.mens.append(cad)
            self.accept()
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    va=Valor()
    va.show()
    sys.exit(app.exec_())
