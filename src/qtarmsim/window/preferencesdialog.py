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

from ..ui.ui_preferences import Ui_PreferencesDialog


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
        self.setFromSettings(self.settings)  # pyright: ignore[reportArgumentType]
        _ = self.ui.pushButtonARMSimRestoreDefaults.clicked.connect(self.restoreARMSimDefaults)
        _ = self.ui.toolButtonARMSimDirectory.clicked.connect(self.ARMSimDirectoryClicked)
        _ = self.ui.toolButtonARMGccCommand.clicked.connect(self.ARMGccCommandClicked)

    def setFromSettings(self, settings: _SettingsReader) -> None:
        # ARMSim tab
        self.ui.lineEditARMSimServer.setText(str(settings.value("ARMSimServer") or ""))
        self.ui.spinBoxARMSimPort.setValue(int(settings.value("ARMSimPort") or 0))
        self.ui.lineEditARMSimCommand.setText(str(settings.value("ARMSimCommand") or ""))
        self.ui.lineEditARMSimDirectory.setText(str(settings.value("ARMSimDirectory") or ""))
        self.ui.useLabelsCheckBox.setChecked(settings.value("ARMSimUseLabels") != "0")
        self.ui.lineEditARMGccCommand.setText(str(settings.value("ARMGccCommand") or ""))
        self.ui.lineEditARMGccOptions.setText(str(settings.value("ARMGccOptions") or ""))

    def restoreARMSimDefaults(self) -> None:
        if self.defaultSettings is not None:
            self.setFromSettings(self.defaultSettings)

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
        s = self.settings
        # ARMSim tab
        s.setValue("ARMSimServer", self.ui.lineEditARMSimServer.text().strip())
        s.setValue("ARMSimPort", self.ui.spinBoxARMSimPort.text().strip())
        s.setValue("ARMSimCommand", self.ui.lineEditARMSimCommand.text().strip())
        s.setValue("ARMSimDirectory", self.ui.lineEditARMSimDirectory.text().strip())
        s.setValue("ARMSimUseLabels", "1" if self.ui.useLabelsCheckBox.isChecked() else "0")
        s.setValue("ARMGccCommand", self.ui.lineEditARMGccCommand.text().strip())
        s.setValue("ARMGccOptions", self.ui.lineEditARMGccOptions.text().strip())
        return super(PreferencesDialog, self).accept()
