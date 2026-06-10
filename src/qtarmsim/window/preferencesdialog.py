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

from typing import Any, Protocol

from PySide6 import QtCore, QtWidgets

from ..theme import DARK, LIGHT, SYSTEM
from ..ui.ui_preferences import Ui_PreferencesDialog


# ── Backend identifiers ──────────────────────────────────────────────────────

BACKEND_MODULE = "module"
BACKEND_PYTHON = "python"
BACKEND_RUBY   = "ruby"

# (display label, settings value) pairs — order determines combo index
_BACKEND_ENTRIES: list[tuple[str, str]] = [
    ("Built-in module (default)", BACKEND_MODULE),
    ("Python server",             BACKEND_PYTHON),
    ("Ruby server",               BACKEND_RUBY),
]


class _SettingsReader(Protocol):
    """Minimal interface shared by QSettings and DefaultSettings."""
    def value(self, name: str, *args: Any, **kwargs: Any) -> Any: ...


class PreferencesDialog(QtWidgets.QDialog):

    def __init__(self, parent: QtWidgets.QWidget, settings: QtCore.QSettings, defaultSettings: _SettingsReader | None = None) -> None:
        QtWidgets.QDialog.__init__(self, parent)
        self.settings = settings
        self.defaultSettings = defaultSettings
        self.ui = Ui_PreferencesDialog()
        self.ui.setupUi(self)
        # Per-backend command/directory buffers (swapped when backend changes)
        self._commandByBackend:   dict[str, str] = {BACKEND_PYTHON: "", BACKEND_RUBY: ""}
        self._directoryByBackend: dict[str, str] = {BACKEND_PYTHON: "", BACKEND_RUBY: ""}
        self._prevBackend: str = BACKEND_MODULE
        # Populate backend combo
        for label, _ in _BACKEND_ENTRIES:
            self.ui.comboBoxARMSimBackend.addItem(label)
        # Populate font-size combo
        self.ui.comboBoxFontSize.addItem("Auto")
        for pt in range(8, 25):
            self.ui.comboBoxFontSize.addItem(str(pt))
        # Load current settings (signal not yet connected; visibility driven explicitly)
        self.setFromSettings(self.settings)  # pyright: ignore[reportArgumentType]
        # Connect signals after initial load to avoid spurious _onBackendChanged calls
        _ = self.ui.pushButtonARMSimRestoreDefaults.clicked.connect(self.restoreARMSimDefaults)
        _ = self.ui.toolButtonARMSimDirectory.clicked.connect(self.ARMSimDirectoryClicked)
        _ = self.ui.toolButtonARMGccCommand.clicked.connect(self.ARMGccCommandClicked)
        _ = self.ui.comboBoxARMSimBackend.currentIndexChanged.connect(self._onBackendChanged)

    # ── Backend helpers ──────────────────────────────────────────────────────

    def _currentBackend(self) -> str:
        idx = self.ui.comboBoxARMSimBackend.currentIndex()
        if 0 <= idx < len(_BACKEND_ENTRIES):
            return _BACKEND_ENTRIES[idx][1]
        return BACKEND_MODULE

    def _setBackend(self, backend: str) -> None:
        for i, (_, value) in enumerate(_BACKEND_ENTRIES):
            if value == backend:
                self.ui.comboBoxARMSimBackend.setCurrentIndex(i)
                return
        self.ui.comboBoxARMSimBackend.setCurrentIndex(0)

    def _setServerFieldsVisible(self, visible: bool) -> None:
        """Show or hide the server/port/command/directory rows."""
        fl = self.ui.formLayout
        fl.setRowVisible(self.ui.labelARMSimServer, visible)
        fl.setRowVisible(self.ui.labelARMSimPort, visible)
        fl.setRowVisible(self.ui.label, visible)
        fl.setRowVisible(self.ui.labelARMSimCommand, visible)

    def _onBackendChanged(self) -> None:
        """Called when the user selects a different backend in the combo."""
        # Save the visible command/directory fields back to the previous backend's buffer
        if self._prevBackend != BACKEND_MODULE:
            self._commandByBackend[self._prevBackend]   = self.ui.lineEditARMSimCommand.text()
            self._directoryByBackend[self._prevBackend] = self.ui.lineEditARMSimDirectory.text()

        new_backend = self._currentBackend()
        self._prevBackend = new_backend

        visible = new_backend != BACKEND_MODULE
        self._setServerFieldsVisible(visible)
        if visible:
            self.ui.lineEditARMSimCommand.setText(self._commandByBackend.get(new_backend, ""))
            self.ui.lineEditARMSimDirectory.setText(self._directoryByBackend.get(new_backend, ""))

    # ── Settings I/O ─────────────────────────────────────────────────────────

    def setFromSettings(self, settings: _SettingsReader) -> None:
        # Load per-backend command/directory buffers
        self._commandByBackend = {
            BACKEND_PYTHON: str(settings.value("ARMSimCommandPython") or ""),
            BACKEND_RUBY:   str(settings.value("ARMSimCommandRuby")   or ""),
        }
        self._directoryByBackend = {
            BACKEND_PYTHON: str(settings.value("ARMSimDirectoryPython") or ""),
            BACKEND_RUBY:   str(settings.value("ARMSimDirectoryRuby")   or ""),
        }
        # Backend selection (block signals so _onBackendChanged doesn't fire mid-load)
        backend = str(settings.value("ARMSimBackend") or BACKEND_MODULE)
        self._prevBackend = backend
        self.ui.comboBoxARMSimBackend.blockSignals(True)
        self._setBackend(backend)
        self.ui.comboBoxARMSimBackend.blockSignals(False)
        self._setServerFieldsVisible(backend != BACKEND_MODULE)
        if backend != BACKEND_MODULE:
            self.ui.lineEditARMSimCommand.setText(self._commandByBackend.get(backend, ""))
            self.ui.lineEditARMSimDirectory.setText(self._directoryByBackend.get(backend, ""))
        # ARMSim server connection fields
        self.ui.lineEditARMSimServer.setText(str(settings.value("ARMSimServer") or ""))
        self.ui.spinBoxARMSimPort.setValue(int(settings.value("ARMSimPort") or 0))
        # Use labels (independent of backend)
        self.ui.useLabelsCheckBox.setChecked(settings.value("ARMSimUseLabels") != "0")
        # Gcc
        self.ui.lineEditARMGccCommand.setText(str(settings.value("ARMGccCommand") or ""))
        self.ui.lineEditARMGccOptions.setText(str(settings.value("ARMGccOptions") or ""))
        # Appearance tab
        theme = str(settings.value("ColorTheme") or SYSTEM)
        self.ui.radioButtonLightTheme.setChecked(theme == LIGHT)
        self.ui.radioButtonDarkTheme.setChecked(theme == DARK)
        self.ui.radioButtonSystemTheme.setChecked(theme not in (LIGHT, DARK))
        stored = str(settings.value("FontSize") or "0")
        idx = self.ui.comboBoxFontSize.findText(stored if stored != "0" else "Auto")
        self.ui.comboBoxFontSize.setCurrentIndex(max(0, idx))

    def restoreARMSimDefaults(self) -> None:
        """Restore defaults for the currently selected backend."""
        if self.defaultSettings is None:
            return
        backend = self._currentBackend()
        if backend == BACKEND_PYTHON:
            cmd  = self.defaultSettings.value("ARMSimCommandPython")
            dir_ = self.defaultSettings.value("ARMSimDirectoryPython")
            self.ui.lineEditARMSimCommand.setText(cmd)
            self.ui.lineEditARMSimDirectory.setText(dir_)
            self._commandByBackend[BACKEND_PYTHON]   = cmd
            self._directoryByBackend[BACKEND_PYTHON] = dir_
        elif backend == BACKEND_RUBY:
            cmd  = self.defaultSettings.value("ARMSimCommandRuby")
            dir_ = self.defaultSettings.value("ARMSimDirectoryRuby")
            self.ui.lineEditARMSimCommand.setText(cmd)
            self.ui.lineEditARMSimDirectory.setText(dir_)
            self._commandByBackend[BACKEND_RUBY]   = cmd
            self._directoryByBackend[BACKEND_RUBY] = dir_
        # Always restore server connection, gcc, and labels from defaults
        self.ui.lineEditARMSimServer.setText(self.defaultSettings.value("ARMSimServer"))
        self.ui.spinBoxARMSimPort.setValue(int(self.defaultSettings.value("ARMSimPort")))
        self.ui.useLabelsCheckBox.setChecked(self.defaultSettings.value("ARMSimUseLabels") != "0")
        self.ui.lineEditARMGccCommand.setText(self.defaultSettings.value("ARMGccCommand"))
        self.ui.lineEditARMGccOptions.setText(self.defaultSettings.value("ARMGccOptions"))

    # ── Slot helpers ─────────────────────────────────────────────────────────

    def ARMSimDirectoryClicked(self) -> None:
        dirname = self.ui.lineEditARMSimDirectory.text()
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self, self.tr('Select ARMSim working directory'), dirname)
        if dirname != '':
            self.ui.lineEditARMSimDirectory.setText(dirname)

    def ARMGccCommandClicked(self) -> None:
        fname = self.ui.lineEditARMGccCommand.text()
        (fname, _) = QtWidgets.QFileDialog.getOpenFileName(self, self.tr('Select file'), fname)
        if fname != '':
            self.ui.lineEditARMGccCommand.setText(fname)

    def accept(self) -> None:
        # Flush the currently visible backend's fields into the buffers before saving
        current = self._currentBackend()
        if current != BACKEND_MODULE:
            self._commandByBackend[current]   = self.ui.lineEditARMSimCommand.text().strip()
            self._directoryByBackend[current] = self.ui.lineEditARMSimDirectory.text().strip()

        s = self.settings
        # ARMSim tab
        s.setValue("ARMSimBackend", current)
        s.setValue("ARMSimServer",  self.ui.lineEditARMSimServer.text().strip())
        s.setValue("ARMSimPort",    self.ui.spinBoxARMSimPort.text().strip())
        s.setValue("ARMSimCommandPython",   self._commandByBackend.get(BACKEND_PYTHON, ""))
        s.setValue("ARMSimDirectoryPython", self._directoryByBackend.get(BACKEND_PYTHON, ""))
        s.setValue("ARMSimCommandRuby",     self._commandByBackend.get(BACKEND_RUBY, ""))
        s.setValue("ARMSimDirectoryRuby",   self._directoryByBackend.get(BACKEND_RUBY, ""))
        s.setValue("ARMSimUseLabels", "1" if self.ui.useLabelsCheckBox.isChecked() else "0")
        s.setValue("ARMGccCommand", self.ui.lineEditARMGccCommand.text().strip())
        s.setValue("ARMGccOptions", self.ui.lineEditARMGccOptions.text().strip())
        # Appearance tab
        if self.ui.radioButtonLightTheme.isChecked():
            s.setValue("ColorTheme", LIGHT)
        elif self.ui.radioButtonDarkTheme.isChecked():
            s.setValue("ColorTheme", DARK)
        else:
            s.setValue("ColorTheme", SYSTEM)
        text = self.ui.comboBoxFontSize.currentText()
        s.setValue("FontSize", "0" if text == "Auto" else text)
        return super(PreferencesDialog, self).accept()
