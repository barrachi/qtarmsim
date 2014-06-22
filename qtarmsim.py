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
import time
from src.mysocket import MySocket
import subprocess

__version__ = "0.1"

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


class QtArmSimMainWindow(QtGui.QMainWindow):
    "Main window of the Qt ArmSim application."
    
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
        # Breakpoint dialog initialization
        self.br = Breakpoi(self)
        # Breakpoints list
        self.ptosrup = QtGui.QListWidget(self.br)
        # Console and help windows initialization
        self.consoleWindow = Conso()
        self.helpWindow = HelpWindow()
        # Connect actions
        self.connectActions()
        # Print welcome message on the Messages Window and "Ready" on the statusBar 
        self.ui.textEditMessages.append(self.welcome_message())
        self.statusBar().showMessage(self.tr("Ready"))
        # Saves the initial WindowState of the interface
        self.initialWindowState = self.saveState()
        # Read the settings
        self.readSettings()
        # Create socket and set current_armsim_port to None
        self.mysocket = MySocket()
        self.armsim_pid = None
        self.armsim_current_port = None
        self.armsim_about_message = ""

    def show(self, *args, **kwargs):
        "Method called when the window is ready to be shown"
        super(QtArmSimMainWindow, self).show(*args, **kwargs)
        # restore actions have to be called after the window is shown
        self.checkShowActions()
        
        
    def extendUi(self):
        "Extends the Ui with new objects and links the table views with their models"
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
        # Link tableViewMemory with tableModelMemory
        tableModelMemory = TableModelMemory()
        self.ui.tableViewMemory.setModel(tableModelMemory)
        self.ui.tableViewMemory.resizeColumnsToContents()
        
            
    def readSettings(self):
        "Reads the settings from the settings file"
        self.settings = QtCore.QSettings("UJI", "QtArmSim")
        self.restoreGeometry(self.settings.value("geometry", self.defaultGeometry()))
        self.restoreState(self.settings.value("windowState", self.initialWindowState))
        self.command_path = os.path.dirname(os.path.realpath(__file__))
        self.armsim_command = self.settings.value("armSimCommand", os.path.join(self.command_path, "armsim", "server.rb"))
        self.armsim_port = self.settings.value("armSimPort", 8010)
        
    def defaultGeometry(self):
        "Resizes main window to 800x600 and returns the geometry"
        self.resize(800, 600)
        return self.saveGeometry()
        
    def checkShowActions(self):
        "Modifies the checked state of the show/hide actions depending on their widgets visibility"
        self.ui.actionShow_Statusbar.setChecked(self.ui.statusBar.isVisible())
        self.ui.actionShow_Toolbar.setChecked(self.ui.toolBar.isVisible())
        self.ui.actionShow_Registers.setChecked(self.ui.dockWidgetRegisters.isVisible())
        self.ui.actionShow_Memory.setChecked(self.ui.dockWidgetMemory.isVisible())
        self.ui.actionShow_Stack.setChecked(self.ui.dockWidgetStack.isVisible())
        self.ui.actionShow_Messages.setChecked(self.ui.dockWidgetMessages.isVisible())
        
 
    #################################################################################
    # Actions and events
    #################################################################################

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

        
    #################################################################################
    # File menu actions
    #################################################################################

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
            
         
    def doSave(self):
        "Saves the current ARM assembler file"
        if self.fileName == '':
            return self.doSave_As()
        else:
            return self.saveFile(self.fileName)


    def doSave_As(self):
        "Saves the ARM assembler file with a new specified name"
        fileName = self.fileName
        if fileName == '':
            fileName = os.path.join(QtCore.QDir.currentPath(), self.tr("untitled.s"))
        fileName = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save File"), fileName, self.tr("ARM assembler file(*.s *.asm)"))
        if fileName == '':
            return False
        else:
            return self.saveFile(fileName)


    def saveFile(self, fileName):
        "Saves the contents of the source editor on the given file name"
        asm_file = QtCore.QFile(fileName)
        if not asm_file.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, self.tr("Error"),
                    self.tr("Could not write to file '{0}':\n{1}.").format(fileName, asm_file.errorString()))
            return False
        asm_file.write(self.ui.textEditSource.text())
        asm_file.close()
        self.statusBar().showMessage(self.tr("File saved"), 2000)
        self.setFileName(fileName)
        return True
    
    def doQuit(self):
        "Quits the program"
        self.close()
        

    #################################################################################
    # Settings menu actions
    #################################################################################
    
    def _doShow(self, widget, action):
        if widget.isVisible():
            widget.setHidden(True)
        else:
            widget.setVisible(True)
        action.setChecked(widget.isVisible())
        
    def doShow_Statusbar(self):
        "Shows or hides the status bar"
        self._doShow(self.ui.statusBar, self.ui.actionShow_Statusbar)

    def doShow_Toolbar(self):
        "Shows or hides the tool bar"
        self._doShow(self.ui.toolBar, self.ui.actionShow_Toolbar)
    
    def doShow_Registers(self):
        "Shows or hides the registers dock widget"
        self._doShow(self.ui.dockWidgetRegisters, self.ui.actionShow_Registers)

    def doShow_Memory(self):
        "Shows or hides the Memory dock widget"
        self._doShow(self.ui.dockWidgetMemory, self.ui.actionShow_Memory)

    def doShow_Stack(self):
        "Shows or hides the Stack dock widget"
        self._doShow(self.ui.dockWidgetStack, self.ui.actionShow_Stack)
            
    def doShow_Messages(self):
        "Shows or hides the Messages dock widget"
        self._doShow(self.ui.dockWidgetMessages, self.ui.actionShow_Messages)

    def doRestore_Default_Layout(self):
        "Restores the initial layout"
        self.restoreState(self.initialWindowState)
        # status bar is not automatically restored, restore it manually
        self.ui.statusBar.setVisible(True)
        self.checkShowActions()
        
            
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
                            
    
    ## Acción asociada a actionLimpiar_Consola
    #
    # Función para limpiar la consola
    def conso_clear(self):
        self.mens.append(self.tr("Limpiando consola"))
        self.consoleWindow.consolEdit.clear()


        
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
        "Called when the main window has been closed. Saves state and performs clean up actions."
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        # Close connection and socket
        self.mysocket.close_connection()
        self.mysocket.close_socket()
        # Close windows
        self.consoleWindow.close()
        self.helpWindow.close()
        event.accept()


    def showEvent(self, event):
        "Method called when the show event is received"
        super(QtArmSimMainWindow, self).showEvent(event)
        if self.consoleWindow.isVisible() == True:
            self.consoleWindow.showNormal()
        if self.helpWindow.isVisible() == True:
            self.helpWindow.showNormal()
            
    def hideEvent(self, event):
        "Method called when the hide event is received, minimizes the other app windows"
        super(QtArmSimMainWindow, self).hideEvent(event)
        if self.consoleWindow.isVisible() == True:
            self.consoleWindow.showMinimized()
        if self.helpWindow.isVisible() == True:
            self.helpWindow.showMinimized()


    def doWhats_This(self):
        "Activates the What's This? mode"
        QtGui.QWhatsThis.enterWhatsThisMode()


    def welcome_message(self):
        return "<b>Qt ArmSim " + self.tr("version") + " " + __version__ + "</b><br></br>\n" + \
                 "(c) 2014 Sergio Barrachina Mir<br></br>\n" + \
                 self.tr("Based on the graphical frontend for Spim developed by Gloria Edo Piñana on 2008.<br></br>\n")

    def about_message(self):
        return self.tr("Version") + " " + __version__ + "\n\n" + \
                 "(c) 2014 Sergio Barrachina Mir\n\n" + \
                 self.tr("Based on the graphical frontend for Spim\ndeveloped by Gloria Edo Piñana on 2008.")
    
    def doAbout_Qt_ArmSim(self):
        "Shows the About Qt ArmSim dialog"
        QtGui.QMessageBox.about(self,
                                self.tr("About Qt ArmSim"),
                                self.about_message(),
                                )

    def doAbout_ArmSim(self):
        "Shows the About ArmSim dialog"
        QtGui.QMessageBox.about(self,
                                self.tr("About ArmSim"),
                                self.armsim_about_message)
        
    def doHelp(self):
        "Shows the Help window"
        self.helpWindow.setVisible(True)

    
    #################################################################################
    # Communication with ArmSim
    #################################################################################

    def read_armsim_version(self):
        self.mysocket.sock.settimeout(2.0) # Set timeout to 2 seconds
        self.mysocket.send_line("SHOW VERSION")
        line = ''
        armsim_version_lines = []
        while line != 'EOF':
            line = self.mysocket.receive_line()
            armsim_version_lines.append(line)
        if line != 'EOF': # timeout occurred
            return ""
        else:
            self.armsim_about_message = "\n".join(armsim_version_lines[:-1])
            return self.armsim_about_message
    
    def connectToArmSim(self):
        if not os.path.exists(self.armsim_command):
            QtGui.QMessageBox.warning(self, self.tr("ArmSim not found"),
                    self.tr("ArmSim command not found.\n\n"
                            "Please go to the 'Configure QtArmSim' entry\n"
                            "on the Window menu, and set its path.\n"))
            return False
        # Search if armsim is already listening in a port in the range [self.armsim_port, self.armsim_port+10[
        current_port = None
        for port in range(self.armsim_port, self.armsim_port+10):
            try:
                self.mysocket.connect_to(port)
            except ConnectionRefusedError:
                continue
            if self.read_armsim_version():
                current_port = port
                break
        # If no current port, then launch armsim and connect to it
        if not current_port:
            self.armsim_pid = subprocess.Popen(["ruby",
                                                self.armsim_command, 
                                                str(self.armsim_port)],
                                               cwd = os.path.dirname(self.armsim_command)
                                               ).pid
            if self.armsim_pid:
                chances = 3
                while chances:
                    try:
                        self.mysocket.connect_to(self.armsim_port)
                        break
                    except ConnectionRefusedError:
                        # Sleep half a second while the server gets ready
                        time.sleep(.5)
                        chances -= 1
                if chances == 0:
                    QtGui.QMessageBox.warning(self, self.tr("Connection Refused"),
                                              self.tr("\nArmSim refused to open a connection at the port {}.\n").format(self.armsim_port))
                    return False
                if self.read_armsim_version():
                    current_port = port
        # If current port
        if current_port:
            self.armsim_current_port = current_port
            self.ui.textEditMessages.append("<b>ArmSim version info</b><br/>")
            self.ui.textEditMessages.append(self.armsim_about_message)
            self.ui.textEditMessages.append("<br/>")
            return True
        else:
            return False

        #=======================================================================
        # numFiles = 5
        # progress = QtGui.QProgressDialog("Copying files...", "Abort Copy", 0, numFiles, self)
        # progress.setWindowModality(QtCore.Qt.WindowModal)
        # for i in range(numFiles):
        #     progress.setValue(i)
        #     if progress.wasCanceled():
        #         break
        #     time.sleep(1)
        #     # ... copy one file
        # progress.setValue(numFiles)
        #=======================================================================
            
def main():
    # Make CTRL+C work
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    # Create the application
    app = QtGui.QApplication(sys.argv)
    # Create the main window and show it
    mainwindow = QtArmSimMainWindow()
    mainwindow.show()
    mainwindow.connectToArmSim()
    # Enter the mainloop of the application
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()
