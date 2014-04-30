#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###########################################################################
#  Qt ArmSim -- a Qt graphical interface to armsim                        #
#  ---------------------------------------------------------------------  #
#    begin                : 2014-04-02                                    #
#    copyright            : (C) 2014 by Sergio Barrachina Mir             #
#    email                : barrachi@uji.es                               #
#  ---------------------------------------------------------------------  #
#                                                                         #
# This application is based on a previous work of Gloria Edo Piñana who   #
# developed the graphical part of a graphical interface to the SPIM       #
# simulator in 2008.                                                      #
#                                                                         #
###########################################################################

###########################################################################
#                                                                         #
#  This program is free software; you can redistribute it and/or modify   #
#  it under the terms of the GNU General Public License as published by   #
#  the Free Software Foundation; either version 2 of the License, or      #
#  (at your option) any later version.                                    #
#                                                                         #
#  This program is distributed in the hope that it will be useful, but    #
#  WITHOUT ANY WARRANTY; without even the implied warranty of             #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU      #
#  General Public License for more details.                               #
#                                                                         #
###########################################################################


from PyQt4 import QtCore, QtGui
from src.br import Breakpoi
from src.co import Conso
from src.ej import Ejecutar
from src.help import HelpWindow
from src.im import Imprimir
from src.mu import Multipasos
from src.op import Opciones
from src.simplearmeditor import SimpleARMEditor
from src.tablemodelregisters import TableModelRegisters
from src.va import Valor
from ui.mainwindow import Ui_MainWindow
import os
import resources.main_rc as main_rc
import signal
import sys
from src.tablemodelmemory import TableModelMemory

__version__ = "0.1"

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

class QtArmSimMainWindow(QtGui.QMainWindow):
    "Main window of the Qt ArmSim application."
    
    # Vector que almacena el valor por defecto de las opciones del simulador
    options = [1, 0, 0, 0]

    def __init__(self, parent=None):
        
        # Call super.__init__()
        super(QtArmSimMainWindow, self).__init__()
        
        # Initialize variables
        self.fileName = ''

        # Load the user interface
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
         
        # Extends the Ui
        self.extendUi()

        # Set the application icon, title and size
        self.setWindowIcon(QtGui.QIcon(":/images/spi.bmp"))
        self.resize(800, 600)

        # Breakpoint dialog initialization
        self.br = Breakpoi(self)
        # Breakpoints list
        self.ptosrup = QtGui.QListWidget(self.br)
        
        # Console window initialization
        self.consoleWindow = Conso()
        self.consoleWindow.move(self.x() + 600, self.y())

        # Help window initialization
        self.helpWindow = HelpWindow()
        self.helpWindow.move(self.x() + 600, self.y())
        
        # Connect actions
        self.connectActions()

        # Print initial message on the Messages Window and print "Ready" on the statusBar 
        self.ui.textEditMessages.append(self.initial_message())
        self.statusBar().showMessage(self.tr("Ready"))

        # Saves the initial state of the interface
        self.state = self.saveState(1)
        

    def extendUi(self):
        "Extends the Ui with new objects and link table view with their models"
        
        # Add text editor based on QsciScintilla
        self.ui.textEditSource = SimpleARMEditor(self.ui.tabSource)
        self.ui.textEditSource.setToolTip(_fromUtf8(""))
        self.ui.textEditSource.setWhatsThis(_fromUtf8(""))
        self.ui.textEditSource.setObjectName(_fromUtf8("textEditSource"))
        self.ui.verticalLayoutSource.addWidget(self.ui.textEditSource)

        # Link tableViewRegisters with tableModelRegisters
        tableModelRegisters = TableModelRegisters()
        self.ui.tableViewRegisters.setModel(tableModelRegisters)
        self.ui.tableViewRegisters.resizeColumnsToContents()
        #self.ui.dockWidgetContentsRegisters.resize(800,100)
        #self.ui.dockWidgetRegisters.resize(800,200)

        tableModelMemory = TableModelMemory()
        self.ui.tableViewMemory.setModel(tableModelMemory)
        self.ui.tableViewMemory.resizeColumnsToContents()
        
            
    def connectActions(self):
        "Connects the actions with their correspondent methods"
        # Automatically assign actions to methods using the actions names
        signalTriggered = QtCore.SIGNAL("triggered()")
        for actionName in dir(self.ui):
            if actionName.startswith('action'):
                methodName = 'do{}'.format(actionName[6:])
                try:
                    method = getattr(self, methodName)
                except AttributeError:
                    print("Method: {} not implemented yet!".format(methodName))
                    continue
                action = getattr(self.ui, actionName)
                self.connect(action, signalTriggered, method)
        # Install event filter for dock widgets
        self.ui.dockWidgetRegisters.installEventFilter(self)
        self.ui.dockWidgetMemory.installEventFilter(self)
        self.ui.dockWidgetStack.installEventFilter(self)
        self.ui.dockWidgetMessages.installEventFilter(self)


    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.Close and isinstance(source, QtGui.QDockWidget)):
            if source is self.ui.dockWidgetRegisters:
                self.ui.actionShow_Registers.setChecked(False)
            elif source is self.ui.dockWidgetMemory:
                self.ui.actionShow_Memory.setChecked(False)
            elif source is self.ui.dockWidgetStack:
                self.ui.actionShow_Stack.setChecked(False)
            elif source is self.ui.dockWidgetMessages:
                self.ui.actionShow_Messages.setChecked(False)
        return super(QtArmSimMainWindow, self).eventFilter(source, event)

        
    def setFileName(self, fileName):
        "Sets the filename and updates the window title accordingly"
        self.fileName = fileName
        self.setWindowTitle("Qt ArmSim - {}".format(self.fileName))
    
    
    def doOpen(self):
        "Opens an ARM assembler file"
        fileName = QtGui.QFileDialog.getOpenFileName(self, self.tr("Open File"),
                                                     QtCore.QDir.currentPath(),
                                                     self.tr("ARM assembler files(*.s *.asm);;All the files(*.*)"))
        if fileName:
            self.ui.textEditSource.setText(open(fileName).read())
            self.setFileName(fileName)
            
         
    def doSafe(self):
        "Saves the current ARM assembler file"
        if self.fileName == '':
            return self.saveAs()
        else:
            return self.saveFile(self.fileName)


    def doSave_As(self):
        "Saves the ARM assembler file with a new specified name"
        fileName = self.fileName
        if fileName =='':
            fileName = os.path.join(QtCore.QDir.currentPath(), self.tr("untitled.s"))
        fileName = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save File"), fileName, self.tr("ARM assembler file(*.s *.asm)"))
        if fileName == '':
            return False
        else:
            return self.saveFile(fileName)


    def saveFile(self, fileName):
        "Saves the contents of the source editor on the given file name"
        # Llamada que crea un fichero con el nombre que pasamos como argumento
        file = QtCore.QFile(fileName)
        if not file.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, self.tr("Error"),
                    self.tr("No se puede escribir %1:\n%2.").arg(fileName).arg(file.errorString()))
            return False
        
        # Escribimos la información de los distintos paneles en el fichero .out
        #----------------------------------------------- a = QtCore.QByteArray()
        #--------------------------------- a.insert(0, self.tr("Regitros:\n\n"))
        #--------------------- a.insert (a.size(), self.registers.toPlainText())
        #--------------- a.insert(a.size(), self.tr("\nSegmento de Datos:\n\n"))
        #--------------------------- a.insert(a.size(), self.data.toPlainText())
        #--------------- a.insert(a.size(), self.tr("\nSegmento de Texto:\n\n"))
        #-------------------------- a.insert(a.size(), self.texto.toPlainText())
        #---------------------- a.insert(a.size(), self.tr("\n\nMensajes:\n\n"))
        #--------------------------- a.insert(a.size(), self.mens.toPlainText())
        #----------------------- a.insert(a.size(), self.tr("\n\nConsola:\n\n"))
        #-------------- a.insert(a.size(), self.consoleWindow.consolEdit.text())
        #--------------------------------------------------------- file.write(a)

        self.statusBar().showMessage(self.tr("File saved"), 2000)
        self.setFileName(fileName)
        return True
    
    def doQuit(self):
        "Quits the program"
        self.close()
        

    def doShow_Statusbar(self):
        if self.ui.statusBar.isVisible():
            self.ui.statusBar.setHidden(True)
            self.ui.actionShow_Statusbar.setChecked(False)
        else:
            self.ui.statusBar.setVisible(True)
            self.ui.actionShow_Statusbar.setChecked(True)


    def doShow_Toolbar(self):
        if self.ui.toolBar.isVisible():
            self.ui.toolBar.setHidden(True)
            self.ui.actionShow_Toolbar.setChecked(False)
        else:
            self.ui.toolBar.setVisible(True)
            self.ui.actionShow_Toolbar.setChecked(True)
    
    
    def doShow_Registers(self):
        "Shows or hides the registers dock widget"
        if self.ui.dockWidgetRegisters.isVisible():
            self.ui.dockWidgetRegisters.setHidden(True)
            self.ui.actionShow_Registers.setChecked(False)
        else:
            self.ui.dockWidgetRegisters.setVisible(True)
            self.ui.actionShow_Registers.setChecked(True)
            

    def doShow_Memory(self):
        "Shows or hides the Memory dock widget"
        if self.ui.dockWidgetMemory.isVisible():
            self.ui.dockWidgetMemory.setHidden(True)
            self.ui.actionShow_Memory.setChecked(False)
        else:
            self.ui.dockWidgetMemory.setVisible(True)
            self.ui.actionShow_Memory.setChecked(True)
            

    def doShow_Stack(self):
        "Shows or hides the Stack dock widget"
        if self.ui.dockWidgetStack.isVisible():
            self.ui.dockWidgetStack.setHidden(True)
            self.ui.actionShow_Stack.setChecked(False)
        else:
            self.ui.dockWidgetStack.setVisible(True)
            self.ui.actionShow_Stack.setChecked(True)
            
    def doShow_Messages(self):
        "Shows or hides the Messages dock widget"
        if self.ui.dockWidgetMessages.isVisible():
            self.ui.dockWidgetMessages.setHidden(True)
            self.ui.actionShow_Messages.setChecked(False)
        else:
            self.ui.dockWidgetMessages.setVisible(True)
            self.ui.actionShow_Messages.setChecked(True)
            
    ## Acción asociada a actionOpciones2
    #
    # Abre el diálogo de opciones del Spim
    def opciones_2(self):
        opc = Opciones(self)
        opc.exec_()

    ## Acción asociada a actionImprimir
    #
    # Abre el diálogo que permite imprimir valores en el panel de mensajes
    def imp(self):
        im = Imprimir(self)
        im.exec_()

    
    ## Acción asociada a actionMensajes
    #
    # Función para ocultar o hacer visible el panel de mensajes
    def mensajes(self):
        #=======================================================================
        # if self.dock4.isVisible():
        #     self.dock4.setVisible(False)
        #     self.ui.actionMensajes.setChecked(0)
        # else:
        #     self.dock4.setVisible(True)
        #     self.ui.actionMensajes.setChecked(1)
        #=======================================================================
        pass

    
    ## Acción asociada a actionRegistros
    #
    # Función para ocultar o hacer visible el panel de registros
    def registros(self):
        #=======================================================================
        # if self.dock1.isVisible():
        #     self.dock1.setVisible(False)
        #     self.ui.actionRegistros.setChecked(0)
        # else:
        #     self.dock1.setVisible(True)
        #     self.ui.actionRegistros.setChecked(1)
        #=======================================================================
        pass

    ## Acción asociada a actionSegmento_de_texto
    #
    # Función para ocultar o hacer visible el panel de segmento de texto
    def segmento_de_texto(self):
        if self.dock3.isVisible():
            self.dock3.setVisible(False)
            self.ui.actionSegmento_de_texto.setChecked(0)
        else:
            self.dock3.setVisible(True)
            self.ui.actionSegmento_de_texto.setChecked(1)

        
    ## Acción asociada a actionSegmento_de_datos
    #
    # Función para ocultar o hacer visible el panel de segmento de datos
    #def segmento_de_datos(self):
    
    ## Acción asociada a actionEjecutar
    #
    # Abre el diálogo de parámetros de ejecución del simulador
    def ejecutar(self):
        eje = Ejecutar(self)
        eje.exec_()
    
    ## Acción asociada a actionEjecuci_n_multipasos
    #
    # Abre el diálogo para seleccionar el número de pasos a ejecutar
    def ejecutar_multi(self):
        ej = Multipasos(self)
        ej.exec_()

        
    ## Acción asociada a actionEjecuci_n_pasos
    def ejecutar_single(self):
        self.mens.append(self.tr("Ejecutando instrucción"))
        
    ## Acción asociada a actionPunto_de_corte
    #
    # Abre el diálogo que permite añadir y suprimir puntos de ruptura
    def cortes(self):
        self.br.layout.addWidget(self.ptosrup)
        self.br.exec_()

    ## Acción asociada a actionFijar_valor
    #
    # Abre el diálogo que permite asignar un valor a un registro
    def fijar_valor(self):
        va = Valor(self)
        va.exec_()
    

    ## Acción asociada al botón de parar ejecución de la barra de herramientas
    #
    # Función para parar la ejecución en curso
    def parar(self):
        para = QtGui.QMessageBox.warning(self, self.tr("Detener ejecución"),
                            self.tr("Quieres detener la ejecución del programa?"), QtGui.QMessageBox.Yes | QtGui.QMessageBox.Default, QtGui.QMessageBox.No | QtGui.QMessageBox.Escape)
                            
    ## Acción asociada a actionBarra_de_herramientas
    #
    # Función para ocultar o hacer visible la barra de herramientas
            
    ## Acción asociada a actionBarra_de_estado
    #
    # Función para ocultar o hacer visible la barra de estado 
    def barraE(self):
        if self.ui.statusbar.isVisible():
            self.ui.statusbar.setHidden(1)
            self.actionBarra_de_estado.setChecked(0)
        else:
            self.ui.statusbar.setVisible(1)
            self.actionBarra_de_estado.setChecked(1)
    
    ## Acción asociada a actionLimpiar_Consola
    #
    # Función para limpiar la consola
    def conso_clear(self):
        self.mens.append(self.tr("Limpiando consola"))
        self.consoleWindow.consolEdit.clear()
        
    ## Acción asociada a actionVista_inicial
    #
    # Función para restaurar la disposición por defecto de la ventana principal
    def recuperar(self):
        if self.ui.statusbar.isVisible() != True:
            self.ui.statusbar.setVisible(1)
            self.actionBarra_de_estado.setChecked(1)
        if self.dock1.isVisible() != True:
            self.dock1.setVisible(1)
        if self.dock2.isVisible() != True:
            self.dock2.setVisible(1)
        if self.dock3.isVisible() != True:
            self.dock3.setVisible(1)
        if self.dock4.isVisible() != True:
            self.dock4.setVisible(1)
        self.restoreState(self.state, 1)
        
        
    ## Acción asociada a actionLimpiar_registros
    #
    # Función para poner todos los registros a 0
    def limpiar_registros(self):
        self.mens.append(self.tr("Limpiando registros"))
     
    ## Acción asociada a actionRecargar
    #
    # Función para volver a ensamblar el archivo actual en el simulador
    def recargar(self):
        self.mens.append(self.tr("Recargando el archivo actual"))
        
        
    ## Acción asociada a actionReinicializar
    #
    # Función para restaurar el contenido de los registros y la memoria
    def reinicializar(self):
        self.mens.append(self.tr("Restaurando contenidos de registros y memoria"))
        
    def closeEvent(self, event):
        "Called when the main window has been closed. Performs clean up actions."
        self.consoleWindow.close()
        self.helpWindow.close()
        event.accept()

    ## Método para redefinir los eventos que se producen tras restaurar la ventana principal
    #
    # Se restauran todas las ventanas abiertas de la aplicación
    def showEvent(self, event):
        event.accept()
        if self.consoleWindow.isVisible() == True:
            self.consoleWindow.showNormal()
        if self.helpWindow.isVisible() == True:
            self.helpWindow.showNormal()
    ## Método para redefinir los eventos que se producen tras minimizar la ventana principal
    #
    # Se minimizan todas las ventanas abiertas de la aplicación
    def hideEvent(self, event):
        event.accept()
        if self.consoleWindow.isVisible() == True:
            self.consoleWindow.showMinimized()
        if self.helpWindow.isVisible() == True:
            self.helpWindow.showMinimized()


    ## Acción asociada a actionTemas_de_ayuda
    #
    # Activa el modo ¿Qué es esto?
    def whats_This(self):
        "Activates the What's This? mode"
        QtGui.QWhatsThis.enterWhatsThisMode()
        self.whatsThisButton.setChecked(1)


    def initial_message(self):
        return "<b>Qt ArmSim " + self.tr("version") + " " + __version__ + "</b><br></br>\n" + \
                 "(c) 2014 Sergio Barrachina Mir<br></br>\n" + \
                 self.tr("Based on the graphical frontend for Spim developed by Gloria Edo Piñana on 2008.<br></br>\n")

    def about_message(self):
        return self.tr("Version") + " " + __version__ + "\n\n" + \
                 "(c) 2014 Sergio Barrachina Mir\n\n" + \
                 self.tr("Based on the graphical frontend for Spim\ndeveloped by Gloria Edo Piñana on 2008.")
    
    def about_Qt_ArmSim(self):
        "About Qt ArmSim dialog"
        QtGui.QMessageBox.about(self,
                                self.tr("About Qt ArmSim"),
                                self.about_message(),
                                )

    def about_ArmSim(self):
        "About Qt ArmSim dialog"
        QtGui.QMessageBox.about(self,
                                self.tr("About ArmSim"),
                                self.tr("Version") + " " + "0.1" + "\n\n" +
                                "(c) 2014 Germán Fabregat Llueca")
        
    ## Acción asociada a actionAyuda
    #
    # Abre una nueva ventana para consultar los distintos temas de ayuda sobre la aplicación
    def help(self):
        #self.helpWindow = HelpWindow()
        self.helpWindow.setVisible(1)
    



    

        
if __name__ == "__main__":
    # Make CTRL+C work
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    # Create the application
    app = QtGui.QApplication(sys.argv)
    # Create the main window and show it
    mainwindow = QtArmSimMainWindow()
    mainwindow.show()
    # Enter the mainloop of the application
    sys.exit(app.exec_())
