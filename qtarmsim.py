#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###########################################################################
#  Qt ARMSim -- a Qt graphical interface to ARMSim                        #
#  ---------------------------------------------------------------------  #
#    begin                : 2014-04-02                                    #
#    copyright            : (C) 2014 by Sergio Barrachina Mir             #
#    email                : barrachi@uji.es                               #
#  ---------------------------------------------------------------------  #
#                                                                         #
# This application is based on a previous work of Gloria Edo Piñana who   #
# developed the graphical part of a Qt graphical interface to the SPIM    #
# simulator in 2008.                                                      #
#                                                                         #
###########################################################################

###########################################################################
#                                                                         #
#  This program is free software: you can redistribute it and/or modify   #
#  it under the terms of the GNU General Public License as published by   #
#  the Free Software Foundation; either version 3 of the License, or      #
#  (at your option) any later version.                                    #
#                                                                         #
#  This program is distributed in the hope that it will be useful, but    #
#  WITHOUT ANY WARRANTY; without even the implied warranty of             #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU      #
#  General Public License for more details.                               #
#                                                                         #
###########################################################################


import os
import shutil
import signal
import sys

from PyQt4 import QtCore, QtGui

import resources.main_rc as main_rc
from src.armsimconnector import ARMSimConnector
from src.br import Breakpoi
from src.co import Conso
from src.ej import Ejecutar
from src.help import HelpWindow
from src.im import Imprimir
from src.memorymodel import MemoryModel
from src.mu import Multipasos
from src.op import Opciones
from src.registersmodel import RegistersModel
from src.settingsdialog import SettingsDialog
from src.simplearmeditor import SimpleARMEditor
from src.va import Valor
from ui.mainwindow import Ui_MainWindow


__version__ = "0.1"

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

class DefaultSettings():
    
    def __init__(self):
        self._setARMSimDefaults()
    
    def value(self, name):
        return getattr(self, "_" + name)
        
    def _setARMSimDefaults(self):
        my_path = os.path.dirname(os.path.realpath(__file__))
        fname = os.path.join(my_path, "armsim", "server.rb")
        if os.path.isfile(fname):
            fname = os.path.abspath(fname)
        else:
            # If not found, search its executable in the path
            fname = shutil.which("server.rb")
            if not os.path.isfile(fname):
                # If not found, use "server.rb" as default
                fname = "server.rb"
        self._ARMSimCommand = fname
        self._ARMSimServer = "localhost"
        self._ARMSimPort = 8010
        self._ARMSimPortMinimum = 8010
        self._ARMSimPortMaximum = 8080
        fname = ""
        for name in ["arm-none-eabi-gcc", "arm-unknown-linux-gnueabi-gcc"]:
            fname = shutil.which(name)
            print("**: ", fname)
            if fname:
                break
        fname = fname if fname else name[0]
        self._ARMGccCommand = fname
        self._ARMGccOptions = "-mcpu=cortex-m1 -mthumb -c"
        

class QtARMSimMainWindow(QtGui.QMainWindow):
    "Main window of the Qt ARMSim application."
    
    def __init__(self, parent=None):
        # Call super.__init__()
        super(QtARMSimMainWindow, self).__init__()
        # Initialize variables
        self.fileName = ''
        # Load the user interface
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # Extends the Ui
        self.extendUi()
        # Set the application icon, title and size
        self.setWindowIcon(QtGui.QIcon(":/images/logo.svg"))
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


    def show(self, *args, **kwargs):
        "Method called when the window is ready to be shown"
        super(QtARMSimMainWindow, self).show(*args, **kwargs)
        # restore actions have to be called after the window is shown
        self.checkShowActions()
        
        
    def extendUi(self):
        "Extends the Ui with new objects and links the table views with their models"
        # Add text editor based on QsciScintilla to tabSource
        self.ui.textEditSource = SimpleARMEditor(self.ui.tabSource)
        self.ui.textEditSource.setObjectName(_fromUtf8("textEditSource"))
        self.ui.verticalLayoutSource.addWidget(self.ui.textEditSource)
        
        # Add text editor based on QsciScintilla to tabARMSim
        self.ui.textEditARMSim = SimpleARMEditor(self.ui.tabARMSim, disassemble=True)
        self.ui.textEditARMSim.setObjectName(_fromUtf8("textEditARMSim"))
        self.ui.verticalLayoutARMSim.addWidget(self.ui.textEditARMSim)
        
        # Link tableViewRegisters with registersModel
        self.registersModel = RegistersModel()
        self.registersModel.setupModelData()
        self.ui.treeViewRegisters.setModel(self.registersModel)
        self.ui.treeViewRegisters.expandAll()
          
        # memoryModel
        self.memoryModel = MemoryModel()
        self.ui.treeViewMemory.setModel(self.memoryModel)

            
    def readSettings(self):
        "Reads the settings from the settings file or initializes them from defaultSettings"
        self.defaultSettings = DefaultSettings()
        self.settings = QtCore.QSettings("UJI", "QtARMSim")
        self.restoreGeometry(self.settings.value("geometry", self.defaultGeometry()))
        self.restoreState(self.settings.value("windowState", self.initialWindowState))
        if not self.settings.value("ARMSimCommand"):
            self.settings.setValue("ARMSimCommand", self.defaultSettings.value("ARMSimCommand"))
        if not self.settings.value("ARMSimServer"):
            self.settings.setValue("ARMSimServer", self.defaultSettings.value("ARMSimServer"))
        if not self.settings.value("ARMSimPort"):
            self.settings.setValue("ARMSimPort", self.defaultSettings.value("ARMSimPort"))
        if not self.settings.value("ARMSimPortMinimum"):
            self.settings.setValue("ARMSimPortMinimum", self.defaultSettings.value("ARMSimPortMinimum"))
        if not self.settings.value("ARMSimPortMaximum"):
            self.settings.setValue("ARMSimPortMaximum", self.defaultSettings.value("ARMSimPortMaximum"))
        if not self.settings.value("ARMGccCommand"):
            self.settings.setValue("ARMGccCommand", self.defaultSettings.value("ARMGccCommand"))
        if not self.settings.value("ARMGccOptions"):
            self.settings.setValue("ARMGccOptions", self.defaultSettings.value("ARMGccOptions"))
            
        
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
        self.ui.dockWidgetMessages.installEventFilter(self)
        #self.ui.treeViewRegisters.installEventFilter(self)
        #self.ui.treeViewMemory.installEventFilter(self)

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.Close and isinstance(source, QtGui.QDockWidget)):
            if source is self.ui.dockWidgetRegisters:
                self.ui.actionShow_Registers.setChecked(False)
            elif source is self.ui.dockWidgetMemory:
                self.ui.actionShow_Memory.setChecked(False)
            elif source is self.ui.dockWidgetMessages:
                self.ui.actionShow_Messages.setChecked(False)
        #if (event.type() == QtCore.QEvent.LayoutRequest and isinstance(source, QtGui.QTableView)): 
        #    source.resizeColumnsToContents()
        return super(QtARMSimMainWindow, self).eventFilter(source, event)

        
    #################################################################################
    # File menu actions
    #################################################################################

    def setFileName(self, fileName):
        "Sets the filename and updates the window title accordingly"
        self.fileName = fileName
        self.setWindowTitle("Qt ARMSim - {}".format(self.fileName))
    
    
    def doOpen(self):
        "Opens an ARM assembler file"
        fileName = QtGui.QFileDialog.getOpenFileName(self, self.tr("Open File"),
                                                     QtCore.QDir.currentPath(),
                                                     self.tr("ARM assembler files (*.s) (*.s)"))
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
    # Run menu actions
    #################################################################################

    def doStep(self):
        if not self.simulator.connected:
            return
        self.registersModel.stepHistory()
        self.memoryModel.stepHistory()
        response = self.simulator.getExecuteStep()
        self.ui.textEditMessages.append(response.assembly_line)
        for (reg_number, reg_value) in response.registers:
            self.registersModel.setRegister(reg_number, reg_value)
        for (hex_address, hex_byte) in response.memory:
            self.memoryModel.setByte(hex_address, hex_byte)
        if response.errmsg:
            self.ui.textEditMessages.append("<b>The following error has occurred:</b>")
            self.ui.textEditMessages.append("\n".join(response.errmsg))
        self.highlight_pc_line()
        
        
    def highlight_pc_line(self):
        PC = self.registersModel.getRegister(15)
        if self.ui.textEditARMSim.findFirst("^\[{}\]".format(PC), True, False, False, False, line=0, index=0):
            (line, index) = self.ui.textEditARMSim.getCursorPosition()  # @UnusedVariable index
            self.ui.textEditARMSim.setFocus()
            self.ui.textEditARMSim.setCursorPosition(line, 0)
            self.ui.textEditARMSim.ensureLineVisible(line)
            
#===============================================================================
# 
#         virtual void ensureLineVisible (int line)
#         
#         virtual void QsciScintilla::setCursorPosition    (    int     line,
# int     index 
# )         [virtual, slot]
#===============================================================================


#===============================================================================
# SUCCESS
# [0x00001000] 0xB580 push {r7, lr}
# AFFECTED REGISTERS
# r13: 0x20070778
# r15: 0x00001002
# AFFECTED MEMORY
# 0x20070778: 0x00
# 0x20070779: 0x00
# 0x2007077A: 0x00
# 0x2007077B: 0x00
# 0x2007077C: 0x00
# 0x2007077D: 0x00
# 0x2007077E: 0x00
# 0x2007077F: 0x00
# EOF
#===============================================================================


    #################################################################################
    # Window menu actions
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

    def doShow_Messages(self):
        "Shows or hides the Messages dock widget"
        self._doShow(self.ui.dockWidgetMessages, self.ui.actionShow_Messages)

    def doRestore_Default_Layout(self):
        "Restores the initial layout"
        self.restoreState(self.initialWindowState)
        # status bar is not automatically restored, restore it manually
        self.ui.statusBar.setVisible(True)
        self.checkShowActions()
        
    def doConfigure_Qt_ArmSim(self):
        settings = SettingsDialog(self)
        if settings.exec_():
            if self.simulator and self.simulator.connected:
                self.simulator.sendExit()
            self.connectToARMSim() 
            
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
        QtGui.QMessageBox.warning(self, self.tr("Detener ejecución"),
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
        # Send EXIT command to ARMSim
        if self.simulator.connected:
            self.simulator.sendExit()
            self.simulator.disconnect()
        # Close windows
        self.consoleWindow.close()
        self.helpWindow.close()
        # Accept event
        event.accept()


    def showEvent(self, event):
        "Method called when the show event is received"
        super(QtARMSimMainWindow, self).showEvent(event)
        if self.consoleWindow.isVisible() == True:
            self.consoleWindow.showNormal()
        if self.helpWindow.isVisible() == True:
            self.helpWindow.showNormal()
            
    def hideEvent(self, event):
        "Method called when the hide event is received, minimizes the other app windows"
        super(QtARMSimMainWindow, self).hideEvent(event)
        if self.consoleWindow.isVisible() == True:
            self.consoleWindow.showMinimized()
        if self.helpWindow.isVisible() == True:
            self.helpWindow.showMinimized()


    def doWhats_This(self):
        "Activates the What's This? mode"
        QtGui.QWhatsThis.enterWhatsThisMode()


    def welcome_message(self):
        return "<b>Qt ARMSim " + self.tr("version") + " " + __version__ + "</b><br></br>\n" + \
                 "(c) 2014 Sergio Barrachina Mir<br></br>\n" + \
                 self.tr("Based on the graphical frontend for Spim developed on 2008 by Gloria Edo Piñana.<br></br>\n")

    def about_message(self):
        return self.tr("Version") + " " + __version__ + "\n\n" + \
                 "(c) 2014 Sergio Barrachina Mir\n\n" + \
                 self.tr("Based on the graphical frontend for Spim\ndeveloped on 2008 by Gloria Edo Piñana.")
    
    def doAbout_Qt_ARMSim(self):
        "Shows the About Qt ARMSim dialog"
        QtGui.QMessageBox.about(self,
                                self.tr("About Qt ARMSim"),
                                self.about_message(),
                                )

    def doAbout_ARMSim(self):
        "Shows the About ARMSim dialog"
        QtGui.QMessageBox.about(self,
                                self.tr("About ARMSim"),
                                self.armsim_about_message)
        
    def doHelp(self):
        "Shows the Help window"
        self.helpWindow.setVisible(True)

    
    #################################################################################
    # Communication with ARMSim
    #################################################################################

    def updateRegisters(self):
        "Updates the registers dock upon ARMSim data."
        registers_model = self.ui.treeViewRegisters.model()
        for (reg, hex_value) in self.simulator.getRegisters():
            registers_model.setRegister(reg, hex_value)
        registers_model.clearHistory()


    def updateMemory(self):
        "Updates the memory dock upon ARMSim data."
        # Process memory info
        self.memoryModel.clear()
        for (memtype, hex_start, hex_end) in self.simulator.getMemoryBanks():
            # Dump memory
            start = int(hex_start, 16)
            end = int(hex_end, 16)
            nbytes = end - start
            membytes = []
            for (hex_address, hex_byte) in self.simulator.getMemory(hex_start, nbytes):  # @UnusedVariable address
                membytes.append(hex_byte)
            self.memoryModel.appendMemoryBank(memtype, hex_start, membytes)
            #self.ui.treeViewMemory.expandAll()
            self.ui.treeViewMemory.resizeColumnToContents(0)
            self.ui.treeViewMemory.resizeColumnToContents(1)
            # if memtype == ROM then load the program into the ARMSim tab
            if memtype == 'ROM':
                ninsts = int(nbytes/2) # Maximum number of instructions in the given ROM
                armsim_lines = self.simulator.getDisassemble(hex_start, ninsts)
                self.ui.textEditARMSim.setText('\n'.join(armsim_lines))
                self.highlight_pc_line()
        self.memoryModel.clearHistory()


    def connectToARMSim(self):
        self.simulator = None
        if not os.path.isfile(self.settings.value("ARMSimCommand")):
            QtGui.QMessageBox.warning(self, self.tr("ARMSim not found"),
                    self.tr("ARMSim command not found.\n\n"
                            "Please go to 'Configure QtARMSim' and set its path.\n"))
            return False
        if not os.path.isfile(self.settings.value("ARMGccCommand")):
            QtGui.QMessageBox.warning(self, self.tr("ARM gcc not found"),
                    self.tr("ARM gcc command not found.\n\n"
                            "Please go to 'Configure QtARMSim' and set its path.\n"))
            return False
        # @todo: simulator does not take into account min and maximum ports
        self.simulator = ARMSimConnector(self.settings.value("ARMSimCommand"), int(self.settings.value("ARMSimPort")))
        errmsg = self.simulator.connect()
        if errmsg:
            QtGui.QMessageBox.warning(self, self.tr("Connection to ARMSim failed"), "\n{}\n".format(errmsg))
            return False
        self.ui.textEditMessages.append("<b>ArmSim version info</b><br/>")
        self.ui.textEditMessages.append(self.simulator.getVersion())
        self.ui.textEditMessages.append("<br/>")
        # Update registers and memory
        self.updateRegisters()
        self.updateMemory()
        return True
            
def main():
    # Make CTRL+C work
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    # Create the application
    app = QtGui.QApplication(sys.argv)
    # Create the main window and show it
    main_window = QtARMSimMainWindow()
    main_window.show()
    main_window.connectToARMSim()
    # Enter the mainloop of the application
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()
