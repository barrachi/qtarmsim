# -*- coding: utf-8 -*-

###########################################################################
#                                                                         #
#  This file is part of Qt ARMSim.                                        #
#                                                                         #
#  Qt ARMSim is free software: you can redistribute it and/or modify      #
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

from PyQt4 import QtCore, QtGui
from PyQt4.Qsci import QsciScintilla

from .version import __version__
from .comm.armsimconnector import ARMSimConnector
from .model.memorymodel import MemoryModel
from .model.registersmodel import RegistersModel
from .res import main_rc
from .ui.mainwindow import Ui_MainWindow
from .widget.simplearmeditor import SimpleARMEditor
from .window.br import Breakpoi
from .window.co import Conso
from .window.ej import Ejecutar
from .window.help import HelpWindow
from .window.im import Imprimir
from .window.mu import Multipasos
from .window.op import Opciones
from .window.settingsdialog import SettingsDialog
from .window.va import Valor


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
            if not fname:
                # If not found, use "server.rb" as default
                fname = "server.rb"
        self._ARMSimCommand = fname
        self._ARMSimServer = "localhost"
        self._ARMSimPort = 8010
        self._ARMSimPortMinimum = 8010
        self._ARMSimPortMaximum = 8070
        fname = ""
        for name in ["arm-none-eabi-gcc", "arm-unknown-linux-gnueabi-gcc"]:
            fname = shutil.which(name)
        fname = fname if fname else name[0]
        self._ARMGccCommand = fname
        self._ARMGccOptions = "-mcpu=cortex-m1 -mthumb -c"
        

class QtARMSimMainWindow(QtGui.QMainWindow):
    "Main window of the Qt ARMSim application."
    
    def __init__(self, parent=None):
        # Call super.__init__()
        super(QtARMSimMainWindow, self).__init__()
        # Load the user interface
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # Extends the Ui
        self.extendUi()
        # Set the file name
        self.setFileName("untitled.s")
        # Set the application icon
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
        # Set self.simulator to None
        self.simulator = None
        # Set current source code has been assembled to False
        self.source_code_assembled = False


    def show(self, *args, **kwargs):
        "Method called when the window is ready to be shown"
        super(QtARMSimMainWindow, self).show(*args, **kwargs)
        # checkFileActions checkShowActions and checkAssembledActions have to be called after the window is shown
        self.checkFileActions()
        self.checkShowActions()
        self.checkAssembledActions()
        

    def extendUi(self):
        "Extends the Ui with new objects and links the tree views with their models"
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

        
    def isSourceCodeModified(self):
        "Asks textEditSource if its contents have been modified"
        return self.ui.textEditSource.SendScintilla(QsciScintilla.SCI_GETMODIFY)
        

    def updateWindowTitle(self):
        modified_txt = self.tr(" [modified] - ") if self.isSourceCodeModified() else " - "
        title_txt = "{}{}{}".format(os.path.basename(self.file_name), modified_txt, "Qt ARMSim")
        self.setWindowTitle(title_txt)
        

    def checkFileActions(self):
        "Enables/disables actions related to file management and updates window title accordingly"
        if self.isSourceCodeModified():
            self.ui.actionSave.setEnabled(True)
            self.ui.actionSave_As.setEnabled(True)
        else:
            self.ui.actionSave.setEnabled(False)
            self.ui.actionSave_As.setEnabled(True)
        self.updateWindowTitle()

        
    def checkShowActions(self):
        "Modifies the checked state of the show/hide actions depending on their widgets visibility"
        self.ui.actionShow_Statusbar.setChecked(self.ui.statusBar.isVisible())
        self.ui.actionShow_Toolbar.setChecked(self.ui.toolBar.isVisible())
        self.ui.actionShow_Registers.setChecked(self.ui.dockWidgetRegisters.isVisible())
        self.ui.actionShow_Memory.setChecked(self.ui.dockWidgetMemory.isVisible())
        self.ui.actionShow_Messages.setChecked(self.ui.dockWidgetMessages.isVisible())
 
        
    def checkAssembledActions(self):
        "Enables/disables actions that depend on an assembled code"
        enabled = True if self.source_code_assembled else False
        #--
        self.ui.actionResume.setEnabled(enabled)
        self.ui.actionStepInto.setEnabled(enabled)
        self.ui.actionStepOver.setEnabled(enabled)
        self.ui.actionRestart.setEnabled(enabled)
        #--
        self.ui.actionRun.setEnabled(enabled)
        #--
        self.ui.actionBreakpoints.setEnabled(enabled)
        #--
        self.ui.actionReset_Registers.setEnabled(enabled)
        self.ui.actionReset_Memory.setEnabled(enabled)
        #--
        self.ui.treeViewRegisters.setEnabled(enabled)
        self.ui.treeViewMemory.setEnabled(enabled)
        self.ui.actionAbout_ARMSim.setEnabled(enabled)
        
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
        # Tab changes
        self.ui.tabWidgetCode.currentChanged.connect(self.onTabChange)
        # textEditSource modification changes 
        self.ui.textEditSource.modificationChanged.connect(self.sourceCodeChanged)
        # Install event filter for dock widgets
        self.ui.dockWidgetRegisters.installEventFilter(self)
        self.ui.dockWidgetMemory.installEventFilter(self)
        self.ui.dockWidgetMessages.installEventFilter(self)


    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.Close and isinstance(source, QtGui.QDockWidget)):
            if source is self.ui.dockWidgetRegisters:
                self.ui.actionShow_Registers.setChecked(False)
            elif source is self.ui.dockWidgetMemory:
                self.ui.actionShow_Memory.setChecked(False)
            elif source is self.ui.dockWidgetMessages:
                self.ui.actionShow_Messages.setChecked(False)
        return super(QtARMSimMainWindow, self).eventFilter(source, event)


    def onTabChange(self, tabIndex):
        if tabIndex == 1: # doAssemble()
            if self.checkCurrentFileState() == QtGui.QMessageBox.Cancel:
                self.ui.tabWidgetCode.setCurrentIndex(0)
                return
            if self.simulator and self.source_code_assembled and not self.isSourceCodeModified():
                return
            # Check if there is something to assemble
            text = self.ui.textEditSource.text().replace(" ", "").replace("\n", "")
            if len(text) < 10:
                msg =   "It seems that there is no source code to assemble.\n" \
                        "Do you really want to proceed?"
                reply = QtGui.QMessageBox.question(self, 'Empty source code?', 
                         msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                if reply == QtGui.QMessageBox.No:
                    self.ui.tabWidgetCode.setCurrentIndex(0)
                    return
            # Connect to the simulator if not already connected
            if not self.simulator or (self.simulator and not self.simulator.connected):
                if not self.connectToARMSim():
                    self.ui.tabWidgetCode.setCurrentIndex(0)
                    return
            # Send settings to ARMSim
            self.sendSettingsToARMSim()
            # Assemble file_name
            self.doAssemble()
    
    def doAssemble(self):
        # Assemble file_name
        response = self.simulator.doAssemble(self.file_name)
        if response.result == "SUCCESS":
            # Set current source code has already been assembled as True
            self.source_code_assembled = True
            self.ui.textEditMessages.append(self.tr("<b>{} assembled.</b>\n").format(self.file_name))
            # Update registers and memory
            self.updateRegisters()
            self.updateMemory()
        else:
            self.ui.textEditMessages.append(self.tr("<b>Assembly errors:</b>"))
            self.ui.textEditMessages.append(response.errmsg)
            self.ui.textEditMessages.append("")
            msg = self.tr("An error has occurred when assembling the source code.\n"\
                          "Please, see the Messages panel for more details.")
            QtGui.QMessageBox.warning(self, self.tr("Assembly Error"), msg)
            self.ui.tabWidgetCode.setCurrentIndex(0)
        self.checkAssembledActions()


    def sourceCodeChanged(self, changed):
        if changed:
            self.source_code_assembled = False
        self.checkFileActions()


    def checkCurrentFileState(self):
        if not self.isSourceCodeModified():
            return QtGui.QMessageBox.Discard
        msg =   "The document '{}' has been modified.\n" \
                "Do you want to save the changes, or discard them?".format(os.path.basename(self.file_name))
        reply = QtGui.QMessageBox.question(self, 'Close Document', 
                                           msg, QtGui.QMessageBox.Save, QtGui.QMessageBox.Discard, QtGui.QMessageBox.Cancel)
        if reply == QtGui.QMessageBox.Save:
            self.doSave()
        return reply

            
    #################################################################################
    # File menu actions
    #################################################################################

    def setFileName(self, file_name):
        "Sets the filename and updates the window title accordingly"
        self.file_name = file_name
        self.ui.textEditSource.SendScintilla(QsciScintilla.SCI_SETSAVEPOINT) # Inform QsciScintilla that the modifications have been saved
        self.checkFileActions()
        
    
    def doNew(self):
        "Creates a new untitled.s file"
        if self.checkCurrentFileState() == QtGui.QMessageBox.Cancel:
            return
        # 1) Change to tab 0
        self.ui.tabWidgetCode.setCurrentIndex(0)
        # 2) Set file name to untitled.s
        self.setFileName("untitled.s")
        # 3) Clear textEditSource
        #self.ui.textEditSource.setText("")
        self.ui.textEditSource.SendScintilla(QsciScintilla.SCI_CLEARALL)
        
        
    def doOpen(self):
        "Opens an ARM assembler file"
        if self.checkCurrentFileState() == QtGui.QMessageBox.Cancel:
            return
        file_name = QtGui.QFileDialog.getOpenFileName(self, self.tr("Open File"),
                                                     QtCore.QDir.currentPath(),
                                                     self.tr("ARM assembler files (*.s) (*.s)"))
        if file_name:
            self.readFile(file_name)
        # Change to tab 0
        self.ui.tabWidgetCode.setCurrentIndex(0)

            
    def readFile(self, file_name):
        "Reads a file. Can be called using an argument from the command line"
        if file_name:
            self.ui.textEditSource.setText(open(file_name).read())
            self.setFileName(file_name)
        
    def doSave(self):
        "Saves the current ARM assembler file"
        # Set current source code has been assembled to False
        self.source_code_assembled = False
        if self.file_name == 'untitled.s':
            return self.doSave_As()
        else:
            return self.saveFile(self.file_name)


    def doSave_As(self):
        "Saves the ARM assembler file with a new specified name"
        file_name = self.file_name
        if file_name == '':
            file_name = os.path.join(QtCore.QDir.currentPath(), self.tr("untitled.s"))
        file_name = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save File"), file_name, self.tr("ARM assembler file (*.s) (*.s)"))
        if file_name == '':
            return False
        else:
            return self.saveFile(file_name)


    def saveFile(self, file_name):
        "Saves the contents of the source editor on the given file name"
        asm_file = QtCore.QFile(file_name)
        if not asm_file.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, self.tr("Error"),
                    self.tr("Could not write to file '{0}':\n{1}.").format(file_name, asm_file.errorString()))
            return False
        asm_file.write(self.ui.textEditSource.text())
        asm_file.close()
        self.statusBar().showMessage(self.tr("File saved"), 2000)
        self.setFileName(file_name)
        return True
    
    def doQuit(self):
        "Quits the program"
        self.close()
        

    #################################################################################
    # Run menu actions
    #################################################################################

    def highlight_pc_line(self):
        PC = self.registersModel.getRegister(15)
        if self.ui.textEditARMSim.findFirst("^\[{}\]".format(PC), True, False, False, False, line=0, index=0):
            (line, index) = self.ui.textEditARMSim.getCursorPosition()  # @UnusedVariable index
            self.ui.textEditARMSim.setFocus()
            self.ui.textEditARMSim.setCursorPosition(line, 0)
            self.ui.textEditARMSim.ensureLineVisible(line)

    def _doStep(self, simulator_step_callback):
        if not self.simulator.connected:
            return
        self.registersModel.stepHistory()
        self.memoryModel.stepHistory()
        response = simulator_step_callback()
        self.ui.textEditMessages.append(response.assembly_line)
        for (reg_number, reg_value) in response.registers:
            self.registersModel.setRegister(reg_number, reg_value)
        for (hex_address, hex_byte) in response.memory:
            self.memoryModel.setByte(hex_address, hex_byte)
        if response.errmsg:
            self.ui.textEditMessages.append("<b>The following error has occurred:</b>")
            self.ui.textEditMessages.append(response.errmsg)
        self.highlight_pc_line()
        
    def doStepInto(self):
        self._doStep(self.simulator.getExecuteStepInto)
        
    def doStepOver(self):
        self._doStep(self.simulator.getExecuteStepOver)

    def doRestart(self):
        self.doAssemble()

    def doRun(self):
        response = self.simulator.getExecuteAll()
        self.ui.textEditMessages.append(response.assembly_line)
        for (reg_number, reg_value) in response.registers:
            self.registersModel.setRegister(reg_number, reg_value)
        for (hex_address, hex_byte) in response.memory:
            self.memoryModel.setByte(hex_address, hex_byte)
        if response.errmsg:
            self.ui.textEditMessages.append("<b>The following error has occurred:</b>")
            self.ui.textEditMessages.append(response.errmsg)
        self.highlight_pc_line()
                
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
                self.sendSettingsToARMSim()
            
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
        "Called when the main window is closed. Saves state and performs clean up actions."
        if self.checkCurrentFileState() == QtGui.QMessageBox.Cancel:
            event.ignore()
            return
        # Save current geometry and window state
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        # Send EXIT command to ARMSim
        if self.simulator and self.simulator.connected:
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
        self.simulator = ARMSimConnector()
        self.statusBar().showMessage(self.tr("Connecting to ARMSim..."), 2000)
        errmsg = self.simulator.connect(self.settings.value("ARMSimCommand"),
                                        self.settings.value("ARMSimServer"),
                                        int(self.settings.value("ARMSimPort")),
                                        int(self.settings.value("ARMSimPortMinimum")),
                                        int(self.settings.value("ARMSimPortMaximum")))
        if errmsg:
            QtGui.QMessageBox.warning(self, self.tr("Connection to ARMSim failed"), "\n{}\n".format(errmsg))
            return False
        self.ui.textEditMessages.append("<b>Connected to ARMSim. ARMSim version info follows.</b><br/>")
        self.ui.textEditMessages.append(self.simulator.getVersion())
        self.ui.textEditMessages.append("<br/>")
        self.statusBar().showMessage(self.tr("Connected to ARMSim at port {}").format(self.simulator.current_port), 2000)
        return True

    def sendSettingsToARMSim(self):
        for setting in [("ARMGccCommand", self.settings.value("ARMGccCommand")), ("ARMGccOptions", self.settings.value("ARMGccOptions"))]:
            errmsg = self.simulator.setSettings(setting[0], setting[1])
            if errmsg:
                QtGui.QMessageBox.warning(self, self.tr("ARMSim set setting failed"), "\n{}\n".format(errmsg))
                return False
                                        