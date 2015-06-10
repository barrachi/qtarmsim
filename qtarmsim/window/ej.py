# -*- coding: utf-8 -*-


##Módulo ej
#
#Construir el diálogo para introducir los parámetros de ejecución

import sys
from PySide import QtCore, QtGui
from ..ui.ejec import Ui_Ejecutar

##Clase que define el diálogo parámetros de ejecución que hereda de la clase QDialog del módulo QtGui
class Ejecutar(QtGui.QDialog):
    ##Constructor del diálogo parámetros de ejecución
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        self.ui=Ui_Ejecutar()
        self.ui.setupUi(self)
        
        layoutH=QtGui.QHBoxLayout(self)
        
        layoutV=QtGui.QVBoxLayout()
        layoutV.addWidget(self.ui.aceptarButton)
        layoutV.addWidget(self.ui.cancelarButton)
        layoutV.setAlignment(QtCore.Qt.AlignTop)
        
        layout=QtGui.QVBoxLayout()
        
        layout1=QtGui.QVBoxLayout()
        layout1.addWidget(self.ui.adresslabel)
        layout1.addWidget(self.ui.adress)
        
        layout2=QtGui.QVBoxLayout()
        layout2.addWidget(self.ui.linelabel)
        layout2.addWidget(self.ui.lineEdit)
        
        layout.insertStretch(1)
        layout.addLayout(layout1)
        layout.insertStretch(3)
        layout.addLayout(layout2)
        layout.insertStretch(5)
        layout.addWidget(self.ui.undefcheckBox)
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
        self.connect(self.ui.aceptarButton,QtCore.SIGNAL("clicked()"),self.accept)
        
        self.cancelarButton = QtGui.QAction(self.trUtf8("Cancelar"), self)
        self.connect(self.ui.cancelarButton,QtCore.SIGNAL("clicked()"),self.reject)

        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    ej=Ejecutar()
    ej.show()
    sys.exit(app.exec_())
