# -*- coding: utf-8 -*-
##Módulo br
#
#Construir el diálogo para añadir o elminar puntos de ruptura en el programa 

import sys
from PySide import QtCore, QtGui
from ..ui.breakpo import Ui_Break

##Clase que define el diálogo puntos de ruptura que hereda de la clase QDialog del módulo QtGui
class Breakpoi(QtGui.QDialog):
    ##Constructor del diálogo puntos de ruptura
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        self.ui=Ui_Break()
        self.ui.setupUi(self)
        
        self.topLabel = QtGui.QLabel(QtGui.QApplication.translate("MainWindow", "Dirección: (ej. 0x00400000)", None, QtGui.QApplication.UnicodeUTF8))
        
        self.dirEdit = QtGui.QLineEdit()
  
        self.addButton = QtGui.QPushButton(self.trUtf8("&Añadir"))
        self.addButton.setGeometry(QtCore.QRect(300,20,75,23))
        self.addButton.setObjectName("addButton")


        self.removeButton = QtGui.QPushButton("&Eliminar")
        self.removeButton.setGeometry(QtCore.QRect(300,50,75,23))
        self.removeButton.setObjectName("removeButton")


        self.closeButton = QtGui.QPushButton("&Cerrar")
        self.closeButton.setGeometry(QtCore.QRect(300,80,75,23))
        self.closeButton.setObjectName("closeButton")

        self.createActions()
    
        layoutH=QtGui.QHBoxLayout(self)  
  
        layoutV = QtGui.QVBoxLayout()
        layoutV.addWidget(self.addButton)
        layoutV.addWidget(self.removeButton)
        layoutV.addWidget(self.closeButton)
        layoutV.setAlignment(QtCore.Qt.AlignTop)
        
        self.layout = QtGui.QVBoxLayout()
        #layout.insertStretch(1)
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.layout.addWidget(self.topLabel)
        self.layout.addWidget(self.dirEdit)
        #layout.insertStretch(4)
        #self.layout.addWidget(self.ptosListBox)
        

        layoutH.addLayout(self.layout)
        #layoutH.insertStretch(2)
        layoutH.addLayout(layoutV)
        
        self.adjustSize()
        layoutH.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        
        self.padre=self.parentWidget()
     
    #def closeEvent(self, event):
        #self.ptosListBox.selectAll()
        #padre=self.parentWidget()
        #padre.cadena=self.ptosListBox.mimeTypes()
        #padre.cadena=self.ptosListBox.selectedItems()
        #event.accept()

    ##Función que traduce una cadena dada a codificación UTF8
    #
    #Recibe como parámetro la cadena a traducir
        
    def tr(self, string):
        return QtGui.QApplication.translate("MainWindow", string, None, QtGui.QApplication.UnicodeUTF8)
        
        
    ##Método para asociar signals de los botones del diálogo y slots
    def createActions(self):
        self.connect(self.addButton, QtCore.SIGNAL("clicked()"), self.add)
        self.connect(self.removeButton, QtCore.SIGNAL("clicked()"), self.remove)
        self.connect(self.closeButton, QtCore.SIGNAL("clicked()"), self.close)
        
   
    ##Función que comprueba si un número es hexadecimal
    #
    #Recibe como parámetro el número a comprobar y devuelve verdadero en el caso de que sea hexadecimal y falso en el caso contrario
    def comprueba_hex (self, hx):
        valid=True
        if hx=='':
            valid=False
        else:
            if len(hx)>10:
                valid=False
            else:
                vld=['1','2','3','4','5','6','7','8','9','0','a','b','c','d','e','f','A','B','C','D','E','F']
                uno=['x']
                if hx[0]!='0':
                    if len(hx)>8:
                        valid=False
                    else:
                        if hx[0] not in vld:
                            valid=False
                        if len(hx)>1:
                            if hx[1] not in vld:
                                valid=False
                else:
                    if len(hx)>1:
                        if hx[1] not in uno:
                            if hx[1] not in vld:
                                valid=False
                if len(hx)>2:    
                    for i in range(len(hx)-2):
                        if hx[i+2] not in vld:
                            valid=False
        return valid
    
    ##Función que devuelve en el formato deseado el número hexadecimal pasado como parámetro
    #
    #Recibe como parámetro el número original y devuelve el número escrito en el formato deseado
    def escribe_hex (self, hx):
        lst='0x'
        uno=['x']
        dos=['0']
        if hx[0] not in dos:
            for i in range(8-len(hx)):
                lst=lst+'0'
            lst=lst+hx[0]
            if len(hx)>1:
                lst=lst+hx[1]
        else:
            if len(hx)==1:
                for n in range(9-len(hx)):
                    lst=lst+'0'
            if len(hx)>1:
                if hx[1] in uno:
                    for j in range(10-len(hx)):
                        lst=lst+'0'
                else:
                    for j in range(8-len(hx)):
                        lst=lst+'0'
                    lst=lst+hx[0]+hx[1]
        if len(hx)>2:
            for m in range (len(hx)-2):
                lst=lst+hx[(m+2)]
        return lst
                

    ##Método asociado al botón addButton
    #
    #Añade un nuevo punto de ruptura en el programa
    def add(self): 
        nuevo=self.dirEdit.text()
        if self.comprueba_hex(nuevo) :
            #new=self.toHex(nuevo)
            #new= lambda x:"".join([hex(ord(c))[2:].zfill(2) for c in nuevo])
            #new2=str(self.toHex(nuevo))
            #array2=nuevo.toUtf8 ()
            array2=str(nuevo)
            uno=self.escribe_hex(array2)
            #hexac=lambda x:"".join([hex(ord(c)).replace('0x', '') for c in x])
            #hexac2=self.toHex(array2)
            dos=str(uno)
            eso=QtCore.QVariant(dos)
            item=QtGui.QListWidgetItem()
            item.setData (QtCore.Qt.EditRole, eso)
            #lst=str(hexac2)
            #self.ptosListBox.insertItem(0,item)
            self.padre.ptosrup.insertItem(0, item)
            self.dirEdit.clear()
        else:
            QtGui.QMessageBox.information(self, self.trUtf8("Error"), self.trUtf8("La entrada no es correcta"))
            self.dirEdit.clear()
            
            
    ##Método asociado al botón removeButton
    #
    #Elimina el punto de ruptura actualmente seleccionado    
    def remove(self):
        #item=self.ptosListBox.currentRow()
        item=self.padre.ptosrup.currentRow()
        #lista=self.ptosListBox.selectedItems ()
        #eliminado=self.ptosListBox.takeItem (item)
        eliminado=self.padre.ptosrup.takeItem(item)
        #parent=QtCore.QModelIndex()

        
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    br=Breakpoi()
    br.show()
    sys.exit(app.exec_())
