# -*- coding: utf-8 -*-

##Módulo mu
#
#Construir el diálogo para introducir el número de instrucciones a ejecutar

import sys
from PySide import QtCore, QtGui
from ..ui.multi import Ui_Multipasos

##Clase que define el diálogo múltiples pasos que hereda de la clase QDialog del módulo QtGui
class Multipasos(QtGui.QDialog):
    ##Constructor del diálogo de múltiples pasos
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        self.ui=Ui_Multipasos()
        self.ui.setupUi(self)
        self.createActions()
        
        layoutH=QtGui.QHBoxLayout(self)
        
        layoutV=QtGui.QVBoxLayout()
        layoutV.addWidget(self.ui.aceptarButton)
        layoutV.addWidget(self.ui.cancelarButton)
        layoutV.setAlignment(QtCore.Qt.AlignTop)
        
        self.ui.pasos.setText("1")
        layout=QtGui.QVBoxLayout()
        layout.insertStretch(1)
        layout.addWidget(self.ui.pasoslabel)
        layout.addWidget(self.ui.pasos)
        layout.insertStretch(4)
        
        layoutH.addLayout(layout)
        layoutH.insertStretch(2)
        layoutH.addLayout(layoutV)
        
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
        self.connect(self.ui.aceptarButton,QtCore.SIGNAL("clicked()"),self.multi_accept)
        
        self.cancelarButton = QtGui.QAction(self.trUtf8("Cancelar"), self)
        self.connect(self.ui.cancelarButton,QtCore.SIGNAL("clicked()"),self.reject)
        
    ##Método asociado a aceptarButton
    #
    #Ejecuta el número de instrucciones indicadas
    def multi_accept(self):
        if self.ui.pasos.text() == "":
            self.ui.pasos.setText("1")
        cad=self.trUtf8("Ejecutando ") + self.ui.pasos.text() + self.trUtf8(" instrucciones")
        padre=self.parentWidget()
        padre.mens.append(cad)
        self.accept()
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    mu=Multipasos()
    mu.show()
    sys.exit(app.exec_())
