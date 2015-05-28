# -*- coding: utf-8 -*-

##Módulo im
#
#Construir el diálogo para imprimir en el panel de mensajes el contenido de un rango de memoria o de las etiquetas globales


import sys
from PySide import QtCore, QtGui
from ..ui.imprimir import Ui_Imprimir

##Clase que define el diálogo imprimir valor que hereda de la clase QDialog del módulo QtGui
class Imprimir(QtGui.QDialog):
    ##Constructor del diálogo imprimir valor
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        self.ui=Ui_Imprimir()
        self.ui.setupUi(self)
        
        self.ui.comboBox.addItem (QtGui.QApplication.translate("MainWindow", "Símbolos globales", None, QtGui.QApplication.UnicodeUTF8))
        self.ui.comboBox.addItem("Rango de memoria")
        self.connect(self.ui.comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.con)
        
        
        layoutH=QtGui.QHBoxLayout(self)
        
        layoutV=QtGui.QVBoxLayout()
        layoutV.addWidget(self.ui.aceptarButton)
        layoutV.addWidget(self.ui.cancelarButton)
        layoutV.setAlignment(QtCore.Qt.AlignTop)
        
        
        layout=QtGui.QVBoxLayout()
        layout.insertStretch(1)
        layout.addWidget(self.ui.comboBox)
        layout.insertStretch(3)
        layout.addWidget(self.ui.labelFrom)
        layout.addWidget(self.ui.fromEdit)
        layout.insertStretch(6)
        layout.addWidget(self.ui.Tolabel)
        layout.addWidget(self.ui.toEdit)
        layout.insertStretch(9)
        
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
        self.connect(self.ui.aceptarButton,QtCore.SIGNAL("clicked()"),self.imp_accept)
        
        self.cancelarButton = QtGui.QAction(self.trUtf8("Cancelar"), self)
        self.connect(self.ui.cancelarButton,QtCore.SIGNAL("clicked()"),self.reject)
        
    ##Método asociado al cambio de selección en comboBox
    #
    #Dependiendo de si se pretende mostrar el contenido de un rango de memoria o el contenido de las etiquetas globales,
    #activa o desactiva los campos de texto para introducir las direcciones de memoria inicial y final del rango de memoria
    def con(self):
        if self.ui.comboBox.currentIndex()==1:
            self.ui.fromEdit.setEnabled(1)
            self.ui.toEdit.setEnabled(1)
        else:
            self.ui.fromEdit.setEnabled(0)
            self.ui.toEdit.setEnabled(0)
            
    ##Método asociado a aceptarButton
    #
    #Imprime el valor del rango de memoria o de los símbolos globales
    def imp_accept(self):
        if self.ui.comboBox.currentIndex()==1:
            if (self.ui.fromEdit.text()=="") or (self.ui.toEdit.text()==""):
                QtGui.QMessageBox.information(self, self.trUtf8("Error"), self.trUtf8("El rango de memoria introducido es incorrecto"))  
                return
            else:
                cad="Imprimiendo contenido de memoria desde " + self.ui.fromEdit.text() + " hasta " + self.ui.toEdit.text()
        else:
            cad=QtGui.QApplication.translate("MainWindow", "Imprimiendo símbolos globales", None, QtGui.QApplication.UnicodeUTF8)
        padre=self.parentWidget()
        padre.mens.append(cad)   
        self.accept()
            
            
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    imp=Imprimir()
    imp.show()
    sys.exit(app.exec_())
