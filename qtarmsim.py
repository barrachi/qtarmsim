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


import os
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
from src.mu import Multipasos
from src.op import Opciones
from src.simplearmeditor import SimpleARMEditor
from src.tablemodelmemory import TableModelMemory
from src.treemodelregisters import TreeModelRegisters
from src.va import Valor
from ui.mainwindow import Ui_MainWindow


__version__ = "0.1"

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

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
        
        # Link tableViewRegisters with tableModelRegisters
        self.treeModelRegisters = TreeModelRegisters()
        self.ui.treeViewRegisters.setModel(self.treeModelRegisters)
        #self.ui.treeViewRegisters.resizeColumnsToContents()

        # tableModelMemory
        self.tableModelMemory = TableModelMemory()

        #=======================================================================
        # # Link tableViewMemory with tableModelMemory
        # tableModelMemory = TableModelMemory()
        # self.ui.tableViewMemory.setModel(tableModelMemory)
        # self.ui.tableViewMemory.resizeColumnsToContents()
        # # Link tableViewStack with tableModelMemory
        # tableModelStack = TableModelMemory()
        # self.ui.tableViewStack.setModel(tableModelStack)
        # self.ui.tableViewStack.resizeColumnsToContents()
        #=======================================================================
        
            
    def readSettings(self):
        "Reads the settings from the settings file"
        self.settings = QtCore.QSettings("UJI", "QtARMSim")
        self.restoreGeometry(self.settings.value("geometry", self.defaultGeometry()))
        self.restoreState(self.settings.value("windowState", self.initialWindowState))
        self.command_path = os.path.dirname(os.path.realpath(__file__))
        self.armsim_command = self.settings.value("ARMSimCommand", os.path.join(self.command_path, "armsim", "server.rb"))
        self.armsim_port = self.settings.value("ARMSimPort", 8010)
        
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
        # self.ui.tableViewMemory.installEventFilter(self)

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.Close and isinstance(source, QtGui.QDockWidget)):
            if source is self.ui.dockWidgetRegisters:
                self.ui.actionShow_Registers.setChecked(False)
            elif source is self.ui.dockWidgetMemory:
                self.ui.actionShow_Memory.setChecked(False)
            elif source is self.ui.dockWidgetMessages:
                self.ui.actionShow_Messages.setChecked(False)
        if (event.type() == QtCore.QEvent.LayoutRequest and isinstance(source, QtGui.QTableView)): 
            source.resizeColumnsToContents()
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
    # Run menu actions
    #################################################################################

    def doStep(self):
        if not self.armsim_current_port:
            return
        self.tableModelRegisters.stepHistory()
        self.tableModelMemory.stepHistory()
        response = self.simulator.getExecuteStep()
        self.ui.textEditMessages.append(response.assembly_line)
        for (reg_number, reg_value) in response.registers:
            self.tableModelRegisters.setRegister(reg_number, reg_value)
        for (hex_address, hex_byte) in response.memory:
            self.tableModelMemory.setByte(hex_address, hex_byte)
        if response.errmsg:
            self.ui.textEditMessages.append("<b>The following error has occurred:</b>")
            self.ui.textEditMessages.append("\n".join(response.errmsg))
        self.highlight_pc_line()
        
        
    def highlight_pc_line(self):
        PC = self.tableModelRegisters.getRegister(15)
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
        if self.armsim_current_port:
            self.mysocket.send_line("EXIT")
        # Close connection and socket
        self.mysocket.close_connection()
        self.mysocket.close_socket()
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
        # Remove previous memory pages on memory toolBox
        for i in range(self.ui.toolBoxMemory.count()):
            self.ui.toolBoxMemory.removeItem(i)
        # Set courier font
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Courier"))
        
        model = QtGui.QStandardItemModel()
        item0 = QtGui.QStandardItem("1 first item");
        item1 = QtGui.QStandardItem("2 second item");
        item3 = QtGui.QStandardItem("3 third item");
        item4 = QtGui.QStandardItem("4 forth item");
        item5 = QtGui.QStandardItem("5");
        item6 = QtGui.QStandardItem("6");
        item7 = QtGui.QStandardItem("7");
        
        model.appendRow(item0);
        item0.appendRow([item3, item5]);
        item0.appendRow([item4, item6]);
        item1.appendRow([item7, ])
        model.appendRow(item1);
        
        model.setColumnCount(2)
        
        page = QtGui.QWidget()
        vertical_layout = QtGui.QVBoxLayout(page)
        treeView = QtGui.QTreeView(page)
        treeView.setModel(model)
        treeView.setRootIndex(model.indexFromItem(item1))
        
        vertical_layout.addWidget(treeView)
        self.ui.toolBoxMemory.addItem(page, _fromUtf8("Yep"))
        
        return
   
    
        # Process memory info
        self.tableModelMemory.clear()
        for (memtype, hex_start, hex_end) in self.simulator.getMemoryBanks():
            # Toolbox page and vertical layout
            page = QtGui.QWidget()
            vertical_layout = QtGui.QVBoxLayout(page)
            # TableView
            tableView = QtGui.QTableView(page)
            tableView.installEventFilter(self)
            tableView.setFont(font)
            tableView.setFrameShape(QtGui.QFrame.NoFrame)
            tableView.setFrameShadow(QtGui.QFrame.Plain)
            tableView.setLineWidth(0)
            tableView.setShowGrid(False)
            tableView.setAlternatingRowColors(True)
            tableView.horizontalHeader().setVisible(False)
            tableView.verticalHeader().setVisible(True)
            tableModel = TableModelMemory(self.tableModelMemory)
            tableView.setModel(tableModel)
            tableModel.appendMemoryRange(memtype, hex_start, hex_end)
            # Add tableView to the vertical layout, and the page to the toolBox 
            vertical_layout.addWidget(tableView)
            self.ui.toolBoxMemory.addItem(page, _fromUtf8("{} {}".format(memtype, hex_start)))
            # Dump memory from ARMSim
            start = int(hex_start, 16)
            end = int(hex_end, 16)
            nbytes = int( (end - start)/4 )*4
            word = []
            words = []
            for (address, byte) in self.simulator.getMemory(hex_start, nbytes):  # @UnusedVariable address
                word.append(byte[2:])
                if len(word) == 4:
                    words.append('0x{}{}{}{}'.format(word[3], word[2], word[1], word[0]))
                    word.clear()
            # Form a word from the last 1-3 bytes read, if any 
            if len(word):
                while len(word) < 4:
                    word.append('00')
                words.append('0x{}{}{}{}'.format(word[3], word[2], word[1], word[0]))
            # load words in table model
            tableModel.loadWords(words)
            # if memtype == ROM then load the program into the ARMSim tab
            if memtype == 'ROM':
                ninsts = int(nbytes/2) # Maximum number of instructions in the given ROM
                armsim_lines = self.simulator.getDisassemble(hex_start, ninsts)
                self.ui.textEditARMSim.setText('\n'.join(armsim_lines))
                self.highlight_pc_line()
        self.tableModelMemory.clearHistory()


    def connectToARMSim(self):
        if not os.path.exists(self.armsim_command):
            QtGui.QMessageBox.warning(self, self.tr("ARMSim not found"),
                    self.tr("ARMSim command not found.\n\n"
                            "Please go to the 'Configure QtARMSim' entry\n"
                            "on the Window menu, and set its path.\n"))
            return False
        self.simulator = ARMSimConnector(self.armsim_command, self.armsim_port)
        errmsg = self.simulator.connect()
        if errmsg:
            QtGui.QMessageBox.warning(self, self.tr("Connection to ARMSim failed"), "\n{}\n".format(errmsg))
            return False
        self.ui.textEditMessages.append("<b>ArmSim version info</b><br/>")
        self.ui.textEditMessages.append(self.simulator.getVersion())
        self.ui.textEditMessages.append("<br/>")
        return True
            
def main():
    # Make CTRL+C work
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    # Create the application
    app = QtGui.QApplication(sys.argv)
    # Create the main window and show it
    main_window = QtARMSimMainWindow()
    main_window.show()
    if main_window.connectToARMSim():
        main_window.updateRegisters()
        main_window.updateMemory()
    # Enter the mainloop of the application
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()
