# -*- coding: utf-8 -*-

##Módulo op
#
#Construir el diálogo de opciones del simulador

import sys
from PySide import QtCore, QtGui
from ..ui.opciones import Ui_Opciones

##Clase que define el diálogo opciones que hereda de la clase QDialog del módulo QtGui
class Opciones(QtGui.QDialog):
    options=[0, 0, 0, 0]
    ##Constructor del diálogo opciones
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        self.ui=Ui_Opciones()
        self.ui.setupUi(self)
        self.createActions()
        padre=self.parentWidget()
        self.options=[0, 0, 0, 0]
        #Por defecto Loadtrap esta activado
        if padre.options[0]==1:
            self.ui.Loadtrap.setCheckState(QtCore.Qt.Checked)
        if padre.options[1]==1:
            self.ui.Bare.setCheckState(QtCore.Qt.Checked)
        if padre.options[2]==1:
            self.ui.Quiet.setCheckState(QtCore.Qt.Checked)
        if padre.options[3]==1:
            self.ui.Mapped.setCheckState(QtCore.Qt.Checked)
        #Llamada que introduce la direccion por defecto
        self.ui.Directrap.setText(parent.pathini)
        self.ui.Directrap.adjustSize()
        
        self.horizontalGroupBox = QtGui.QGroupBox(self.trUtf8("Modo de funcionamiento"))
        
        layout1=QtGui.QHBoxLayout()
        layout1.addWidget(self.ui.Bare)
        layout1.addWidget(self.ui.Quiet)
        layout1.addWidget(self.ui.Mapped)
 
        self.horizontalGroupBox.setLayout(layout1)
        
        
        layout2=QtGui.QHBoxLayout()
        layout2.addWidget(self.ui.Loadtrap)
        layout2.addWidget(self.ui.Directrap)
        layout2.addWidget(self.ui.actionExplorar)
 
        
        layout3=QtGui.QVBoxLayout()
        layout3.addWidget(self.ui.buttonBox)
        layout3.addWidget(self.ui.cancelarButton)
        layout3.setAlignment(QtCore.Qt.AlignTop)
        
        layout4=QtGui.QVBoxLayout()
        layout4.insertStretch(1)
        layout4.addWidget(self.horizontalGroupBox)
        layout4.insertStretch(3)
        layout4.addLayout(layout2)
        layout4.insertStretch(5)
        
        layoutH=QtGui.QHBoxLayout(self)
        layoutH.addLayout(layout4)
        layoutH.insertStretch(2)
        layoutH.addLayout(layout3)
        
        self.adjustSize()
        layoutH.setSizeConstraint(QtGui.QLayout.SetFixedSize)

        
    ##Función que traduce una cadena dada a codificación UTF8
    #
    #Recibe como parámetro la cadena a traducir
    def tr(self, string):
        return QtGui.QApplication.translate("MainWindow", string, None, QtGui.QApplication.UnicodeUTF8)
        
    ##Método asociado a actionExplorar
    #
    #Abre un diálogo para determinar la ruta del archivo de interrupciones
    def explora(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, self.trUtf8("Ruta del archivo"),QtCore.QDir.currentPath(),self.trUtf8("Assembly files (*.s *.asm)"))
        if not fileName == "":
            self.ui.Directrap.setText(fileName)

    ##Método asociado a actionLoadtrap
    #
    #Activa o desactiva el campo que alberga la ruta del archivo de interrupciones dependiendo de si el checkbox cargar archivo de interrupciones está o no activado
    def act(self):
        if self.ui.Loadtrap.isChecked() :
            self.ui.Directrap.setDisabled(False)
            self.ui.actionExplorar.setDisabled(False)
            self.options[0]=1
        else:
            self.ui.Directrap.setDisabled(True)
            self.ui.actionExplorar.setDisabled(True)
            self.options[0]=0

    ##Método asociado a buttonBox, botón de aceptar
    #
    #Se guarda la configuración de las opciones del simulador
    def aceptar(self):
        padre=self.parentWidget()
        #La variable pathini tendra el valor escrito en el lineEdit Directrap
        padre.pathini=self.ui.Directrap.text()
        padre.options=self.options
        self.accept()
    
    ##Método asociado a Bare
    #
    #Activa o desactiva la opción de Máquina básica
    def bar(self):
        if self.ui.Bare.isChecked() :
            self.options[1]=1
        else:
            self.options[1]=0
    
    ##Método asociado a Quiet
    #
    #Activa o desactiva la opción de Modo silencioso
    def qui(self):
        if self.ui.Quiet.isChecked() :
            self.options[2]=1
        else:
            self.options[2]=0
    
    ##Método asociado a Mapped
    #
    #Activa o desactiva la opción de E/S Mapeada
    def map(self):
        if self.ui.Mapped.isChecked() :
            self.options[3]=1
        else:
            self.options[3]=0
    
    ##Método para asociar signals de los botones del diálogo y slots
    def createActions(self):
        self.buttonBox = QtGui.QAction(self.trUtf8("&Aceptar"), self)
        self.connect(self.ui.buttonBox,QtCore.SIGNAL("clicked()"),self.aceptar)
        
        self.cancelarButton = QtGui.QAction(self.trUtf8("&Cancelar"), self)
        self.connect(self.ui.cancelarButton,QtCore.SIGNAL("clicked()"),self.reject)
        
        self.actionExplorar = QtGui.QAction(self.trUtf8("&Explorar"), self)
        self.connect(self.ui.actionExplorar,QtCore.SIGNAL("clicked()"),self.explora)

        self.Loadtrap = QtGui.QAction(self.trUtf8("Load"), self)
        self.connect(self.ui.Loadtrap,QtCore.SIGNAL("stateChanged(int)"),self.act)
        
        self.Bare = QtGui.QAction(self.trUtf8("Bare"), self)
        self.connect(self.ui.Bare,QtCore.SIGNAL("stateChanged(int)"),self.bar)
        self.ui.Bare.setToolTip(self.trUtf8("Simula el ensamblador sin pseudoinstrucciones o modos de direccionamiento suministrados por el simulador"))
        
        self.Quiet = QtGui.QAction(self.trUtf8("Quiet"), self)
        self.connect(self.ui.Quiet,QtCore.SIGNAL("stateChanged(int)"),self.qui)
        self.ui.Quiet.setToolTip(self.trUtf8("Permite seleccionar que PCSpim no imprima ningún mensaje cuando se producen las excepciones"))
        
        self.Mapped = QtGui.QAction(self.trUtf8("Mapped"), self)
        self.connect(self.ui.Mapped,QtCore.SIGNAL("stateChanged(int)"),self.map)
        self.ui.Mapped.setToolTip(self.trUtf8("Permite seleccionar si se activa la entrada/salida mapeada en memoria"))
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    optionsw = Opciones()
    optionsw.show()
    sys.exit(app.exec_())
