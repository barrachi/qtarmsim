# -*- coding: utf-8 -*-

###########################################################################
#                                                                         #
#  This file is part of QtARMSim.                                         #
#                                                                         #
#  QtARMSim is free software: you can redistribute it and/or modify       #
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
import platform
import re
import shutil
import sys
import tempfile
from functools import partial
from glob import glob

import PySide2
from PySide2 import QtCore, QtGui, QtWidgets, QtPrintSupport
from PySide2.QtCore import Qt

from .comm.armsimconnector import ARMSimConnector
from .model.memorybywordproxymodel import MemoryByWordProxyModel
from .model.memorydumpproxymodel import MemoryDumpProxyModel
from .model.memorymodel import MemoryModel
from .model.registersmodel import RegistersModel
from .modulepath import module_path
from .ui.mainwindow import Ui_MainWindow
from .version import __version__
from .widget.armcodeeditor import ARMCodeEditor
from .window.connectprogressbardialog import ConnectProgressBarDialog
from .window.help import HelpWindow
from .window.preferencesdialog import PreferencesDialog
from .window.runprogressbardialog import RunProgressBarDialog
from .res import main_rc, breeze_rc  # oxygen_rc  # @UnusedImport


def _fromUtf8(s):
    return s


def which(cmd):
    """
    Searches cmd in the system PATH.

    It calls shutil.which if available (>= Python3.3), otherwise it does a naive search for the given command on the
    system PATH.

    @return: the full path to the given command.
    """
    # Try with shutil.which
    try:
        return shutil.which(cmd)
    except AttributeError:
        pass
    # Do naive search if not
    for dirname in os.get_exec_path():
        path = os.path.join(dirname, cmd)
        if os.path.exists(path):
            return os.path.realpath(path)
    return None


class DefaultSettings:

    def __init__(self):
        self._setARMSimDefaults()
        self._setDirectoryDefaults()

    def value(self, name):
        return getattr(self, "_" + name)

    def _setARMSimDefaults(self):
        fname = os.path.join(module_path, "armsim", "server.rb")
        if os.path.isfile(fname):
            fname = os.path.abspath(fname)
        else:
            # If not found, search its executable in the path
            fname = which("server.rb")
        if fname:
            ruby_cmd = "ruby" if sys.platform != "win32" else "rubyw"
            self._ARMSimCommand = "{} {}".format(ruby_cmd, os.path.basename(fname))
            self._ARMSimDirectory = os.path.dirname(fname)
        else:
            self._ARMSimCommand = ""
            self._ARMSimDirectory = ""
        self._ARMSimServer = "localhost"
        self._ARMSimPort = "8010"
        self._ARMSimUseLabels = "0"
        gcc_names = ["arm-none-eabi-gcc", "arm-unknown-linux-gnueabi-gcc", "arm-linux-gnueabi-gcc"]
        if sys.platform == "win32":
            gcc_names = ["{}.exe".format(name) for name in gcc_names]
        fname = ""
        for name in gcc_names:
            fname = which(name)
            if fname:
                break
        if not fname:  # Use bundled GNU Gcc if no native cross compiler is found
            if sys.platform == "linux":
                if platform.architecture()[0] == '64bit':
                    fname = os.path.join(module_path, "gcc-arm", "linux64", "g++_arm_none_eabi", "bin",
                                         "arm-none-eabi-gcc")
                else:
                    fname = os.path.join(module_path, "gcc-arm", "linux32", "g++_arm_none_eabi", "bin",
                                         "arm-none-eabi-gcc")
            elif sys.platform == "win32":
                fname = os.path.join(module_path, "gcc-arm", "win32", "g++_arm_none_eabi", "bin",
                                     "arm-none-eabi-gcc.exe")
            elif sys.platform == "darwin":
                fname = os.path.join(module_path, "gcc-arm", "macos", "g++_arm_none_eabi", "bin", "arm-none-eabi-gcc")
        fname = fname if fname else ""
        self._ARMGccCommand = fname
        self._ARMGccOptions = "-mcpu=cortex-m1 -mthumb -c"
        self._TerminalHistory = "SHOW VERSION"

    # noinspection PyArgumentList
    def _setDirectoryDefaults(self):
        self._LastUsedDirectory = QtCore.QDir.currentPath()


# noinspection PyArgumentList
class QtARMSimMainWindow(QtWidgets.QMainWindow):
    """Main window of the QtARMSim application."""

    def __init__(self, parent=None, debug=False, verbose=False):
        # Call super.__init__()
        super(QtARMSimMainWindow, self).__init__(parent)
        # Set debug and verbosity flags
        self.debug = debug
        self.verbose = verbose
        # Load the user interface
        self.ui = Ui_MainWindow()
        # Setup ui
        self.ui.setupUi(self)
        # Extends the Ui
        self.extendUi()
        # Set the file name to default untitled name
        self.setFileName("")
        # Set the application icon
        self.setWindowIcon(QtGui.QIcon(":/images/logo.svg"))
        # Help windows initialization
        self.helpWindow = HelpWindow()
        # Connect actions
        self.connectActions()
        # Editor flags
        self.editorFlags = {
            'selectionAvailable': False,
            'redoAvailable': False,
            'undoAvailable': False,
        }
        # Saves the initial WindowState of the interface
        self.initialWindowState = self.saveState()
        # Read the settings
        self.readSettings()
        # Set self.simulator to None
        self.simulator = None
        # Set current source code has been assembled to False
        self.current_source_code_assembled = False
        # Breakpoints
        self.breakpoints = []
        # Spinner
        self.spinnerLabel = QtWidgets.QLabel(self)
        self.spinnerLabel.setMovie(QtGui.QMovie(":/images/ajax-loader.gif"))
        self.spinnerLabel.hide()
        # Worker threads
        self.getMemoryThread = self.GetMemoryThread(self)
        self.getMemoryThread.finished.connect(self.onGetMemoryThreadFinished)
        # Print welcome message on the Messages Window and show Ready on the status bar
        self.ui.textEditMessages.append(self.welcome_message())
        self.statusBar().showMessage(self.tr("Ready"))
        # Initialize number of received lines from simulator
        self._received_lines_from_simulator = 0
        # Initialize the terminal history cursor
        self._terminal_history_cursor = 0

    def show(self, *args, **kwargs):
        """Method called when the window is ready to be shown"""
        super(QtARMSimMainWindow, self).show(*args, **kwargs)
        # updateFileActions updateShowActions and enableSimulatorActions have to be called after the window is shown
        self.updateFileActions()
        self.updateEditActions()
        self.updateShowActions()
        self.enableSimulatorActions(False)

    def extendUi(self):
        """Extends the Ui with new objects, links the views with their models,
           and puts in tabs the bottom dock widgets"""

        # Mac OS X quirks
        # @todo: check again the next on a MacOs (last time it didn't work)
        # if sys.platform == 'darwin':
        #     # Set unified title and toolbar on Mac
        #     self.setUnifiedTitleAndToolBarOnMac(True)

        # Add an ARMCodeEditor to tabSource
        self.ui.sourceCodeEditor = ARMCodeEditor(self.ui.tabSource)
        self.ui.sourceCodeEditor.setObjectName(_fromUtf8("sourceCodeEditor"))
        self.ui.sourceCodeEditor.setFocus()
        self.ui.verticalLayoutSource.addWidget(self.ui.sourceCodeEditor)

        # Clear default tabs in tabTabARMSim
        self.ui.tabTabARMSim.clear()

        # Create three simCodeEditors
        self.ui.simCodeEditors = []
        for i in range(3):
            simCodeEditor = ARMCodeEditor(self.ui.tabTabARMSim)
            simCodeEditor.setReadOnly(True)  # disassemble mode
            simCodeEditor.setObjectName(_fromUtf8("simCodeEditor{}".format(i)))
            simCodeEditor.hide()
            self.ui.simCodeEditors.append(simCodeEditor)

        # Link tableViewRegisters with registersModel
        self.registersModel = RegistersModel(self)
        self.ui.treeViewRegisters.setModel(self.registersModel)
        self.ui.treeViewRegisters.expandAll()

        # memoryModel
        self.memoryModel = MemoryModel(self)
        memoryByWordProxyModel = MemoryByWordProxyModel(self)
        memoryByWordProxyModel.setSourceModel(self.memoryModel)
        self.ui.treeViewMemory.setModel(memoryByWordProxyModel)
        self.ui.memoryLCDView.setModel(self.memoryModel, '0x20080000', 40, 6)

        # Status bar with flags indicator
        self.statusBar().addWidget(QtWidgets.QLabel(""), 10)  # No permanent
        self.flagsLabel = QtWidgets.QLabel("Flags:")
        self.statusBar().addPermanentWidget(self.flagsLabel, 0)
        self.flagsText = QtWidgets.QLabel("- - - -")
        self.flagsText.setFrameStyle(QtWidgets.QFrame.Sunken | QtWidgets.QFrame.StyledPanel)
        font = QtGui.QFont("fake font name")  # @warning: fake name needed to setStyleHint work
        font.setStyleHint(QtGui.QFont.TypeWriter)
        if not QtGui.QFontInfo(font).fixedPitch():
            font.setStyleHint(QtGui.QFont.Monospace)
        font.setPointSize(QtGui.QFont().pointSize())  # Using the system default font point size
        self.flagsText.setFont(font)
        self.flagsText.setToolTip("""
            <p><strong>Condition flag bits in the Application Processor Status Register</strong></p>
            <p>Negative: The N flag is set by an instruction if the result is negative.</p>
            <p>Zero: The Z flag is set if the result of the flag-setting instruction is zero.</p>
            <p>Carry: The C flag is set if the result of an unsigned operation overflows the 32-bit result register.</p>
            <p>oVerflow: The V flag works the same as the C flag, but for signed operations.</p>
            """)
        self.statusBar().addPermanentWidget(self.flagsText, 0)

        # Remove default tabs of self.ui.tabWidgetMemoryDump
        self.ui.tabWidgetMemoryDump.clear()

        # If not in debug mode, hide Terminal (action and dock)
        if not self.debug:
            self.ui.menu_Window.removeAction(self.ui.actionShow_Terminal)
            self.ui.dockWidgetTerminal.hide()

        # Tabify bottom dock widgets
        bottomDocks = []
        if self.dockWidgetArea(self.ui.dockWidgetMessages) == Qt.BottomDockWidgetArea:
            bottomDocks.append(self.ui.dockWidgetMessages)
        if self.dockWidgetArea(self.ui.dockWidgetMemoryDump) == Qt.BottomDockWidgetArea:
            bottomDocks.append(self.ui.dockWidgetMemoryDump)
        if self.dockWidgetArea(self.ui.dockWidgetLCDDisplay) == Qt.BottomDockWidgetArea:
            bottomDocks.append(self.ui.dockWidgetLCDDisplay)
        if self.dockWidgetArea(self.ui.dockWidgetTerminal) == Qt.BottomDockWidgetArea:
            bottomDocks.insert(0, self.ui.dockWidgetTerminal)
        if len(bottomDocks) > 1:
            self.tabifyDockWidget(bottomDocks[0], bottomDocks[1])
            if len(bottomDocks) > 2:
                for i in range(1, len(bottomDocks) - 1):
                    self.splitDockWidget(bottomDocks[i], bottomDocks[i + 1], Qt.Horizontal)
            bottomDocks[0].raise_()

        # Examples menu
        self.buildExamplesMenu(self.ui.menuExamples, os.path.join(module_path, "examples"))

    def buildExamplesMenu(self, menu, path):
        def _name_from_path(path_):
            basename = os.path.basename(path_)
            basename = basename.replace('_', ' ')
            res = re.search('[0-9]+ (.*)', basename)
            if res:
                return res.groups()[0]
            else:
                return basename
        files_or_dirs = glob(os.path.join(path, "*"))
        files_or_dirs.sort()
        for file_or_dir in files_or_dirs:
            if os.path.isdir(file_or_dir):
                new_menu = QtWidgets.QMenu(menu)
                new_menu.setTitle(QtWidgets.QApplication.translate("Examples", _name_from_path(file_or_dir), None, -1))
                self.buildExamplesMenu(new_menu, file_or_dir)
                menu.addAction(new_menu.menuAction())
            elif file_or_dir[-2:] in ('.s', '.c'):
                action = QtWidgets.QAction(self)
                action.setText(QtWidgets.QApplication.translate("Examples", _name_from_path(file_or_dir), None, -1))
                action.setData(file_or_dir)
                action.triggered.connect(partial(self.doOpenExample, action))
                menu.addAction(action)

    def readSettings(self):
        """Reads the settings from the settings file or initializes them from defaultSettings"""
        self.defaultSettings = DefaultSettings()
        self.settings = QtCore.QSettings("UJI", "QtARMSim")
        self.restoreGeometry(self.settings.value("geometry", self.defaultGeometry()))
        # @TODO: The next line does not work as expected, the central widget does not claims all the space
        # self.restoreState(self.settings.value("windowState", self.initialWindowState))
        # -----------------------------------------------------------------------------
        # Begin migration of settings versions
        # -----------------------------------------------------------------------------
        conf_version = self.settings.value("ConfVersion")
        if conf_version is None and self.settings.value("ARMSimCommand") and self.settings.value("ARMSimCommand").count(
                "ruby") == 0:
            # Migrate from version 1 to version 2
            # Version 1 -> ARMSimCommand only had the server.rb full path.
            # Version 2 -> ARMSimCommand has the full command, e.g. 'rubyw server.rb',
            #              and ARMSimDirectory has the working directory of the simulator.
            #              ARMSimPortMinimum and ARMSimPortMaximum are no longer used.
            ARMSimCommand = self.settings.value("ARMSimCommand")
            ruby_cmd = self.defaultSettings.value("ARMSimCommand").split(" ")[0]
            self.settings.setValue("ARMSimCommand", "{} {}".format(ruby_cmd, os.path.basename(ARMSimCommand)))
            self.settings.setValue("ARMSimDirectory", os.path.dirname(ARMSimCommand))
        # -----------------------------------------------------------------------------
        # End migration of settings versions
        # -----------------------------------------------------------------------------
        self.settings.setValue("ConfVersion", 3)
        for setting in (
                "ARMSimCommand", "ARMSimDirectory", "ARMSimServer", "ARMSimPort", "ARMSimUseLabels",
                "ARMGccCommand", "ARMGccOptions",
                "LastUsedDirectory", "TerminalHistory"):
            if self.settings.value(setting) is None:
                self.settings.setValue(setting, self.defaultSettings.value(setting))

    def defaultGeometry(self):
        """Resizes main window to 800x600 and returns the geometry"""
        self.resize(800, 600)
        return self.saveGeometry()

    def isSourceCodeModified(self):
        """Asks sourceCodeEditor if its contents have been modified"""
        return self.ui.sourceCodeEditor.document().isModified()

    def updateWindowTitle(self):
        modified_txt = self.tr(" [modified] - ") if self.isSourceCodeModified() else " - "
        title_txt = "{}{}{}".format(os.path.basename(self.file_name), modified_txt, "QtARMSim")
        self.setWindowTitle(title_txt)

    def updateFileActions(self):
        """Enables/disables actions related to file management and updates window title accordingly"""
        if self.isSourceCodeModified():
            self.ui.actionSave.setEnabled(True)
            self.ui.actionSave_As.setEnabled(True)
        else:
            self.ui.actionSave.setEnabled(False)
            self.ui.actionSave_As.setEnabled(True)
        self.updateWindowTitle()

    def updateEditActions(self, onSimulator=False):
        """Enables/disables actions related to edit menu"""
        self.ui.action_Undo.setEnabled(not onSimulator and self.editorFlags['undoAvailable'])
        self.ui.actionRedo.setEnabled(not onSimulator and self.editorFlags['redoAvailable'])
        self.ui.actionCut.setEnabled(not onSimulator and self.editorFlags['selectionAvailable'])
        self.ui.actionCopy.setEnabled(not onSimulator and self.editorFlags['selectionAvailable'])
        self.ui.actionPaste.setEnabled(not onSimulator and QtWidgets.QApplication.clipboard().text() != '')
        self.ui.actionSelect_All.setEnabled(not onSimulator)

    def updateShowActions(self):
        """Modifies the checked state of the show/hide actions depending on their widgets visibility"""
        self.ui.actionShow_Statusbar.setChecked(self.ui.statusBar.isVisible())
        self.ui.actionShow_Toolbar.setChecked(self.ui.toolBar.isVisible())
        self.ui.actionShow_Registers.setChecked(self.ui.dockWidgetRegisters.isVisible())
        self.ui.actionShow_Memory.setChecked(self.ui.dockWidgetMemory.isVisible())
        self.ui.actionShow_Memory_Dump.setChecked(self.ui.dockWidgetMemoryDump.isVisible())
        self.ui.actionShow_LCD_Display.setChecked(self.ui.dockWidgetLCDDisplay.isVisible())
        self.ui.actionShow_Terminal.setChecked(self.ui.dockWidgetTerminal.isVisible())
        self.ui.actionShow_Messages.setChecked(self.ui.dockWidgetMessages.isVisible())

    def enableSimulatorActions(self, onSimulator):
        """Enables/disables actions that depend on being on the simulator tab"""
        # --
        self.updateEditActions(onSimulator)
        # --
        self.ui.actionStepInto.setEnabled(onSimulator)
        self.ui.actionStepOver.setEnabled(onSimulator)
        self.ui.actionRestart.setEnabled(onSimulator)
        # --
        self.ui.actionRun.setEnabled(onSimulator)
        # --
        self.ui.treeViewRegisters.setEnabled(onSimulator)
        self.ui.treeViewMemory.setEnabled(onSimulator)
        self.ui.actionAbout_ARMSim.setEnabled(onSimulator)
        # --
        self.flagsLabel.setEnabled(onSimulator)
        self.flagsText.setEnabled(onSimulator)

    def clearBreakpoints(self):
        """
        Clears breakpoints on simulator, on simCodeEditor and on myself
        """
        if self.simulator and self.simulator.connected:
            self.simulator.clearBreakpoints()
        for simCodeEditor in self.ui.simCodeEditors:
            simCodeEditor.clearBreakpoints()
        self.breakpoints.clear()

    def startSpinner(self):
        """
        Centers the spinner on the central widget and shows it
        """
        centralwidgetQRect = self.ui.centralwidget.geometry()
        spinnerLabelQRect = self.spinnerLabel.geometry()
        spinnerLabelQRect.moveTo(QtCore.QPoint(centralwidgetQRect.x() + centralwidgetQRect.width() / 2,
                                               centralwidgetQRect.y() + centralwidgetQRect.height() / 2))
        self.spinnerLabel.setGeometry(spinnerLabelQRect)
        self.spinnerLabel.show()
        self.spinnerLabel.movie().start()
        self.repaint()

    def stopSpinner(self):
        """
        Hides the spinner
        """
        self.spinnerLabel.hide()
        self.spinnerLabel.movie().stop()

    #################################################################################
    # Actions and events
    #################################################################################

    def connectActions(self):
        """Connects the actions with their correspondent methods"""
        # Automatically assign actions to methods using the actions names
        signalTriggered = QtCore.SIGNAL("triggered()")
        for actionName in dir(self.ui):
            if actionName.startswith('action'):
                methodName = 'do{}'.format(actionName[6:])
                try:
                    method = getattr(self, methodName)
                except AttributeError:
                    if self.verbose:
                        print("Method: {} not implemented yet!".format(methodName))
                    continue
                action = getattr(self.ui, actionName)
                self.connect(action, signalTriggered, method)
        # Tab changes
        self.ui.tabWidgetCode.currentChanged.connect(self.onTabChange)
        # Clipboard changes
        QtWidgets.QApplication.clipboard().changed.connect(self.updateEditActions)
        # sourceCodeEditor modification changes
        self.ui.sourceCodeEditor.textChanged.connect(self.sourceCodeChanged)
        self.ui.sourceCodeEditor.selectionChanged.connect(self.sourceCodeSelectionChanged)
        self.ui.sourceCodeEditor.redoAvailable.connect(self.sourceCodeRedoAvailable)
        self.ui.sourceCodeEditor.undoAvailable.connect(self.sourceCodeUndoAvailable)
        # Install event filter for dock widgets
        self.ui.dockWidgetRegisters.installEventFilter(self)
        self.ui.dockWidgetMemory.installEventFilter(self)
        self.ui.dockWidgetMemoryDump.installEventFilter(self)
        self.ui.dockWidgetLCDDisplay.installEventFilter(self)
        self.ui.dockWidgetTerminal.installEventFilter(self)
        self.ui.dockWidgetMessages.installEventFilter(self)
        # Connect to self.uji.simCodeEditor set and clear breakpoint signals
        for simCodeEditor in self.ui.simCodeEditors:
            simCodeEditor.setBreakpointSignal.connect(self.setBreakpoint)
            simCodeEditor.clearBreakpointSignal.connect(self.clearBreakpoint)
        # Connect register edited on registers model to self.registerEdited
        self.registersModel.register_edited.connect(self.registerEdited)
        # Connect memory edited on memory model to self.memoryEdited
        self.memoryModel.memoryEdited.connect(self.memoryEdited)
        # Connect Terminal push button and Terminal line edit return to send line to simulator
        self.ui.pushButtonTerminal.pressed.connect(self.sendLineToSimulator)
        self.ui.lineEditTerminal.returnPressed.connect(self.sendLineToSimulator)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.Close and isinstance(source, QtWidgets.QDockWidget):
            if source is self.ui.dockWidgetRegisters:
                self.ui.actionShow_Registers.setChecked(False)
            elif source is self.ui.dockWidgetMemory:
                self.ui.actionShow_Memory.setChecked(False)
            elif source is self.ui.dockWidgetMemoryDump:
                self.ui.actionShow_Memory_Dump.setChecked(False)
            elif source is self.ui.dockWidgetLCDDisplay:
                self.ui.actionShow_LCD_Display.setChecked(False)
            elif source is self.ui.dockWidgetTerminal:
                self.ui.actionShow_Terminal.setChecked(False)
            elif source is self.ui.dockWidgetMessages:
                self.ui.actionShow_Messages.setChecked(False)
        if event.type() == QtCore.QEvent.KeyPress and source == self.ui.dockWidgetTerminal:
            if event.key() == Qt.Key_Up:
                self.ui.lineEditTerminal.setText(self.terminalHistoryUp())
                return True
            elif event.key() == Qt.Key_Down:
                self.ui.lineEditTerminal.setText(self.terminalHistoryDown())
                return True
        return super(QtARMSimMainWindow, self).eventFilter(source, event)

    def onTabChange(self, tabIndex):
        if tabIndex == 1:
            # Check if source code has to be saved or not
            if self.checkCurrentFileState() == QtWidgets.QMessageBox.Cancel:
                self.ui.tabWidgetCode.setCurrentIndex(0)
                return
            # If we have already assembled the current source code, enable the simulator actions and return
            if self.simulator and self.current_source_code_assembled and not self.isSourceCodeModified():
                self.enableSimulatorActions(True)
                return
            # If not,
            #   1) check if there is something to assemble
            text = self.ui.sourceCodeEditor.document().toPlainText().replace(" ", "").replace("\n", "")
            if len(text) < 10:
                msg = "It seems that there is no source code to assemble.\n" \
                      "Do you really want to proceed?"
                reply = QtWidgets.QMessageBox.question(self, 'Empty source code?',
                                                       msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.No:
                    self.ui.tabWidgetCode.setCurrentIndex(0)
                    return
            #   2) Assembly self.file_name
            self.doAssemble()
        else:
            self.enableSimulatorActions(False)
            self.ui.sourceCodeEditor.setFocus()

    def assembled(self, has_been_assembled):
        if has_been_assembled:
            self.current_source_code_assembled = True
            self.enableSimulatorActions(True)
            self.ui.textEditMessages.append(self.tr("<b>{} assembled.</b>\n").format(self.file_name))
        else:
            self.current_source_code_assembled = False
            self.enableSimulatorActions(False)
            self.ui.tabWidgetCode.setCurrentIndex(0)

    def doAssemble(self):
        # If not connected, connect to the simulator
        if not self.simulator or (self.simulator and not self.simulator.connected):
            if not self.connectToARMSim():
                self.assembled(False)
                return
        # Check that self.file_name exists
        if not os.path.exists(self.file_name):
            strerror = self.tr('File not found')
            QtWidgets.QMessageBox.warning(self, self.tr("Assemble File"), "{}: '{}'.".format(strerror, self.file_name))
            self.assembled(False)
            return
        # Assemble self.file_name
        response = self.simulator.doAssemble(self.file_name)
        if response.result == "SUCCESS":
            self.assembled(True)
            # Update registers and memory
            self.startSpinner()
            self.updateRegisters()
            self.updateMemory()
        else:
            self.assembled(False)
            self.ui.textEditMessages.append(self.tr("<b>Assembly errors:</b>"))
            if response.errmsg:
                self.ui.textEditMessages.append(response.errmsg)
            else:
                self.ui.textEditMessages.append(self.tr("(Something bad has happened. That's all I know.)"))
            self.ui.textEditMessages.append("")
            msg = self.tr("An error has occurred when assembling the source code.\n"
                          "Please, see the Messages panel for more details.")
            QtWidgets.QMessageBox.warning(self, self.tr("Assembly Error"), msg)

    def sourceCodeChanged(self):
        self.current_source_code_assembled = False
        self.updateFileActions()

    def sourceCodeSelectionChanged(self):
        self.editorFlags['selectionAvailable'] = self.ui.sourceCodeEditor.textCursor().selectedText() != ''
        self.updateEditActions()

    def sourceCodeRedoAvailable(self, redoAvailable):
        self.editorFlags['redoAvailable'] = redoAvailable
        self.updateEditActions()

    def sourceCodeUndoAvailable(self, undoAvailable):
        self.editorFlags['undoAvailable'] = undoAvailable
        self.updateEditActions()

    def setBreakpoint(self, lineNumber, text):
        """Sets a breakpoint on the memory address obtained from text"""
        hex_address = text.split(" ")[0][1:-1]
        errmsg = self.simulator.setBreakpoint(hex_address)
        if errmsg:
            QtWidgets.QMessageBox.warning(self, self.tr("Set breakpoint error"), errmsg)
        else:
            self.breakpoints.append(hex_address)

    def clearBreakpoint(self, lineNumber, text):
        """Clears a breakpoint from the memory address obtained from text"""
        hex_address = text.split(" ")[0][1:-1]
        errmsg = self.simulator.clearBreakpoint(hex_address)
        if errmsg:
            QtWidgets.QMessageBox.warning(self, self.tr("Clear breakpoint error"), errmsg)
        else:
            self.breakpoints.remove(hex_address)

    def registerEdited(self, reg_name, hex_value):
        errmsg = self.simulator.setRegister(reg_name, hex_value)
        if errmsg:
            QtWidgets.QMessageBox.warning(self, self.tr("Set Register Error"), errmsg)
        self.highlight_pc_line()

    def memoryEdited(self, hex_address, hex_value):
        errmsg = self.simulator.setMemory(hex_address, hex_value)
        if errmsg:
            QtWidgets.QMessageBox.warning(self, self.tr("Set Memory Error"), errmsg)

    def checkCurrentFileState(self):
        if not self.isSourceCodeModified():
            return QtWidgets.QMessageBox.Discard
        msg = "The document '{}' has been modified.\n" \
              "Do you want to save the changes?".format(os.path.basename(self.file_name))
        reply = QtWidgets.QMessageBox.question(self, 'Close Document',
                                               msg,
                                               QtWidgets.QMessageBox.Save
                                               | QtWidgets.QMessageBox.Discard
                                               | QtWidgets.QMessageBox.Cancel,
                                               QtWidgets.QMessageBox.Save)
        if reply == QtWidgets.QMessageBox.Save:
            self.doSave()
        return reply

    #################################################################################
    # File menu actions
    #################################################################################

    def setFileName(self, file_name):
        """Sets the filename and updates the window title accordingly"""
        self.file_name = file_name if file_name else self.tr("untitled.s")
        self.ui.sourceCodeEditor.document().setModified(False)
        self.updateFileActions()

    def doNew(self):
        """Creates a new file"""
        if self.checkCurrentFileState() == QtWidgets.QMessageBox.Cancel:
            return
        # 1) Change to tab 0
        self.ui.tabWidgetCode.setCurrentIndex(0)
        # 2) Set file name to default untitled name
        self.setFileName("")
        # 3) Clear sourceCodeEditor
        self.ui.sourceCodeEditor.clear()
        # 4) Clear breakpoints when creating a new file
        self.clearBreakpoints()

    def _getDirectory(self):
        directory = self.settings.value("LastUsedDirectory")
        if not os.path.isdir(directory):
            directory = self.defaultSettings.value("LastUsedDirectory")
        return directory

    def doOpen(self):
        """Opens an ARM assembler file"""
        if self.checkCurrentFileState() == QtWidgets.QMessageBox.Cancel:
            return
        file_name = QtWidgets.QFileDialog.getOpenFileName(self, self.tr("Open File"),
                                                          self._getDirectory(),
                                                          self.tr("ARM assembler files (*.s);;ARM C files (*.c)"))
        # @warning: file_name should return a string, but on Python 3.3.5, PySide2 1.2.2, and Qt 4.8.5, it returns a
        #           tuple (file_name, 'ARM assembler files (*.s)')
        # @todo: check why this is happening and remove the following hack and this comment
        if type(file_name) == tuple:
            file_name = file_name[0]
        if file_name:
            self.readFile(file_name)
            # Change to tab 0
            self.ui.tabWidgetCode.setCurrentIndex(0)
            # Clear breakpoints for the new read file
            self.clearBreakpoints()
            # Update LastUsedDirectory setting
            self.settings.setValue("LastUsedDirectory", os.path.dirname(file_name))

    def doOpenExample(self, action):
        """Opens an example file"""
        if self.checkCurrentFileState() == QtWidgets.QMessageBox.Cancel:
            return
        file_name = action.data()
        if file_name:
            tmp_dir = tempfile.mkdtemp(".qtarmsim")
            file_name_in_tmp = os.path.join(tmp_dir, os.path.basename(file_name))
            shutil.copyfile(file_name, file_name_in_tmp)
            self.readFile(file_name_in_tmp)
            # Change to tab 0
            self.ui.tabWidgetCode.setCurrentIndex(0)
            # Clear breakpoints for the new read file
            self.clearBreakpoints()
            # Do not update LastUsedDirectory setting
            pass

    def readFile(self, file_name):
        """Reads a file. Can be called using an argument from the command line"""
        text = ''
        encodings = ['utf-8', 'latin1', 'ascii']
        for i in range(len(encodings)):
            try:
                f = open(file_name, encoding=encodings[i])
            except FileNotFoundError as e:
                QtWidgets.QMessageBox.warning(self, self.tr("Open File"), "{}: '{}'.".format(e.strerror, file_name))
                raise e
            try:
                text = f.read()
                f.close()
                break
            except UnicodeDecodeError as e:
                f.close()
                if i < len(encodings) - 1:
                    msg = self.tr("Will try next with '{}' encoding.").format(encodings[i + 1])
                else:
                    msg = self.tr(
                        "No more supported encodings.\nPlease, manually convert the file to 'utf-8' and load it again.")
                err_msg = self.tr("Couldn't read the file using the '{}' encoding.\n{}").format(encodings[i], msg)
                QtWidgets.QMessageBox.warning(self, self.tr("Error reading '{}'").format(os.path.basename(file_name)),
                                              err_msg)
                if i == len(encodings) - 1:
                    raise e
        if file_name[-2:] == '.c':
            self.ui.sourceCodeEditor.setCMode()
        else:
            self.ui.sourceCodeEditor.setARMMode()
        self.ui.sourceCodeEditor.setPlainText(text)
        self.setFileName(file_name)

    def doSave(self):
        """Saves the current ARM assembler file"""
        # Set current source code has been assembled to False
        self.current_source_code_assembled = False
        # Save file
        if self.file_name == self.tr("untitled.s"):
            return self.doSave_As()
        else:
            return self.saveFile(self.file_name)

    def doSave_As(self):
        """Saves the ARM assembler file with a new specified name"""
        assert (self.file_name != "")
        new_file_name = self.file_name
        if os.path.dirname(new_file_name) == '':
            new_file_name = os.path.join(self._getDirectory(), new_file_name)
        new_file_name = QtWidgets.QFileDialog.getSaveFileName(self, self.tr("Save File"),
                                                              new_file_name,
                                                              self.tr("ARM assembler files (*.s);;ARM C files (*.c)"))
        # @warning: file_name should return a string, but on Python 3.3.5, PySide2 1.2.2, and Qt 4.8.5, it returns a
        # tuple (file_name, 'ARM assembler files (*.s)')
        # @todo: check why this is happening and remove the following hack and this comment
        if type(new_file_name) == tuple:
            new_file_name = new_file_name[0]
        if new_file_name != '':
            return self.saveFile(new_file_name)
        else:
            return False

    def saveFile(self, file_name):
        """Saves the contents of the source editor on the given file name"""
        asm_file = QtCore.QFile(file_name)
        if not asm_file.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            QtWidgets.QMessageBox.warning(self,
                                          self.tr("Error"),
                                          self.tr("Could not write to file '{0}':\n{1}.")
                                          .format(file_name, asm_file.errorString()))
            return False
        text = self.ui.sourceCodeEditor.document().toPlainText()
        asm_file.write(
            text.encode('utf-8'))  # @todo: let user decide which encoding (including sys.getdefaultencoding())
        asm_file.close()
        self.statusBar().showMessage(self.tr("File saved"), 2000)
        # Set file name
        self.setFileName(file_name)
        # Update LastUsedDirectory setting
        self.settings.setValue("LastUsedDirectory", os.path.dirname(file_name))
        # Return
        return True

    def doPrint(self):
        """Prints the current ARM assembler source file or the disassembled code"""
        printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
        printDialog = QtPrintSupport.QPrintDialog(printer, self)
        printDialog.setOption(QtPrintSupport.QAbstractPrintDialog.PrintToFile, True)
        if printDialog.exec_() == PySide2.QtWidgets.QDialog.Accepted:
            if self.ui.tabWidgetCode.currentIndex() == 0:
                self.ui.sourceCodeEditor.print_(printer)
            else:
                self.ui.tabTabARMSim.currentWidget().print_(printer)

    def doQuit(self):
        """Quits the program"""
        self.close()

    #################################################################################
    # Edit menu actions
    #################################################################################

    def do_Undo(self):
        self.ui.sourceCodeEditor.undo()

    def doRedo(self):
        self.ui.sourceCodeEditor.redo()

    def doCut(self):
        self.ui.sourceCodeEditor.cut()

    def doCopy(self):
        self.ui.sourceCodeEditor.copy()

    def doPaste(self):
        self.ui.sourceCodeEditor.paste()

    def doSelect_All(self):
        self.ui.sourceCodeEditor.selectAll()

    #################################################################################
    # Run menu actions
    #################################################################################

    def highlight_pc_line(self):
        PC = self.registersModel.getRegister(15)
        for simCodeEditor in self.ui.simCodeEditors:
            document = simCodeEditor.document()
            cursor = QtGui.QTextCursor(document)
            cursor = document.find(QtCore.QRegExp("^\\[{}\\]".format(PC)), cursor, QtGui.QTextDocument.FindWholeWords)
            if cursor:
                simCodeEditor.setCurrentHighlightedLineNumber(cursor.blockNumber())
                self.ui.tabTabARMSim.setCurrentWidget(simCodeEditor)
                break

    def _processExecutionResponse(self, response):
        self.ui.textEditMessages.append(response.assembly_line)
        self.updateFlags()
        for (reg_number, reg_value) in response.registers:
            self.registersModel.setRegister(reg_number, reg_value)
        for (hex_address, hex_byte) in response.memory:
            self.memoryModel.setByte(hex_address, hex_byte)
            self.ui.treeViewMemory.expand(self.ui.treeViewMemory.model().mapFromSource(self.memoryModel.getIndex('0x20070000').parent()))
            self.ui.treeViewMemory.scrollTo(self.ui.treeViewMemory.model().mapFromSource(self.memoryModel.getIndex(hex_address)))
        if response.result == "ERROR":
            self.ui.textEditMessages.append("<b>An error has occurred.</b>")
        elif response.result == "BREAKPOINT REACHED":
            self.ui.textEditMessages.append("Breakpoint reached.")
        elif response.result == "END OF PROGRAM":
            self.ui.textEditMessages.append("End of program reached.")
        if response.errmsg:
            self.ui.textEditMessages.append(response.errmsg)

    def _doStep(self, simulator_step_callback):
        if not self.simulator.connected:
            return
        self.registersModel.stepHistory()
        self.memoryModel.stepHistory()
        response = simulator_step_callback()
        self._processExecutionResponse(response)
        self.highlight_pc_line()

    def doStepInto(self):
        self._doStep(self.simulator.getExecuteStepInto)

    def doStepOver(self):
        self._doStep(self.simulator.getExecuteStepOver)

    def doRestart(self):
        self.simulator.disconnect()
        self.doAssemble()
        # Restore breakpoints
        for hex_address in self.breakpoints:
            self.simulator.setBreakpoint(hex_address)

    def doRun(self):
        # @warning: Don't issue RunProgressBarDialog(self.simulator, **parent=self**)
        #           After executing Examples > Registers > add.s the cursor on the editor is lost
        runProgressBarDialog = RunProgressBarDialog(self.simulator)
        if not runProgressBarDialog.exec_():
            self.doRestart()
            return
        response = runProgressBarDialog.getResponse()
        self._processExecutionResponse(response)
        self.highlight_pc_line()

    #################################################################################
    # Window menu actions
    #################################################################################

    @staticmethod
    def _doShow(widget, action):
        if widget.isVisible():
            widget.setHidden(True)
        else:
            widget.setVisible(True)
        action.setChecked(widget.isVisible())

    def doShow_Statusbar(self):
        """Shows or hides the status bar"""
        self._doShow(self.ui.statusBar, self.ui.actionShow_Statusbar)

    def doShow_Toolbar(self):
        """Shows or hides the tool bar"""
        self._doShow(self.ui.toolBar, self.ui.actionShow_Toolbar)

    def doShow_Registers(self):
        """Shows or hides the registers dock widget"""
        self._doShow(self.ui.dockWidgetRegisters, self.ui.actionShow_Registers)

    def doShow_Memory(self):
        """Shows or hides the Memory dock widget"""
        self._doShow(self.ui.dockWidgetMemory, self.ui.actionShow_Memory)

    def doShow_Memory_Dump(self):
        """Shows or hides the Memory Dump dock widget"""
        self._doShow(self.ui.dockWidgetMemoryDump, self.ui.actionShow_Memory_Dump)

    def doShow_LCD_Display(self):
        """Shows or hides the LCD Display dock widget"""
        self._doShow(self.ui.dockWidgetLCDDisplay, self.ui.actionShow_LCD_Display)

    def doShow_Terminal(self):
        """Shows or hides the Terminal dock widget"""
        self._doShow(self.ui.dockWidgetTerminal, self.ui.actionShow_Terminal)

    def doShow_Messages(self):
        """Shows or hides the Messages dock widget"""
        self._doShow(self.ui.dockWidgetMessages, self.ui.actionShow_Messages)

    def doRestore_Default_Layout(self):
        """Restores the initial layout"""
        self.restoreState(self.initialWindowState)
        # status bar is not automatically restored, restore it manually
        self.ui.statusBar.setVisible(True)
        self.updateShowActions()

    def doPreferences(self):
        preferences = PreferencesDialog(self)
        if preferences.exec_():
            if self.simulator and self.simulator.connected:
                self.sendSettingsToARMSim()

    def closeEvent(self, event):
        """Called when the main window is closed. Saves state and performs clean up actions."""
        if self.checkCurrentFileState() == QtWidgets.QMessageBox.Cancel:
            event.ignore()
            return
        # Save current geometry and window state
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        # Disconnect the simulator
        if self.simulator and self.simulator.connected:
            self.simulator.disconnect()
        # Close windows
        self.helpWindow.close()
        # Accept event
        event.accept()

    def showEvent(self, event):
        """Method called when the show event is received"""
        super(QtARMSimMainWindow, self).showEvent(event)
        if self.helpWindow.isVisible():
            self.helpWindow.showNormal()

    def hideEvent(self, event):
        """Method called when the hide event is received, minimizes the other app windows"""
        super(QtARMSimMainWindow, self).hideEvent(event)
        if self.helpWindow.isVisible():
            self.helpWindow.showMinimized()

    @staticmethod
    def doWhats_This():
        """Activates the What's This? mode"""
        QtWidgets.QWhatsThis.enterWhatsThisMode()

    def welcome_message(self):
        return "<b>QtARMSim " + self.tr("version") + " " + __version__ + "</b><br></br>\n" + \
               "(c) 2014-18 Sergio Barrachina Mir<br></br>\n" + \
               self.tr("Developed at the Jaume I University, Castellón, Spain.<br></br>\n")

    def about_message(self):
        return "<html>" + \
               "<p><b>" + self.tr("Version") + " " + __version__ + "</b></p>" + \
               "<p>" + "(c) 2014-18 Sergio Barrachina Mir" + "</p>" + \
               "<p>" + \
               "<a href='http://lorca.act.uji.es/projects/qtarmsim/'>http://lorca.act.uji.es/projects/qtarmsim/</a>" + \
               "</p>" + \
               "<p></p>" + \
               "<p>" + self.tr("Running on ") + \
               "Python " + sys.version.split(" ")[0] + ", " + \
               "PySide2 " + PySide2.__version__ + ", and " + \
               "Qt " + QtCore.__version__ + "." + \
               "</p>" + \
               "<hr/>" + \
               self.tr("<p><b>Acknowledgments</b></p>") + \
               "<p></p>" + \
               self.tr(
                   "<p>Initial development of QtARMSim was based on the graphical frontend for Spim developed on 2008 by Gloria Edo Piñana.</p>") + \
               self.tr(
                   "<p>Most of the ARM keywords and directives used on the assembler editor syntax highlighter are from the listings ARM definition for LaTeX (c) 2013 by Jacques Supcik.</p>") + \
               self.tr("<p>GUI icons from the KDE Breeze theme icons.</p>") + \
               self.tr("<p>The LCD Display font is '1 Digit' by David Chung.</p>") + \
               self.tr(
                   "<p>Software floating point support thanks to <a href='https://www.quinapalus.com/qfplib.html'>Qfplib: an ARM Cortex-M0 floating-point library in 1 kbyte</a>, (c) Mark Owen.</p>") + \
               "</html>"

    def doAbout_Qt_ARMSim(self):
        """Shows the About QtARMSim dialog"""
        QtWidgets.QMessageBox.about(self,
                                    self.tr("About QtARMSim"),
                                    self.about_message(),
                                    )

    def doAbout_ARMSim(self):
        """Shows the About ARMSim dialog"""
        QtWidgets.QMessageBox.about(self,
                                    self.tr("About ARMSim"),
                                    self.simulator.getVersion())

    def doHelp(self):
        """Shows the Help window"""
        self.helpWindow.setVisible(True)

    #################################################################################
    # Communication with ARMSim
    #################################################################################

    def updateFlags(self):
        (reg, hex_value) = self.simulator.getRegister('r16')  # @UnusedVariable reg
        value = int(hex_value, 16)
        N = '<b>N</b>' if value & 2 ** 31 else 'n'
        Z = '<b>Z</b>' if value & 2 ** 30 else 'z'
        C = '<b>C</b>' if value & 2 ** 29 else 'c'
        V = '<b>V</b>' if value & 2 ** 28 else 'v'
        self.flagsText.setText("{} {} {} {}".format(N, Z, C, V))

    def updateRegisters(self):
        """Updates the registers dock upon ARMSim data."""
        registers_model = self.ui.treeViewRegisters.model()
        for (reg, hex_value) in self.simulator.getRegisters():
            registers_model.setRegister(reg, hex_value)
        registers_model.clearHistory()
        self.updateFlags()

    class GetMemoryThread(QtCore.QThread):
        finished = QtCore.Signal(list)

        def __init__(self, parent=None):
            super(QtARMSimMainWindow.GetMemoryThread, self).__init__(parent)
            self.parent = parent

        def run(self):
            memory_banks = []
            for (memtype, hex_start, hex_end) in self.parent.simulator.getMemoryBanks():
                # Dump memory
                start = int(hex_start, 16)
                end = int(hex_end, 16)
                nbytes = end - start
                membytes = []
                for (hex_address, hex_byte) in self.parent.simulator.getMemory(hex_start,
                                                                               nbytes):  # @UnusedVariable address
                    membytes.append(hex_byte)
                armsim_lines = []
                # if memtype == ROM then load the program into the ARMSim tab
                if memtype == 'ROM':
                    ninsts = int(nbytes / 2)  # Maximum number of instructions in the given ROM
                    armsim_lines += ['@@ ----------------------------------------',
                                     '@@ DISASSEMBLED CODE STARTING AT {}'.format(hex_start),
                                     '@@ ----------------------------------------']
                    armsim_lines += self.parent.simulator.getDisassemble(hex_start, ninsts)
                memory_banks.append({
                    'memtype': memtype,
                    'hex_start': hex_start,
                    'nbytes': nbytes,
                    'membytes': membytes,
                    'armsim_lines': armsim_lines,
                })
            self.finished.emit(memory_banks)

    def onGetMemoryThreadFinished(self, memory_banks):
        # Display the disassembled code
        for simCodeEditor in self.ui.simCodeEditors:
            simCodeEditor.setPlainText('')
            simCodeEditor.setCenterOnScroll(False)
            simCodeEditor.scrollLock = True
            simCodeEditor.clearDecorations()
            simCodeEditor.hide()
        i = 0
        self.ui.tabTabARMSim.clear()
        for mb in memory_banks:
            if mb['armsim_lines']:
                self.ui.tabTabARMSim.addTab(self.ui.simCodeEditors[i], mb['hex_start'])
                n_lines = len(mb['armsim_lines'])
                for j in range(0, n_lines//30+1):
                    self.ui.simCodeEditors[i].appendPlainText('\n'.join(mb['armsim_lines'][j*30: min((j+1)*30, n_lines)]))
                    QtWidgets.QApplication.processEvents()
                i += 1
        for simCodeEditor in self.ui.simCodeEditors:
            simCodeEditor.scrollLock = False
        self.highlight_pc_line()
        # Stop spinner now
        self.stopSpinner()
        # Process memory info
        self.memoryModel.reset()
        self.ui.tabWidgetMemoryDump.clear()
        memoryBank = 0
        for mb in memory_banks:
            # Append the memory bank
            self.memoryModel.appendMemoryBank(mb['memtype'], mb['hex_start'], mb['membytes'])
            # Add a page to tabWidgetMemoryDump
            memoryDumpProxyModel = MemoryDumpProxyModel()
            memoryDumpProxyModel.setSourceModel(self.memoryModel, memoryBank)
            memoryBank += 1
            memoryDumpView = QtWidgets.QTableView()
            memoryDumpView.setModel(memoryDumpProxyModel)
            memoryDumpView.resizeColumnsToContents()
            memoryDumpView.resizeRowsToContents()
            self.ui.tabWidgetMemoryDump.addTab(memoryDumpView, "{}".format(mb['memtype']))
            QtWidgets.QApplication.processEvents()
        # Focus the first tab with RAM memory
        for i in range(self.ui.tabWidgetMemoryDump.count()):
            if self.ui.tabWidgetMemoryDump.tabText(i) == "RAM":
                self.ui.tabWidgetMemoryDump.setCurrentIndex(i)
                break
        # Modify the layout of treeViewMemory
        # @todo: expand automatically the first RAM module
        self.ui.treeViewMemory.expand(self.ui.treeViewMemory.model().mapFromSource(self.memoryModel.getIndex('0x20070000').parent()))
        QtWidgets.QApplication.processEvents()
        self.ui.treeViewMemory.updateGeometry()

    def updateMemory(self):
        """Updates the memory widgets upon ARMSim data."""
        self.getMemoryThread.start()

    def connectToARMSim(self):
        self.simulator = None
        if self.settings.value("ARMSimServer") in ('localhost', '127.0.0.1') \
                and not self.settings.value("ARMSimCommand"):
            QtWidgets.QMessageBox.warning(self, self.tr("ARMSim command empty"),
                                          self.tr("ARMSim command is empty.\n\n"
                                                  "Please go to 'Edit, Preferences...' and set it.\n"))
            return False
        if not os.path.isfile(self.settings.value("ARMGccCommand")):
            QtWidgets.QMessageBox.warning(self, self.tr("ARM gcc not found"),
                                          self.tr("ARM gcc command not found.\n\n"
                                                  "Please go to 'Edit, Preferences...' and set it.\n"))
            return False
        self.simulator = ARMSimConnector(verbose=self.verbose)
        if self.debug:
            self.simulator.mysocket.sentLine.connect(self.sentLineToSimulator)
            self.simulator.mysocket.receivedLine.connect(self.receivedLineFromSimulator)
        self.statusBar().showMessage(self.tr("Connecting to ARMSim..."), 2000)
        connectProgressBarDialog = ConnectProgressBarDialog(self.simulator,
                                                            self.settings.value("ARMSimCommand"),
                                                            self.settings.value("ARMSimDirectory"),
                                                            self.settings.value("ARMSimServer"),
                                                            int(self.settings.value("ARMSimPort")),
                                                            self
                                                            )
        if not connectProgressBarDialog.exec_():
            return False
        errmsg = connectProgressBarDialog.getMsg()
        if errmsg:
            QtWidgets.QMessageBox.warning(self, self.tr("Connection to ARMSim failed\n\n"), "{}".format(errmsg))
            return False
        self.ui.textEditMessages.append(u"<b>Connected to ARMSim (ARMSim version info follows).</b><br/>")
        self.ui.textEditMessages.append(self.simulator.getVersion())
        self.ui.textEditMessages.append("<br/>")
        self.statusBar().showMessage(self.tr("Connected to ARMSim at port {}").format(self.simulator.current_port),
                                     2000)
        return self.sendSettingsToARMSim()

    def sendSettingsToARMSim(self):
        for setting in [("ARMSimUseLabels", "TRUE" if self.settings.value("ARMSimUseLabels") != "0" else "FALSE"),
                        ("ARMGccCommand", self.settings.value("ARMGccCommand")),
                        ("ARMGccOptions", self.settings.value("ARMGccOptions"))]:
            errmsg = self.simulator.setSettings(setting[0], setting[1])
            if errmsg:
                QtWidgets.QMessageBox.warning(self, self.tr("ARMSim set setting failed"), "\n{}\n".format(errmsg))
                return False
        return True

    def sentLineToSimulator(self, line):
        self._received_lines_from_simulator = 0
        self.ui.textBrowserTerminal.append('> {}'.format(line))

    def receivedLineFromSimulator(self, line):
        self._received_lines_from_simulator += 1
        if self._received_lines_from_simulator < 10:
            self.ui.textBrowserTerminal.append('{}'.format(line))
        elif self._received_lines_from_simulator == 10:
            self.ui.textBrowserTerminal.append('[...]')

    def sendLineToSimulator(self):
        if self.simulator:
            line = self.ui.lineEditTerminal.text()
            self.ui.lineEditTerminal.clear()
            sb = self.ui.textBrowserTerminal.verticalScrollBar()
            sb.setValue(sb.maximum())
            self.terminalHistoryPush(line)
            self.simulator.sendCommand(line)

    def terminalHistoryUp(self):
        self._terminal_history_cursor -= 1
        terminal_history = self.settings.value("TerminalHistory").split('::')
        if -self._terminal_history_cursor > len(terminal_history):
            self._terminal_history_cursor = -len(terminal_history)
        return terminal_history[self._terminal_history_cursor]

    def terminalHistoryDown(self):
        self._terminal_history_cursor += 1
        if self._terminal_history_cursor >= 0:  # new line (not in history)
            self._terminal_history_cursor = 0
            return ""
        else:
            terminal_history = self.settings.value("TerminalHistory").split('::')
            return terminal_history[self._terminal_history_cursor]

    def terminalHistoryPush(self, line):
        self._terminal_history_cursor = 0
        terminal_history = self.settings.value("TerminalHistory").split('::')
        terminal_history.append(line)
        if len(terminal_history) > 20:
            terminal_history = terminal_history[-20:]
        self.settings.setValue("TerminalHistory", '::'.join(terminal_history))
