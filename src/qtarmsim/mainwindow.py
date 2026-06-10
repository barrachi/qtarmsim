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

from __future__ import annotations

import os
import sys
import platform
import re
import shutil
import tempfile
from functools import partial
from glob import glob
from typing import Callable, TypedDict, cast

import PySide6
from PySide6 import QtCore, QtGui, QtPrintSupport, QtWidgets
from PySide6.QtCore import QByteArray, QObject, Qt
from PySide6.QtGui import QAction, QKeyEvent
from PySide6.QtWidgets import QDialog, QLabel, QWidget
from typing_extensions import override

from .comm.armsimconnector import ARMSimConnector
from .comm.armsimmoduleconnector import ARMSimModuleConnector
from .comm.responses import ExecuteResponse
from .model.memorybywordproxymodel import MemoryByWordProxyModel
from .model.memorydumpproxymodel import MemoryDumpProxyModel
from .model.memorymodel import MemoryModel
from .model.registersmodel import RegistersModel
from .modulepath import module_path
from .theme import DARK, SYSTEM, apply_theme, get_original_font_size, make_icon, save_default_style
from .utils import getMonoSpacedFont
from .res import breeze_icons_rc, main_rc
from .ui.ui_mainwindow import Ui_MainWindow
from .widget.armcodeeditor import ARMCodeEditor
from .widget.memorydumpview import MemoryDumpView
from .window.connectprogressbardialog import ConnectProgressBarDialog
from .window.help import HelpWindow
from .window.preferencesdialog import PreferencesDialog
from .window.runprogressbardialog import RunProgressBarDialog

try:
    from ._version import __version__
except ImportError:
    # Fallback for when the package is not installed (e.g., during development without a build)
    __version__ = "0.0.0+unknown"

def __stub():  # pyright: ignore[reportUnusedFunction]
    """
    This function does nothing. It exists only to avoid main_rc and breeze_icons_rc imports from being removed.
    """
    return main_rc, breeze_icons_rc


def _fromUtf8(s: str) -> str:
    return s


def which(cmd: str) -> str | None:
    """Searches cmd in the system PATH. Returns the full path or None."""
    return shutil.which(cmd)


class DefaultSettings:

    def __init__(self) -> None:
        self._setARMSimDefaults()
        self._setDirectoryDefaults()

    def value(self, name: str) -> str:
        return cast(str, getattr(self, "_" + name))

    def _setARMSimDefaults(self) -> None:
        self._ARMSimBackend: str = "module"
        # Python external server defaults
        python_server = os.path.join(module_path, "armsim", "armsim_python", "server.py")
        if os.path.isfile(python_server):
            python_server = os.path.abspath(python_server)
            self._ARMSimCommandPython: str = "{} {}".format(sys.executable, os.path.basename(python_server))
            self._ARMSimDirectoryPython: str = os.path.dirname(python_server)
        else:
            self._ARMSimCommandPython = ""
            self._ARMSimDirectoryPython = ""
        # Ruby external server defaults
        ruby_dir = os.path.join(module_path, "armsim", "armsim_ruby")
        self._ARMSimDirectoryRuby: str = ruby_dir if os.path.isdir(ruby_dir) else ""
        if platform.system() == "Windows":
            self._ARMSimCommandRuby: str = "rubyw server.rb"
        else:
            self._ARMSimCommandRuby = "ruby server.rb"
        self._ARMSimServer: str = "localhost"
        self._ARMSimPort: str = "8010"
        self._ARMSimUseLabels: str = "0"
        gcc_names = ["arm-none-eabi-gcc", "arm-unknown-linux-gnueabi-gcc", "arm-linux-gnueabi-gcc"]
        if platform.system() == "Windows":
            gcc_names = ["{}.exe".format(name) for name in gcc_names]
        fname = ""
        for name in gcc_names:
            fname = which(name)
            if fname:
                fname = os.path.abspath(fname)
                break
        # See https://en.wikipedia.org/wiki/Uname for possible values of platform.machine() (i.e., uname -m)
        if not fname:  # Use bundled GNU Gcc if no native (cross) compiler has been found
            def get_fname(arch_dir: str, gcc: str="arm-none-eabi-gcc"):
                return os.path.join(module_path, "gcc-arm", arch_dir, "bin", gcc)

            if platform.system() == "Linux":
                if platform.machine() == 'aarch64':
                    fname = get_fname("linuxARM")
                elif platform.machine() == 'x86_64':
                    fname = get_fname("linux64")
                else:
                    fname = get_fname("linux32")
            elif platform.system() == "Windows":
                executable = "arm-none-eabi-gcc.exe"
                if platform.machine() in ('AMD64', 'x86_64'):
                    fname = get_fname("win64", executable)
                else:
                    fname = get_fname("win32", executable)
            elif platform.system() == "Darwin":
                if platform.machine() == 'arm64':
                    fname = get_fname("macosARM")
                elif platform.machine() == 'x86_64':
                    fname = get_fname("macos")
                else:
                    fname = "Could not determine the correct compiler for this macOS system!"
            else:
                fname = "Could not determine the correct compiler for this unknown system!"
        fname = fname if fname else ""
        self._ARMGccCommand: str = fname
        self._ARMGccOptions: str = "-mcpu=cortex-m1 -mthumb -c"
        self._TerminalHistory: str = "SHOW VERSION"
        self._ColorTheme: str = SYSTEM
        self._FontSize: str = "0"

    # noinspection PyArgumentList
    def _setDirectoryDefaults(self) -> None:
        self._LastUsedDirectory: str = QtCore.QDir.currentPath()


class UiMainWindowExtended(Ui_MainWindow):
    sourceCodeEditor: ARMCodeEditor # pyright: ignore[reportUninitializedInstanceVariable]
    simCodeEditors: list[ARMCodeEditor] = []

# noinspection PyArgumentList
class QtARMSimMainWindow(QtWidgets.QMainWindow):
    """Main window of the QtARMSim application."""

    def __init__(self, parent: QWidget | None = None, debug: bool = False, verbose: bool = False) -> None:
        # Call super.__init__()
        super(QtARMSimMainWindow, self).__init__(parent)
        # Set debug and verbosity flags
        self.memoryModel: MemoryModel | None = None
        self.debug: bool = debug
        self.verbose: bool = verbose
        # Load the user interface
        self.ui: UiMainWindowExtended = UiMainWindowExtended()
        # Setup ui
        self.ui.setupUi(self)  # pyright: ignore[reportUnknownMemberType]
        # Attributes that will be initialized by extendUi()
        self.simulator: ARMSimConnector | ARMSimModuleConnector | None = None
        self.registersModel: RegistersModel | None = None
        self.flagsLabel: QtWidgets.QLabel = QtWidgets.QLabel()
        self.flagsText: QtWidgets.QLabel = QtWidgets.QLabel()
        # Extend the Ui
        self.extendUi()
        # Set the file name to default untitled name
        self.fileName: str = ""
        self.setFileName("")
        # Set the application icon
        self.setWindowIcon(QtGui.QIcon(":/images/qtarmsim.svg"))
        # Help windows initialization
        self.helpWindow: HelpWindow = HelpWindow()
        # Connect actions
        self.connectActions()
        # Editor flags
        self.editorFlags: dict[str, bool] = {
            'selectionAvailable': False,
            'redoAvailable': False,
            'undoAvailable': False,
        }
        # Saves the initial WindowState of the interface
        self.initialWindowState: QByteArray = self.saveState()
        # Attributes that will be initialized by readSettings()
        self.defaultSettings: DefaultSettings
        self.settings: QtCore.QSettings
        # Read the settings
        self.readSettings()
        # Set current source code has been assembled to False
        self.current_source_code_assembled: bool = False
        # Breakpoints
        self.breakpoints: list[str] = []
        # Spinner
        self.spinnerLabel: QLabel = QtWidgets.QLabel(self)
        self.spinnerLabel.setMovie(QtGui.QMovie(":/images/ajax-loader.gif"))
        self.spinnerLabel.hide()
        # Worker threads
        self.getMemoryThread: 'QtARMSimMainWindow.GetMemoryThread' = self.GetMemoryThread(self)
        _ = self.getMemoryThread.memoryBanksReady.connect(self.onGetMemoryThreadFinished)
        # Print a welcome message on the Messages' Window and show Ready on the status bar
        self.ui.textEditMessages.append(self.welcome_message())
        self.statusBar().showMessage(self.tr("Ready"))
        # Initialize the number of received lines from the simulator
        self._received_lines_from_simulator: int = 0
        # Initialize the terminal history cursor
        self._terminal_history_cursor: int = 0

    @override
    def show(self, *args: object, **kwargs: object) -> None:
        """Method called when the window is ready to be shown"""
        super().show(*args, **kwargs)
        # updateFileActions updateShowActions and enableSimulatorActions have to be called after the window is shown
        self.updateFileActions()
        self.updateEditActions()
        self.updateViewActions()
        self.enableSimulatorActions(False)

    def extendUi(self) -> None:
        """Extends the Ui with new objects, links the views with their models,
           and puts in tabs the bottom dock widgets"""

        # macOS X quirks
        if platform.system() == 'Darwin':
            # Set unified title and toolbar on Mac
            # @todo: check again the next on a macOS (last time it didn't work)
            # self.setUnifiedTitleAndToolBarOnMac(True)
            self.ui.menuView.removeAction(self.ui.actionFull_Screen_Mode)

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
        self.memoryModel = MemoryModel()
        memoryByWordProxyModel: MemoryByWordProxyModel = MemoryByWordProxyModel(self)
        memoryByWordProxyModel.setSourceModel(self.memoryModel)
        self.ui.treeViewMemory.setModel(memoryByWordProxyModel)
        # self.ui.memoryLCDView.setMemoryModel(self.memoryModel, '0x20080000', 40, 6)

        # Status bar with flags
        self.statusBar().addWidget(QtWidgets.QLabel(""), 10)  # No permanent
        self.flagsLabel = QtWidgets.QLabel("Flags:")
        self.statusBar().addPermanentWidget(self.flagsLabel, 0)
        self.flagsText = QtWidgets.QLabel("- - - -")
        self.flagsText.setFrameStyle(QtWidgets.QFrame.Shadow.Sunken | QtWidgets.QFrame.Shape.StyledPanel)
        font = QtGui.QFont("fake font name")  # @warning: fake name needed to setStyleHint work
        font.setStyleHint(QtGui.QFont.StyleHint.TypeWriter)
        if not QtGui.QFontInfo(font).fixedPitch():
            font.setStyleHint(QtGui.QFont.StyleHint.Monospace)
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

        # If not in debug mode, hide Terminal and Simulator Output (actions and docks)
        if not self.debug:
            self.ui.menuView.removeAction(self.ui.actionShow_Terminal)
            self.ui.dockWidgetTerminal.hide()
            self.ui.menuView.removeAction(self.ui.actionShow_Simulator_Output)
            self.ui.dockWidgetSimulatorOutput.hide()

        # Tabify bottom dock widgets
        bottomDocks : list[QtWidgets.QDockWidget] = []
        if self.dockWidgetArea(self.ui.dockWidgetMessages) == Qt.DockWidgetArea.BottomDockWidgetArea:
            bottomDocks.append(self.ui.dockWidgetMessages)
        if self.dockWidgetArea(self.ui.dockWidgetMemoryDump) == Qt.DockWidgetArea.BottomDockWidgetArea:
            bottomDocks.append(self.ui.dockWidgetMemoryDump)
        if self.dockWidgetArea(self.ui.dockWidgetLCD) == Qt.DockWidgetArea.BottomDockWidgetArea:
            bottomDocks.append(self.ui.dockWidgetLCD)
        if self.dockWidgetArea(self.ui.dockWidgetTerminal) == Qt.DockWidgetArea.BottomDockWidgetArea:
            bottomDocks.insert(0, self.ui.dockWidgetTerminal)
        if self.dockWidgetArea(self.ui.dockWidgetSimulatorOutput) == Qt.DockWidgetArea.BottomDockWidgetArea:
            bottomDocks.insert(1, self.ui.dockWidgetSimulatorOutput)
        if len(bottomDocks) > 1:
            self.tabifyDockWidget(bottomDocks[0], bottomDocks[1])
            if len(bottomDocks) > 2:
                for i in range(1, len(bottomDocks) - 1):
                    self.splitDockWidget(bottomDocks[i], bottomDocks[i + 1], Qt.Orientation.Horizontal)
            bottomDocks[0].raise_()

        # Examples menu
        self.buildExamplesMenu(self.ui.menuExamples, os.path.join(module_path, "examples"))

    def buildExamplesMenu(self, menu: QtWidgets.QMenu, path: str) -> None:
        def _name_from_path(path_: str) -> str:
            basename: str = os.path.basename(path_).replace('_', ' ')
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
                action = QtGui.QAction(self)
                action.setText(QtWidgets.QApplication.translate("Examples", _name_from_path(file_or_dir), None, -1))
                action.setData(file_or_dir)
                _ = action.triggered.connect(partial(self.doOpenExample, action))
                menu.addAction(action)

    def readSettings(self) -> None:
        """Reads the settings from the settings file or initializes them from defaultSettings"""
        self.defaultSettings = DefaultSettings()
        self.settings = QtCore.QSettings("UJI", "QtARMSim")
        geometry: QtCore.QByteArray = cast(QtCore.QByteArray, self.settings.value("geometry", self.defaultGeometry()))
        _ = self.restoreGeometry(QtCore.QByteArray(geometry))
        # @TODO: The next line does not work as expected, the central widget does not claims all the space
        # self.restoreState(self.settings.value("windowState", self.initialWindowState))
        # -----------------------------------------------------------------------------
        # Begin migration of settings versions
        # -----------------------------------------------------------------------------
        conf_version = int(cast(str, self.settings.value("ConfVersion", "1")))
        ARMSimCommand: str = cast(str, self.settings.value("ARMSimCommand")) if self.settings.value("ARMSimCommand") else ""
        if (conf_version == 1
                and ARMSimCommand
                and ARMSimCommand.count("ruby") == 0):
            # Migrate from version 1 to version 2
            # Version 1 -> ARMSimCommand only had the server.rb full path.
            # Version 2 -> ARMSimCommand has the full command, e.g. 'rubyw server.rb',
            #              and ARMSimDirectory has the working directory of the simulator.
            #              ARMSimPortMinimum and ARMSimPortMaximum are no longer used.
            ruby_cmd: str = self.defaultSettings.value("ARMSimCommandRuby").split(" ")[0]
            self.settings.setValue("ARMSimCommand", "{} {}".format(ruby_cmd, os.path.basename(ARMSimCommand)))
            self.settings.setValue("ARMSimDirectory", os.path.dirname(ARMSimCommand))
            conf_version = 2
        # Something changed in conf_version 3 that was lost in time
        if (conf_version < 4):
            # Version <4 -> ARMSim ruby implementation
            # Version 4 -> ARMSim reimplemented in python
            # @warning: Reread setting as it could have been changed
            ARMSimCommand = cast(str, self.settings.value("ARMSimCommand") or "")
            if ARMSimCommand.count("ruby") != 0:
                self.settings.setValue("ARMSimCommand", self.defaultSettings.value("ARMSimCommandPython"))
                self.settings.setValue("ARMSimDirectory", self.defaultSettings.value("ARMSimDirectoryPython"))
            conf_version = 4
        if conf_version < 5:
            # Version 4 -> external Python server was the only option
            # Version 5 -> in-process module backend added; set as default
            self.settings.setValue("ARMSimBackend", "module")
            conf_version = 5
        if conf_version < 6:
            # Version 5 -> single ARMSimCommand / ARMSimDirectory shared by python and ruby
            # Version 6 -> per-backend keys: ARMSimCommandPython/Ruby, ARMSimDirectoryPython/Ruby
            old_cmd = cast(str, self.settings.value("ARMSimCommand") or "")
            old_dir = cast(str, self.settings.value("ARMSimDirectory") or "")
            self.settings.setValue("ARMSimCommandPython", old_cmd or self.defaultSettings.value("ARMSimCommandPython"))
            self.settings.setValue("ARMSimDirectoryPython", old_dir or self.defaultSettings.value("ARMSimDirectoryPython"))
            self.settings.setValue("ARMSimCommandRuby", self.defaultSettings.value("ARMSimCommandRuby"))
            self.settings.setValue("ARMSimDirectoryRuby", self.defaultSettings.value("ARMSimDirectoryRuby"))
            conf_version = 6
        # -----------------------------------------------------------------------------
        # End migration of settings versions
        # -----------------------------------------------------------------------------
        self.settings.setValue("ConfVersion", 6)
        # If some of the next settings is empty, populate it with its default value
        for setting in (
                "ARMSimBackend",
                "ARMSimCommandPython", "ARMSimDirectoryPython",
                "ARMSimCommandRuby", "ARMSimDirectoryRuby",
                "ARMSimServer", "ARMSimPort", "ARMSimUseLabels",
                "ARMGccCommand", "ARMGccOptions",
                "LastUsedDirectory", "TerminalHistory", "ColorTheme", "FontSize"):
            if self.settings.value(setting) is None:
                self.settings.setValue(setting, self.defaultSettings.value(setting))
        save_default_style()
        theme = str(self.settings.value("ColorTheme") or SYSTEM)
        apply_theme(theme)
        dark = theme == DARK
        self._applyEditorTheme(dark)
        self._applyIconTheme(dark)
        self._applyFontSize()
        # Validate per-backend command/directory; reset to defaults if invalid
        if not os.path.exists(
                os.path.join(cast(str, self.settings.value("ARMSimDirectoryPython")), "server.py")):
            self.settings.setValue("ARMSimCommandPython", self.defaultSettings.value("ARMSimCommandPython"))
            self.settings.setValue("ARMSimDirectoryPython", self.defaultSettings.value("ARMSimDirectoryPython"))
        if not os.path.exists(
                os.path.join(cast(str, self.settings.value("ARMSimDirectoryRuby")), "server.rb")):
            self.settings.setValue("ARMSimCommandRuby", self.defaultSettings.value("ARMSimCommandRuby"))
            self.settings.setValue("ARMSimDirectoryRuby", self.defaultSettings.value("ARMSimDirectoryRuby"))
        # If the gcc command is not a regular file, change the ARMGccCommand by the default one
        ARMGccCommandSetting: str = "ARMGccCommand"
        if not os.path.isfile(cast(str, self.settings.value(ARMGccCommandSetting))):
            self.settings.setValue(ARMGccCommandSetting, self.defaultSettings.value(ARMGccCommandSetting))

    def defaultGeometry(self) -> QtCore.QByteArray:
        """Resizes the main window to 800x600 and returns the geometry"""
        self.resize(800, 600)
        return self.saveGeometry()

    def isSourceCodeModified(self) -> bool:
        """Asks sourceCodeEditor if its contents have been modified"""
        return self.ui.sourceCodeEditor.document().isModified()

    def updateWindowTitle(self) -> None:
        modified_txt = self.tr(" [modified] - ") if self.isSourceCodeModified() else " - "
        title_txt = "{}{}{}".format(os.path.basename(self.fileName), modified_txt, "QtARMSim")
        self.setWindowTitle(title_txt)

    def updateFileActions(self) -> None:
        """Enables/disables actions related to file management and updates window title accordingly"""
        if self.isSourceCodeModified():
            self.ui.actionSave.setEnabled(True)
            self.ui.actionSave_As.setEnabled(True)
        else:
            self.ui.actionSave.setEnabled(False)
            self.ui.actionSave_As.setEnabled(True)
        self.updateWindowTitle()

    def updateEditActions(self, onSimulator: bool=False) -> None:
        """Enables/disables actions related to edit menu"""
        self.ui.action_Undo.setEnabled(not onSimulator and self.editorFlags['undoAvailable'])
        self.ui.actionRedo.setEnabled(not onSimulator and self.editorFlags['redoAvailable'])
        self.ui.actionCut.setEnabled(not onSimulator and self.editorFlags['selectionAvailable'])
        self.ui.actionCopy.setEnabled(not onSimulator and self.editorFlags['selectionAvailable'])
        self.ui.actionPaste.setEnabled(not onSimulator and QtWidgets.QApplication.clipboard().text() != '')
        self.ui.actionSelect_All.setEnabled(not onSimulator)

    def updateViewActions(self) -> None:
        """Modifies the checked state of the show/hide actions depending on their widget visibility"""
        self.ui.actionShow_Statusbar.setChecked(self.ui.statusBar.isVisible())
        self.ui.actionShow_Toolbar.setChecked(self.ui.toolBar.isVisible())
        self.ui.actionShow_Registers.setChecked(self.ui.dockWidgetRegisters.isVisible())
        self.ui.actionShow_Memory.setChecked(self.ui.dockWidgetMemory.isVisible())
        self.ui.actionShow_Memory_Dump.setChecked(self.ui.dockWidgetMemoryDump.isVisible())
        self.ui.actionShow_LCD.setChecked(self.ui.dockWidgetLCD.isVisible())
        self.ui.actionShow_Terminal.setChecked(self.ui.dockWidgetTerminal.isVisible())
        self.ui.actionShow_Simulator_Output.setChecked(self.ui.dockWidgetSimulatorOutput.isVisible())
        self.ui.actionShow_Messages.setChecked(self.ui.dockWidgetMessages.isVisible())
        self.ui.actionFull_Screen_Mode.setChecked(self.isFullScreen())

    def enableSimulatorActions(self, onSimulator: bool) -> None:
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

    def clearBreakpoints(self) -> None:
        """
        Clears breakpoints on simulator, on simCodeEditor, and on myself
        """
        if self.simulator and self.simulator.connected:
            _ = self.simulator.clearBreakpoints()
        for simCodeEditor in self.ui.simCodeEditors:
            simCodeEditor.clearBreakpoints()
        self.breakpoints.clear()

    def startSpinner(self) -> None:
        """
        Centers the spinner on the central widget and shows it
        """
        centralwidgetQRect = self.ui.centralwidget.geometry()
        spinnerLabelQRect = self.spinnerLabel.geometry()
        spinnerLabelQRect.moveTo(QtCore.QPoint(centralwidgetQRect.x() + centralwidgetQRect.width() // 2,
                                               centralwidgetQRect.y() + centralwidgetQRect.height() // 2))
        self.spinnerLabel.setGeometry(spinnerLabelQRect)
        self.spinnerLabel.show()
        self.spinnerLabel.movie().start()
        self.update()

    def stopSpinner(self) -> None:
        """
        Hides the spinner
        """
        self.spinnerLabel.hide()
        self.spinnerLabel.movie().stop()

    #################################################################################
    # Actions and events
    #################################################################################

    def connectActions(self) -> None:
        """Connects the actions with their correspondent methods"""
        # Automatically assign actions to methods using their names
        for actionName in dir(self.ui):
            if actionName.startswith('action'):
                methodName = 'do{}'.format(actionName[6:])
                try:
                    method = cast(Callable[..., None], getattr(self, methodName))
                except AttributeError:
                    if self.verbose:
                        print("Method: {} not implemented yet!".format(methodName))
                    continue
                action = cast(QAction, getattr(self.ui, actionName))
                _ = action.triggered.connect(method)
        # Tab changes
        _ = self.ui.tabWidgetCode.currentChanged.connect(self.onTabChange)
        # Clipboard changes
        _ = QtWidgets.QApplication.clipboard().changed.connect(self.updateEditActions)
        # sourceCodeEditor modification changes
        _ = self.ui.sourceCodeEditor.textChanged.connect(self.sourceCodeChanged)
        _ = self.ui.sourceCodeEditor.selectionChanged.connect(self.sourceCodeSelectionChanged)
        _ = self.ui.sourceCodeEditor.redoAvailable.connect(self.sourceCodeRedoAvailable)
        _ = self.ui.sourceCodeEditor.undoAvailable.connect(self.sourceCodeUndoAvailable)
        _ = self.ui.sourceCodeEditor.highlightedWordSignal.connect(self.highlightedWord)
        # Install event filter for dock widgets
        self.ui.dockWidgetRegisters.installEventFilter(self)
        self.ui.dockWidgetMemory.installEventFilter(self)
        self.ui.dockWidgetMemoryDump.installEventFilter(self)
        self.ui.dockWidgetLCD.installEventFilter(self)
        self.ui.dockWidgetTerminal.installEventFilter(self)
        self.ui.dockWidgetSimulatorOutput.installEventFilter(self)
        self.ui.dockWidgetMessages.installEventFilter(self)
        # Connect to self.uji.simCodeEditor set and clear breakpoint signals and highlightedWord signal
        for simCodeEditor in self.ui.simCodeEditors:
            _ = simCodeEditor.setBreakpointSignal.connect(self.setBreakpoint)
            _ = simCodeEditor.clearBreakpointSignal.connect(self.clearBreakpoint)
            _ = simCodeEditor.highlightedWordSignal.connect(self.highlightedWord)
        # Connect register edited on registers' model to self.registerEdited
        assert self.registersModel is not None
        _ = self.registersModel.registerEdited.connect(self.registerEdited)
        # Connect memory edited on the memory model to self.memoryEdited
        assert self.memoryModel is not None
        _ = self.memoryModel.memoryEdited.connect(self.memoryEdited)
        # Connect Terminal push button and Terminal line edit return to send line to simulator
        _ = self.ui.pushButtonTerminal.pressed.connect(self.sendLineToSimulator)
        _ = self.ui.lineEditTerminal.returnPressed.connect(self.sendLineToSimulator)

    @override
    def eventFilter(self, source: QObject, event: QtCore.QEvent) -> bool:
        if event.type() == QtCore.QEvent.Type.Close and isinstance(source, QtWidgets.QDockWidget):
            if source is self.ui.dockWidgetRegisters:
                self.ui.actionShow_Registers.setChecked(False)
            elif source is self.ui.dockWidgetMemory:
                self.ui.actionShow_Memory.setChecked(False)
            elif source is self.ui.dockWidgetMemoryDump:
                self.ui.actionShow_Memory_Dump.setChecked(False)
            elif source is self.ui.dockWidgetLCD:
                self.ui.actionShow_LCD.setChecked(False)
            elif source is self.ui.dockWidgetTerminal:
                self.ui.actionShow_Terminal.setChecked(False)
            elif source is self.ui.dockWidgetSimulatorOutput:
                self.ui.actionShow_Simulator_Output.setChecked(False)
            elif source is self.ui.dockWidgetMessages:
                self.ui.actionShow_Messages.setChecked(False)
        if event.type() == QtCore.QEvent.Type.KeyPress and source == self.ui.dockWidgetTerminal:
            if isinstance(event, QKeyEvent):
                if event.key() == Qt.Key.Key_Up:
                    self.ui.lineEditTerminal.setText(self.terminalHistoryUp())
                    return True
                elif event.key() == Qt.Key.Key_Down:
                    self.ui.lineEditTerminal.setText(self.terminalHistoryDown())
                    return True
        return super().eventFilter(source, event)

    def onTabChange(self, tabIndex: int) -> None:
        """
        Actions to be performed when the user changes from the edit tab to the simulator one
        """
        if tabIndex == 1:
            # Check if source code has to be saved or not
            if self.checkCurrentFileState() == QtWidgets.QMessageBox.StandardButton.Cancel:
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
                msg = "It seems that there is no source code to assemble.\n" + \
                      "Do you really want to proceed?"
                reply = QtWidgets.QMessageBox.question(self, 'Empty source code?',
                                                       msg,
                                                       QtWidgets.QMessageBox.StandardButton.Yes,
                                                       QtWidgets.QMessageBox.StandardButton.No)
                if reply == QtWidgets.QMessageBox.StandardButton.No:
                    self.ui.tabWidgetCode.setCurrentIndex(0)
                    return
            #   2) Assembly self.fileName
            self.doAssemble()
        else:
            self.enableSimulatorActions(False)
            self.ui.sourceCodeEditor.setFocus()

    def assembled(self, has_been_assembled: bool) -> None:
        if has_been_assembled:
            self.current_source_code_assembled = True
            self.enableSimulatorActions(True)
            self.ui.textEditMessages.append(self.tr("<b>{} assembled.</b>\n").format(self.fileName))
        else:
            self.current_source_code_assembled = False
            self.enableSimulatorActions(False)
            self.ui.tabWidgetCode.setCurrentIndex(0)

    def doAssemble(self) -> None:
        # If not connected, connect to the simulator
        if not self.simulator or (self.simulator and not self.simulator.connected):
            if not self.connectToARMSim():
                self.assembled(False)
                return
        assert self.simulator is not None
        # Check that self.fileName exists
        if not os.path.exists(self.fileName):
            strerror = self.tr('File not found')
            _ = QtWidgets.QMessageBox.warning(self, self.tr("Assemble File"), "{}: '{}'.".format(strerror, self.fileName))
            self.assembled(False)
            return
        # Assemble self.fileName
        response = self.simulator.doAssemble(self.fileName)
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
                self.ui.textEditMessages.append(self.tr("Something went wrong. Expected response not received."))
                self.simulator.disconnect_from()
            self.ui.textEditMessages.append("")
            msg = self.tr("An error has occurred when assembling the source code.\n" + \
                               "Please, see the Messages panel for more details.")
            _ = QtWidgets.QMessageBox.warning(self, self.tr("Assembly Error"), msg)

    def sourceCodeChanged(self) -> None:
        self.current_source_code_assembled = False
        self.updateFileActions()

    def sourceCodeSelectionChanged(self) -> None:
        self.editorFlags['selectionAvailable'] = self.ui.sourceCodeEditor.textCursor().selectedText() != ''
        self.updateEditActions()

    def sourceCodeRedoAvailable(self, redoAvailable: bool) -> None:
        self.editorFlags['redoAvailable'] = redoAvailable
        self.updateEditActions()

    def sourceCodeUndoAvailable(self, undoAvailable: bool) -> None:
        self.editorFlags['undoAvailable'] = undoAvailable
        self.updateEditActions()

    def setBreakpoint(self, _: int, text: str) -> None:
        """Sets a breakpoint on the memory address obtained from the variable text"""
        assert self.simulator is not None
        hex_address = text.split(" ")[0][1:-1]
        errmsg = self.simulator.setBreakpoint(hex_address)
        if errmsg:
            _ = QtWidgets.QMessageBox.warning(self, self.tr("Set breakpoint error"), errmsg)
        else:
            self.breakpoints.append(hex_address)

    def clearBreakpoint(self, _: int, text: str) -> None:
        """Clears a breakpoint from the memory address obtained from the variable text"""
        assert self.simulator is not None
        hex_address = text.split(" ")[0][1:-1]
        errmsg = self.simulator.clearBreakpoint(hex_address)
        if errmsg:
            _ = QtWidgets.QMessageBox.warning(self, self.tr("Clear breakpoint error"), errmsg)
        else:
            self.breakpoints.remove(hex_address)

    reg_text_to_number: dict[str, int] = dict([("r{}".format(n), n) for n in range(16)])
    reg_text_to_number['sp'] = 13
    reg_text_to_number['lr'] = 14
    reg_text_to_number['pc'] = 15

    def highlightedWord(self, text: str) -> None:
        """Reacts upon a highlighted word in any code editor"""
        registersModel = self.registersModel
        assert registersModel is not None
        if text.lower() in self.reg_text_to_number:
            registersModel.highlightRegister(self.reg_text_to_number[text.lower()])
        else:
            registersModel.unHighlightRegister()

    def registerEdited(self, reg_name: str, hex_value: str) -> None:
        assert self.simulator is not None
        errmsg = self.simulator.setRegister(reg_name, hex_value)
        if errmsg:
            _ = QtWidgets.QMessageBox.warning(self, self.tr("Set Register Error"), errmsg)
        self.highlight_pc_line()

    def memoryEdited(self, hex_address: str, hex_value: str) -> None:
        assert self.simulator is not None
        errmsg = self.simulator.setMemory(hex_address, hex_value)
        if errmsg:
            _ = QtWidgets.QMessageBox.warning(self, self.tr("Set Memory Error"), errmsg)

    def checkCurrentFileState(self) -> QtWidgets.QMessageBox.StandardButton:
        if not self.isSourceCodeModified():
            return QtWidgets.QMessageBox.StandardButton.Discard
        msg: str = "The document '{}' has been modified.\n".format(os.path.basename(self.fileName)) + \
                    "Do you want to save the changes?"
        reply = QtWidgets.QMessageBox.question(self, 'Close Document',
                                               msg,
                                               QtWidgets.QMessageBox.StandardButton.Save
                                               | QtWidgets.QMessageBox.StandardButton.Discard
                                               | QtWidgets.QMessageBox.StandardButton.Cancel,
                                               QtWidgets.QMessageBox.StandardButton.Save)
        if reply == QtWidgets.QMessageBox.StandardButton.Save:
            _ = self.doSave()
        return reply

    #################################################################################
    # File menu actions
    #################################################################################

    def setFileName(self, fileName: str) -> None:
        """Sets the filename and updates the window title accordingly"""
        self.fileName = fileName if fileName else self.tr("untitled.s")
        self.ui.sourceCodeEditor.document().setModified(False)
        self.updateFileActions()

    def doNew(self) -> None:
        """Creates a new file"""
        if self.checkCurrentFileState() == QtWidgets.QMessageBox.StandardButton.Cancel:
            return
        # 1) Change to tab 0
        self.ui.tabWidgetCode.setCurrentIndex(0)
        # 2) Set the filename to the default untitled name
        self.setFileName("")
        # 3) Clear sourceCodeEditor
        self.ui.sourceCodeEditor.clear()
        # 4) Clear breakpoints when creating a new file
        self.clearBreakpoints()

    def _getDirectory(self) -> str:
        directory: str = cast(str, self.settings.value("LastUsedDirectory"))
        if not os.path.isdir(directory):
            directory = self.defaultSettings.value("LastUsedDirectory")
        return directory

    def doOpen(self) -> None:
        """Opens an ARM assembler file"""
        if self.checkCurrentFileState() == QtWidgets.QMessageBox.StandardButton.Cancel:
            return
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, self.tr("Open File"),
                                                            self._getDirectory(),
                                                            self.tr("ARM assembler files (*.s);;ARM C files (*.c)"))
        if not fileName:
            return
        self.readFile(fileName)
        # Change to tab 0
        self.ui.tabWidgetCode.setCurrentIndex(0)
        # Clear breakpoints for the new read file
        self.clearBreakpoints()
        # Update LastUsedDirectory setting
        self.settings.setValue("LastUsedDirectory", os.path.dirname(fileName))

    def doOpenExample(self, action: QAction) -> None:
        """Opens an example file"""
        if self.checkCurrentFileState() == QtWidgets.QMessageBox.StandardButton.Cancel:
            return
        fileName: str = cast(str, action.data())
        if fileName:
            tmp_dir = tempfile.mkdtemp(".qtarmsim")
            fileNameInTmp = os.path.join(tmp_dir, os.path.basename(fileName))
            _ = shutil.copyfile(fileName, fileNameInTmp)
            self.readFile(fileNameInTmp)
            # Change to tab 0
            self.ui.tabWidgetCode.setCurrentIndex(0)
            # Clear breakpoints for the new read file
            self.clearBreakpoints()
            # Do not update LastUsedDirectory setting
            pass

    def readFile(self, fileName: str) -> None:
        """Reads a file. Can be called using an argument from the command line"""
        text = ''
        encodings = ['utf-8', 'latin1', 'ascii']
        for i in range(len(encodings)):
            try:
                f = open(fileName, encoding=encodings[i])
            except FileNotFoundError as e:
                _ = QtWidgets.QMessageBox.warning(self, self.tr("Open File"), "{}: '{}'.".format(e.strerror, fileName))
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
                _ = QtWidgets.QMessageBox.warning(self, self.tr("Error reading '{}'").format(os.path.basename(fileName)), err_msg)
                if i == len(encodings) - 1:
                    raise e
        if fileName[-2:] == '.c':
            self.ui.sourceCodeEditor.setCMode()
        else:
            self.ui.sourceCodeEditor.setARMMode()
        self.ui.sourceCodeEditor.setPlainText(text)
        self.setFileName(fileName)

    def doSave(self) -> bool:
        """Saves the current ARM assembler file"""
        # Set current source code has been assembled to False
        self.current_source_code_assembled = False
        # Save file
        if self.fileName == self.tr("untitled.s"):
            return self.doSave_As()
        else:
            return self.saveFile(self.fileName)

    def doSave_As(self) -> bool:
        """Saves the ARM assembler file with a new specified name"""
        assert (self.fileName != "")
        newFileName = self.fileName
        if os.path.dirname(newFileName) == '':
            newFileName = os.path.join(self._getDirectory(), newFileName)
        newFileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, self.tr("Save File"),
                                                               newFileName,
                                                               self.tr("ARM assembler files (*.s);;ARM C files (*.c)"))
        assert isinstance(newFileName, str)
        if newFileName != '':
            return self.saveFile(newFileName)
        else:
            return False

    def saveFile(self, fileName: str) -> bool:
        """Saves the contents of the source editor on the given file name"""
        asm_file = QtCore.QFile(fileName)
        if not asm_file.open(QtCore.QFile.OpenModeFlag.WriteOnly | QtCore.QFile.OpenModeFlag.Text):
            _ = QtWidgets.QMessageBox.warning(self,
                                              self.tr("Error"),
                                              self.tr("Could not write to file '{0}':\n{1}.")
                                              .format(fileName, asm_file.errorString()))
            return False
        text = self.ui.sourceCodeEditor.document().toPlainText()
        # Force a new line at the end of the file
        text += '\n'
        text = re.sub('\n+$', '\n', text)
        # @todo: let user decide which encoding (including sys.getdefaultencoding())
        _ = asm_file.write(text.encode('utf-8'))
        asm_file.close()
        self.statusBar().showMessage(self.tr("File saved"), 2000)
        # Set filename
        self.setFileName(fileName)
        # Update LastUsedDirectory setting
        self.settings.setValue("LastUsedDirectory", os.path.dirname(fileName))
        # Return
        return True

    def doPrint(self) -> None:
        """Prints the current ARM assembler source file or the disassembled code"""
        printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.PrinterMode.HighResolution)
        printDialog = QtPrintSupport.QPrintDialog(printer, self)
        printDialog.setOption(QtPrintSupport.QAbstractPrintDialog.PrintDialogOption.PrintToFile, True)
        if printDialog.exec() == QDialog.DialogCode.Accepted:
            if self.ui.tabWidgetCode.currentIndex() == 0:
                self.ui.sourceCodeEditor.print_(printer)
            else:
                cast(ARMCodeEditor, self.ui.tabTabARMSim.currentWidget()).print_(printer)

    def doQuit(self) -> None:
        """Quits the program"""
        _ = self.close()

    #################################################################################
    # Edit menu actions
    #################################################################################

    def do_Undo(self) -> None:
        self.ui.sourceCodeEditor.undo()

    def doRedo(self) -> None:
        self.ui.sourceCodeEditor.redo()

    def doCut(self) -> None:
        self.ui.sourceCodeEditor.cut()

    def doCopy(self) -> None:
        self.ui.sourceCodeEditor.copy()

    def doPaste(self) -> None:
        self.ui.sourceCodeEditor.paste()

    def doSelect_All(self) -> None:
        self.ui.sourceCodeEditor.selectAll()

    #################################################################################
    # Run menu actions
    #################################################################################

    def highlight_pc_line(self) -> None:
        assert self.registersModel is not None
        PC = self.registersModel.getRegister(15)
        for simCodeEditor in self.ui.simCodeEditors:
            document = simCodeEditor.document()
            cursor = QtGui.QTextCursor(document)
            cursor = document.find(QtCore.QRegularExpression("^\\[{}\\]".format(PC)), cursor,
                                   QtGui.QTextDocument.FindFlag.FindWholeWords)
            if cursor:
                simCodeEditor.setCurrentHighlightedLineNumber(cursor.blockNumber())
                self.ui.tabTabARMSim.setCurrentWidget(simCodeEditor)
                break

    def _processExecutionResponse(self, response: ExecuteResponse) -> None:
        registersModel = self.registersModel
        memoryModel = self.memoryModel
        assert registersModel is not None
        assert memoryModel is not None
        self.ui.textEditMessages.append(response.assembly_line)
        self.updateFlags()
        for (reg_number, reg_value) in response.registers:
            registersModel.setRegister(reg_number, reg_value)
        for (hex_address, hex_byte) in response.memory:
            memoryModel.setByte(hex_address, hex_byte)
            self.ui.treeViewMemory.expand(
                cast(MemoryByWordProxyModel, self.ui.treeViewMemory.model()).mapFromSource(memoryModel.parent(memoryModel.getIndex(hex_address))))
            self.ui.treeViewMemory.scrollTo(
                cast(MemoryByWordProxyModel, self.ui.treeViewMemory.model()).mapFromSource(memoryModel.getIndex(hex_address)))
        if response.result == "ERROR":
            self.ui.textEditMessages.append("<b>An error has occurred.</b>")
        elif response.result == "BREAKPOINT REACHED":
            self.ui.textEditMessages.append("Breakpoint reached.")
        elif response.result == "END OF PROGRAM":
            self.ui.textEditMessages.append("End of program reached.")
        if response.errmsg:
            self.ui.textEditMessages.append(response.errmsg)

    def _doStep(self, simulator_step_callback: Callable[[], ExecuteResponse]) -> None:
        simulator = self.simulator
        registersModel = self.registersModel
        memoryModel = self.memoryModel
        assert simulator is not None
        assert registersModel is not None
        assert memoryModel is not None
        if not simulator.connected:
            return
        registersModel.stepHistory()
        memoryModel.stepHistory()
        response = simulator_step_callback()
        self._processExecutionResponse(response)
        self.highlight_pc_line()

    def doStepInto(self) -> None:
        assert self.simulator is not None
        self._doStep(self.simulator.getExecuteStepInto)

    def doStepOver(self) -> None:
        assert self.simulator is not None
        self._doStep(self.simulator.getExecuteStepOver)

    def doRestart(self) -> None:
        simulator = self.simulator
        assert simulator is not None
        simulator.disconnect_from()
        self.doAssemble()
        # Restore breakpoints
        for hex_address in self.breakpoints:
            _ = simulator.setBreakpoint(hex_address)

    def doRun(self) -> None:
        # @warning: Don't issue RunProgressBarDialog(self.simulator, **parent=self**)
        #           After executing Examples > Registers > add.s the cursor on the editor is lost
        assert self.simulator is not None
        runProgressBarDialog = RunProgressBarDialog(self.simulator)
        if not runProgressBarDialog.exec():
            self.doRestart()
            return
        response = runProgressBarDialog.getResponse()
        self._processExecutionResponse(response)
        self.highlight_pc_line()

    #################################################################################
    # Window menu actions
    #################################################################################

    @staticmethod
    def _doShow(widget: QWidget, action: QAction) -> None:
        if widget.isVisible():
            widget.setHidden(True)
        else:
            widget.setVisible(True)
        action.setChecked(widget.isVisible())

    def doShow_Statusbar(self) -> None:
        """Shows or hides the status bar"""
        self._doShow(self.ui.statusBar, self.ui.actionShow_Statusbar)

    def doShow_Toolbar(self) -> None:
        """Shows or hides the toolbar"""
        self._doShow(self.ui.toolBar, self.ui.actionShow_Toolbar)

    def doShow_Registers(self) -> None:
        """Shows or hides the registers dock widget"""
        self._doShow(self.ui.dockWidgetRegisters, self.ui.actionShow_Registers)

    def doShow_Memory(self) -> None:
        """Shows or hides the Memory dock widget"""
        self._doShow(self.ui.dockWidgetMemory, self.ui.actionShow_Memory)

    def doShow_Memory_Dump(self) -> None:
        """Shows or hides the Memory Dump dock widget"""
        self._doShow(self.ui.dockWidgetMemoryDump, self.ui.actionShow_Memory_Dump)

    def doShow_LCD(self) -> None:
        """Shows or hides the LCD dock widget"""
        self._doShow(self.ui.dockWidgetLCD, self.ui.actionShow_LCD)

    def doShow_Terminal(self) -> None:
        """Shows or hides the Terminal dock widget"""
        self._doShow(self.ui.dockWidgetTerminal, self.ui.actionShow_Terminal)

    def doShow_Simulator_Output(self) -> None:
        """Shows or hides the Simulator Output dock widget"""
        self._doShow(self.ui.dockWidgetSimulatorOutput, self.ui.actionShow_Simulator_Output)

    def doShow_Messages(self) -> None:
        """Shows or hides the Messages dock widget"""
        self._doShow(self.ui.dockWidgetMessages, self.ui.actionShow_Messages)

    def doDefault_Layout(self) -> None:
        """Sets the default layout"""
        _ = self.restoreState(self.initialWindowState)
        # Statusbar is not automatically restored, restore it manually
        self.ui.statusBar.setVisible(True)
        self.updateViewActions()

    def doCompact_Layout(self) -> None:
        """Sets the compact layout"""
        # Hide the next elements
        for widget, action in [
            (self.ui.statusBar, self.ui.actionShow_Statusbar),
            (self.ui.toolBar, self.ui.actionShow_Toolbar),
            (self.ui.dockWidgetMemoryDump, self.ui.actionShow_Memory_Dump),
            (self.ui.dockWidgetLCD, self.ui.actionShow_LCD),
            (self.ui.dockWidgetTerminal, self.ui.actionShow_Terminal),
            (self.ui.dockWidgetSimulatorOutput, self.ui.actionShow_Simulator_Output),
            (self.ui.dockWidgetMessages, self.ui.actionShow_Messages)]:
            widget.setHidden(True)
            action.setChecked(False)
        # Show the next elements
        for widget, action in [
            (self.ui.dockWidgetRegisters, self.ui.actionShow_Registers),
            (self.ui.dockWidgetMemory, self.ui.actionShow_Memory)]:
            widget.setVisible(True)
            action.setChecked(True)
        # Tabify register and memory docks
        self.tabifyDockWidget(self.ui.dockWidgetRegisters, self.ui.dockWidgetMemory)
        self.ui.dockWidgetRegisters.raise_()

    def doFull_Screen_Mode(self, wasMaximized: bool=False) -> None:
        """Toggles full screen mode"""
        if self.isFullScreen():
            if wasMaximized:
                self.showMaximized()
            else:
                self.showNormal()
        else:
            self.showFullScreen()

    _BREEZE_ICON_ACTIONS: list[tuple[str, str]] = [
        ('actionWhats_This',   'help-whatsthis'),
        ('actionAbout_Qt_ARMSim', 'help-about'),
        ('actionHelp',         'help-contents'),
        ('actionAbout_ARMSim', 'help-about'),
        ('actionNew',          'document-new'),
        ('actionOpen',         'document-open'),
        ('actionSave',         'document-save'),
        ('actionSave_As',      'document-save-as'),
        ('actionPrint',        'document-print'),
        ('actionQuit',         'application-exit'),
        ('actionRun',          'system-run'),
        ('actionStepInto',     'debug-step-into'),
        ('action_Undo',        'edit-undo'),
        ('actionRedo',         'edit-redo'),
        ('actionCut',          'edit-cut'),
        ('actionCopy',         'edit-copy'),
        ('actionPaste',        'edit-paste'),
        ('actionSelect_All',   'edit-select-all'),
        ('actionStepOver',     'debug-step-over'),
        ('actionRestart',      'view-refresh'),
    ]

    def _applyIconTheme(self, dark: bool) -> None:
        """Recolor all Breeze toolbar/menu icons for the current theme."""
        prefix = ':themes/breeze_icons/22/'
        for action_name, icon_name in self._BREEZE_ICON_ACTIONS:
            action = getattr(self.ui, action_name, None)
            if action is not None:
                action.setIcon(make_icon(f'{prefix}{icon_name}.svg', dark))

    def _applyEditorTheme(self, dark: bool) -> None:
        """Propagate dark/light mode to all open code editors and the LCD view."""
        self.ui.sourceCodeEditor.setDarkMode(dark)
        for simCodeEditor in self.ui.simCodeEditors:
            simCodeEditor.setDarkMode(dark)
        self.ui.memoryLCDView.setDarkMode(dark)

    def _effective_font_size(self) -> int:
        """Return the configured font size, resolving Auto (0) to system default + 1."""
        size = int(self.settings.value("FontSize") or 0)
        if size < 8:
            orig = get_original_font_size()
            size = max(8, orig + 1)
        return size

    def _applyFontSize(self) -> None:
        """Apply the configured font size to all application fonts, code editors, and data models."""
        size = self._effective_font_size()
        # Set app-wide font (propagates to all widgets)
        app = QtWidgets.QApplication.instance()
        if isinstance(app, QtWidgets.QApplication):
            app_font = app.font()
            app_font.setPointSize(size)
            app.setFont(app_font)
        # Code editors use a monospace font at the same size
        mono_font = getMonoSpacedFont(size)
        self.ui.sourceCodeEditor.applyFont(mono_font)
        for simCodeEditor in self.ui.simCodeEditors:
            simCodeEditor.applyFont(mono_font)
        self.flagsText.setFont(mono_font)
        # Registers model
        if self.registersModel is not None:
            self.registersModel.applyFontSize(size)
        # Memory by-word proxy model
        memory_proxy = self.ui.treeViewMemory.model()
        if isinstance(memory_proxy, MemoryByWordProxyModel):
            memory_proxy.applyFontSize(size)
        # Memory dump proxy models (one per tab)
        for i in range(self.ui.tabWidgetMemoryDump.count()):
            view = self.ui.tabWidgetMemoryDump.widget(i)
            if isinstance(view, QtWidgets.QTableView):
                dump_model = view.model()
                if isinstance(dump_model, MemoryDumpProxyModel):
                    dump_model.applyFontSize(size)
                    view.resizeColumnsToContents()
                    view.resizeRowsToContents()

    def doPreferences(self) -> None:
        preferences = PreferencesDialog(self, self.settings, self.defaultSettings)
        if preferences.exec():
            theme = str(self.settings.value("ColorTheme") or SYSTEM)
            apply_theme(theme)
            dark = theme == DARK
            self._applyEditorTheme(dark)
            self._applyIconTheme(dark)
            self._applyFontSize()
            if self.simulator and self.simulator.connected:
                _ = self.sendSettingsToARMSim()

    @override
    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """Called when the main window is closed. Saves state and performs cleanup actions."""
        if self.checkCurrentFileState() == QtWidgets.QMessageBox.StandardButton.Cancel:
            event.ignore()
            return
        # Save current geometry and window state
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        # Disconnect the simulator
        if self.simulator and self.simulator.connected:
            self.simulator.disconnect_from()
        # Close windows
        _ = self.helpWindow.close()
        # Accept event
        event.accept()

    @override
    def showEvent(self, event: QtGui.QShowEvent) -> None:
        """Method called when the show event is received"""
        super(QtARMSimMainWindow, self).showEvent(event)
        if self.helpWindow.isVisible():
            self.helpWindow.showNormal()

    @override
    def hideEvent(self, event: QtGui.QHideEvent) -> None:
        """Method called when the hide event is received, minimizes the other app windows"""
        super(QtARMSimMainWindow, self).hideEvent(event)
        if self.helpWindow.isVisible():
            self.helpWindow.showMinimized()

    @staticmethod
    def doWhats_This() -> None:
        """Activates the What's This? mode"""
        QtWidgets.QWhatsThis.enterWhatsThisMode()

    def welcome_message(self) -> str:
        return "<b>QtARMSim " + self.tr("version") + " " + __version__ + "</b><br></br>\n" + \
            "(c) 2014-2026 Sergio Barrachina Mir<br></br>\n" + \
            self.tr("Developed at the Jaume I University, Castellón, Spain.<br></br>\n")

    def about_message(self) -> str:
        return "<html>" + \
            "<p><b>" + self.tr("Version") + " " + __version__ + "</b></p>" + \
            "<p>" + "(c) 2014-2026 Sergio Barrachina Mir" + "</p>" + \
            "<p>" + \
            "<a href='https://lorca.act.uji.es/project/qtarmsim/'>https://lorca.act.uji.es/project/qtarmsim/</a>" + \
            "</p>" + \
            "<p></p>" + \
            "<p>" + self.tr("Running on ") + \
            "Python " + platform.python_version() + ", " + \
            "PySide6 " + PySide6.__version__ + ", and " + \
            "Qt " + QtCore.qVersion() + "." + \
            "</p>" + \
            "<hr/>" + \
            self.tr("<p><b>Acknowledgments</b></p>") + \
            "<p></p>" + \
            self.tr(
                "<p>Initial development of QtARMSim was based on the graphical frontend for Spim developed on 2008 by Gloria Edo Piñana.</p>") + \
            self.tr(
                "<p>Most of the ARM keywords and directives used on the assembler editor syntax highlighter are from the listings ARM definition for LaTeX (c) 2013 by Jacques Supcik.</p>") + \
            self.tr("<p>The GUI icons are from the KDE Breeze theme icons.</p>") + \
            self.tr("<p>The LCD font is 'AlphaSmart 3000' by Colonel Sanders.</p>") + \
            self.tr(
                "<p>Software floating point support thanks to <a href='https://www.quinapalus.com/qfplib.html'>Qfplib: an ARM Cortex-M0 floating-point library in 1 kbyte</a>, (c) Mark Owen.</p>") + \
            "</html>"

    def doAbout_Qt_ARMSim(self) -> None:
        """Shows the About QtARMSim dialog"""
        QtWidgets.QMessageBox.about(self,
                                    self.tr("About QtARMSim"),
                                    self.about_message(),
                                    )

    def doAbout_ARMSim(self) -> None:
        """Shows the About ARMSim dialog"""
        assert self.simulator is not None
        QtWidgets.QMessageBox.about(self,
                                    self.tr("About ARMSim"),
                                    self.simulator.getVersion())

    def doHelp(self) -> None:
        """Shows the Help window"""
        self.helpWindow.setVisible(True)

    #################################################################################
    # Communication with ARMSim
    #################################################################################

    def updateFlags(self) -> None:
        assert self.simulator is not None
        (_, hex_value) = self.simulator.getRegister('r16')
        value = int(hex_value, 16)
        N = '<b>N</b>' if value & 2 ** 31 else 'n'
        Z = '<b>Z</b>' if value & 2 ** 30 else 'z'
        C = '<b>C</b>' if value & 2 ** 29 else 'c'
        V = '<b>V</b>' if value & 2 ** 28 else 'v'
        self.flagsText.setText("{} {} {} {}".format(N, Z, C, V))

    def updateRegisters(self) -> None:
        """Updates the registers dock upon ARMSim data."""
        simulator = self.simulator
        assert simulator is not None
        registers_model = cast(RegistersModel, self.ui.treeViewRegisters.model())
        for (reg, hex_value) in simulator.getRegisters():
            registers_model.setRegister(reg, hex_value)
        registers_model.clearHistory()
        self.updateFlags()

    class MemoryBankInfo(TypedDict):
        """Class to store information about a memory bank"""
        memType: str
        hexStart: str
        nBytes: int
        memBytes: list[str]
        armsimLines: list[str]

    class GetMemoryThread(QtCore.QThread):

        memoryBanksReady: QtCore.Signal = QtCore.Signal(list)

        def __init__(self, mainWindow: 'QtARMSimMainWindow') -> None:
            super().__init__()
            self.mainWindow: QtARMSimMainWindow = mainWindow

        @override
        def run(self) -> None:
            simulator = self.mainWindow.simulator
            assert simulator is not None
            memory_banks: list[dict[str, str | list[str] | int]] = []
            for (memType, hexStart, hex_end) in simulator.getMemoryBanks():
                # Dump memory
                start = int(hexStart, 16)
                end = int(hex_end, 16)
                nBytes = end - start
                memBytes: list[str] = []
                for (_, hexByte) in simulator.getMemory(hexStart, nBytes):
                    memBytes.append(hexByte)
                armsimLines: list[str] = []
                # if memType == ROM then load the program into the ARMSim tab
                if memType == 'ROM':
                    nInstructions = int(nBytes / 2)  # Maximum number of instructions in the given ROM
                    armsimLines += ['@@ ----------------------------------------',
                                     '@@ DISASSEMBLED CODE STARTING AT {}'.format(hexStart),
                                     '@@ ----------------------------------------']
                    armsimLines += simulator.getDisassemble(hexStart, nInstructions)
                memory_banks.append({
                    'memType': memType,
                    'hexStart': hexStart,
                    'nBytes': nBytes,
                    'memBytes': memBytes,
                    'armsimLines': armsimLines,
                })
            self.memoryBanksReady.emit(memory_banks)

    def onGetMemoryThreadFinished(self, memory_banks: list[MemoryBankInfo]) -> None:
        # Display the disassembled code
        for simCodeEditor in self.ui.simCodeEditors:
            simCodeEditor.setPlainText('')
            simCodeEditor.setCenterOnScroll(False)
            simCodeEditor.scrollLock = True
            simCodeEditor.clearDecorations()
            simCodeEditor.hide()
        self.ui.tabTabARMSim.clear()
        self.ui.simCodeEditors.clear()
        dark = str(self.settings.value("ColorTheme") or SYSTEM) == DARK
        mono_font = getMonoSpacedFont(self._effective_font_size())
        for mb in memory_banks:
            if mb['armsimLines']:
                simCodeEditor = ARMCodeEditor(self.ui.tabTabARMSim)
                simCodeEditor.applyFont(mono_font)
                simCodeEditor.setDarkMode(dark)
                simCodeEditor.setReadOnly(True)
                simCodeEditor.setCenterOnScroll(False)
                simCodeEditor.scrollLock = True
                _ = simCodeEditor.setBreakpointSignal.connect(self.setBreakpoint)
                _ = simCodeEditor.clearBreakpointSignal.connect(self.clearBreakpoint)
                _ = simCodeEditor.highlightedWordSignal.connect(self.highlightedWord)
                self.ui.simCodeEditors.append(simCodeEditor)
                _ = self.ui.tabTabARMSim.addTab(simCodeEditor, mb['hexStart'])
                n_lines = len(mb['armsimLines'])
                for j in range(0, n_lines // 30 + 1):
                    simCodeEditor.appendPlainText(
                        '\n'.join(mb['armsimLines'][j * 30: min((j + 1) * 30, n_lines)]))
                    QtWidgets.QApplication.processEvents()
                simCodeEditor.scrollLock = False
        self.highlight_pc_line()
        # Stop spinner now
        self.stopSpinner()
        # Process memory info
        memoryModel = self.memoryModel
        assert memoryModel is not None
        # Save expansion state before reset; detect first population
        proxyModel = cast(MemoryByWordProxyModel, self.ui.treeViewMemory.model())
        first_population = memoryModel.getNumberOfMemoryBanks() == 0
        expanded_slots: set[int] = {
            slot for slot in range(memoryModel.getNumberOfMemoryBanks())
            if self.ui.treeViewMemory.isExpanded(proxyModel.index(slot, 0))
        }
        memoryModel.reset()
        self.ui.tabWidgetMemoryDump.clear()
        memoryBank = 0
        dump_font_size = self._effective_font_size()
        for mb in memory_banks:
            # Append the memory bank
            memoryModel.appendMemoryBank(mb['memType'], mb['hexStart'], mb['memBytes'])
            # Add a page to the tabWidgetMemoryDump
            memoryDumpProxyModel = MemoryDumpProxyModel()
            memoryDumpProxyModel.setSourceModel(memoryModel, memoryBank)
            memoryDumpProxyModel.applyFontSize(dump_font_size)
            memoryBank += 1
            memoryDumpView = MemoryDumpView()
            memoryDumpView.setModel(memoryDumpProxyModel)
            memoryDumpView.horizontalHeader().setMinimumSectionSize(1)
            memoryDumpView.verticalHeader().setMinimumSectionSize(1)
            memoryDumpView.resizeColumnsToContents()
            memoryDumpView.resizeRowsToContents()
            _ = self.ui.tabWidgetMemoryDump.addTab(memoryDumpView, "{}".format(mb['memType']))
            QtWidgets.QApplication.processEvents()
        # Focus the first tab on to the RAM
        for i in range(self.ui.tabWidgetMemoryDump.count()):
            if self.ui.tabWidgetMemoryDump.tabText(i) == "RAM":
                self.ui.tabWidgetMemoryDump.setCurrentIndex(i)
                break
        # Set the LCD model now that memory banks are populated
        try:
            self.ui.memoryLCDView.setMemoryModel(memoryModel, '0x20080000', 40, 6)
            self.ui.memoryLCDView.setDarkMode(dark)
        except IndexError:
            pass  # LCD bank is not present in this program
        # Synchronously rebuild the view from the fully populated model
        self.ui.treeViewMemory.reset()
        self.ui.treeViewMemory.geometry_updated = False
        # Restore expansion state: auto-expand the first RAM on the first load, otherwise restore previous state
        if first_population:
            for slot in range(memoryModel.getNumberOfMemoryBanks()):
                if memoryModel.getMemoryBankInSlot(slot).memType == 'RAM':
                    self.ui.treeViewMemory.expand(proxyModel.index(slot, 0))
                    break
        else:
            for slot in expanded_slots:
                if slot < memoryModel.getNumberOfMemoryBanks():
                    self.ui.treeViewMemory.expand(proxyModel.index(slot, 0))
        QtWidgets.QApplication.processEvents()
        # Compute column widths from the monospaced font to avoid measuring only visible rows
        fm = QtGui.QFontMetrics(proxyModel.qFont)
        hex_word_width = fm.horizontalAdvance("0xFFFFFFFF")
        indent = self.ui.treeViewMemory.indentation()
        padding = 8
        self.ui.treeViewMemory.setColumnWidth(0, hex_word_width + 2 * indent + padding)
        self.ui.treeViewMemory.setColumnWidth(1, hex_word_width + padding)
        self.ui.treeViewMemory.setColumnWidthHint(0, "0xFFFFFFFF", 2 * indent + padding)
        self.ui.treeViewMemory.setColumnWidthHint(1, "0xFFFFFFFF", padding)
        QtWidgets.QApplication.processEvents()
        # Measure at runtime the overhead added by dock borders and layout margins
        dock_overhead = max(0, self.ui.dockWidgetMemory.width() - self.ui.treeViewMemory.width())
        tree_width = (self.ui.treeViewMemory.columnWidth(0)
                      + self.ui.treeViewMemory.columnWidth(1)
                      + self.ui.treeViewMemory.verticalScrollBar().sizeHint().width())
        self.resizeDocks([self.ui.dockWidgetMemory], [tree_width + dock_overhead], Qt.Orientation.Horizontal)

    def updateMemory(self) -> None:
        """Updates the memory widgets upon ARMSim data."""
        self.getMemoryThread.start()

    def connectToARMSim(self) -> bool:
        backend = cast(str, self.settings.value("ARMSimBackend") or "module")
        # Resolve backend-specific command/directory (empty strings for module backend)
        if backend == "python":
            armsim_command   = cast(str, self.settings.value("ARMSimCommandPython") or "")
            armsim_directory = cast(str, self.settings.value("ARMSimDirectoryPython") or "")
        elif backend == "ruby":
            armsim_command   = cast(str, self.settings.value("ARMSimCommandRuby") or "")
            armsim_directory = cast(str, self.settings.value("ARMSimDirectoryRuby") or "")
        else:
            armsim_command   = ""
            armsim_directory = ""
        # For external server backends, check that the command is configured
        if backend != "module" \
                and self.settings.value("ARMSimServer") in ('localhost', '127.0.0.1') \
                and not armsim_command:
            _ = QtWidgets.QMessageBox.warning(self, self.tr("ARMSim command empty"),
                                              self.tr("ARMSim command is empty.\n\n" +
                                                      "Please go to 'Edit, Preferences...' and set it.\n"))
            return False
        if not os.path.isfile(cast(str, self.settings.value("ARMGccCommand"))):
            _ = QtWidgets.QMessageBox.warning(self, self.tr("ARM gcc not found"),
                                              self.tr("ARM gcc command not found.\n\n" +
                                                      "Please go to 'Edit, Preferences...' and set it.\n"))
            return False
        if backend == "module":
            self.simulator = ARMSimModuleConnector(verbose=self.verbose)
        else:
            self.simulator = ARMSimConnector(verbose=self.verbose)
        simulator = self.simulator
        assert simulator is not None
        if self.debug:
            _ = simulator.mySocket.sentLine.connect(self.sentLineToSimulator)
            _ = simulator.mySocket.receivedLine.connect(self.receivedLineFromSimulator)
            _ = simulator.stdoutLine.connect(self.stdoutLineFromSimulator)
        self.statusBar().showMessage(self.tr("Connecting to ARMSim..."), 2000)
        connectProgressBarDialog = ConnectProgressBarDialog(simulator,
                                                            armsim_command,
                                                            armsim_directory,
                                                            cast(str, self.settings.value("ARMSimServer")),
                                                            int(cast(str, self.settings.value("ARMSimPort"))),
                                                            self
                                                            )
        if not connectProgressBarDialog.exec():
            return False
        errmsg = connectProgressBarDialog.getMsg()
        if errmsg:
            _ = QtWidgets.QMessageBox.warning(self, self.tr("Connection to ARMSim failed"), "{}".format(errmsg))
            return False
        self.ui.textEditMessages.append(u"<b>Connected to ARMSim (ARMSim version info follows).</b><br/>")
        self.ui.textEditMessages.append(simulator.getVersion())
        self.ui.textEditMessages.append("<br/>")
        port = simulator.currentPort
        port_info = self.tr("port {}").format(port) if port is not None else self.tr("built-in module")
        self.statusBar().showMessage(self.tr("Connected to ARMSim ({})").format(port_info), 2000)
        return self.sendSettingsToARMSim()

    def sendSettingsToARMSim(self) -> bool:
        simulator = self.simulator
        assert simulator is not None
        for setting in [("ARMSimUseLabels", "TRUE" if self.settings.value("ARMSimUseLabels") != "0" else "FALSE"),
                        ("ARMGccCommand", self.settings.value("ARMGccCommand")),
                        ("ARMGccOptions", self.settings.value("ARMGccOptions"))]:
            errmsg = simulator.setSettings(setting[0], setting[1])
            if errmsg:
                _ = QtWidgets.QMessageBox.warning(self, self.tr("ARMSim set settings failed"), "\n{}\n".format(errmsg))
                return False
        return True

    def sentLineToSimulator(self, line: str) -> None:
        self._received_lines_from_simulator = 0
        self.ui.textBrowserTerminal.append('> {}'.format(line))

    def receivedLineFromSimulator(self, line: str) -> None:
        self._received_lines_from_simulator += 1
        if self._received_lines_from_simulator < 10:
            self.ui.textBrowserTerminal.append('{}'.format(line))
        elif self._received_lines_from_simulator == 10:
            self.ui.textBrowserTerminal.append('[...]')

    def sendLineToSimulator(self) -> None:
        if self.simulator:
            line = self.ui.lineEditTerminal.text()
            self.ui.lineEditTerminal.clear()
            sb = self.ui.textBrowserTerminal.verticalScrollBar()
            sb.setValue(sb.maximum())
            self.terminalHistoryPush(line)
            self.simulator.sendCommand(line)

    def stdoutLineFromSimulator(self, line: str) -> None:
        if self.ui.textBrowserSimulatorOutput.isEnabled():
            self.ui.textBrowserSimulatorOutput.append('{}'.format(line))

    def terminalHistoryUp(self) -> str:
        self._terminal_history_cursor -= 1
        terminal_history = cast(str, self.settings.value("TerminalHistory")).split('::')
        if -self._terminal_history_cursor > len(terminal_history):
            self._terminal_history_cursor = -len(terminal_history)
        return terminal_history[self._terminal_history_cursor]

    def terminalHistoryDown(self) -> str:
        self._terminal_history_cursor += 1
        if self._terminal_history_cursor >= 0:  # new line (not in history)
            self._terminal_history_cursor = 0
            return ""
        else:
            terminal_history = cast(str, self.settings.value("TerminalHistory")).split('::')
            return terminal_history[self._terminal_history_cursor]

    def terminalHistoryPush(self, line: str) -> None:
        self._terminal_history_cursor = 0
        terminal_history = cast(str, self.settings.value("TerminalHistory")).split('::')
        terminal_history.append(line)
        if len(terminal_history) > 20:
            terminal_history = terminal_history[-20:]
        self.settings.setValue("TerminalHistory", '::'.join(terminal_history))
