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


from PySide2 import QtGui, QtCore, QtWidgets

from ..ui.preferences import Ui_PreferencesDialog


class PreferencesDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_PreferencesDialog()
        self.ui.setupUi(self)
        self.setFromSettings(self.parent().settings)
        self.connect(self.ui.pushButtonARMSimRestoreDefaults, QtCore.SIGNAL('clicked()'), self.restoreARMSimDefaults)
        self.connect(self.ui.toolButtonARMSimDirectory, QtCore.SIGNAL('clicked()'), self.ARMSimDirectoryClicked)
        self.connect(self.ui.toolButtonARMGccCommand, QtCore.SIGNAL('clicked()'), self.ARMGccCommandClicked)

    def setFromSettings(self, settings):
        # ARMSim tab
        self.ui.lineEditARMSimServer.setText(settings.value("ARMSimServer"))
        self.ui.spinBoxARMSimPort.setValue(int(settings.value("ARMSimPort")))
        self.ui.lineEditARMSimCommand.setText(settings.value("ARMSimCommand"))
        self.ui.lineEditARMSimDirectory.setText(settings.value("ARMSimDirectory"))
        self.ui.useLabelsCheckBox.setChecked(settings.value("ARMSimUseLabels") != "0")
        self.ui.lineEditARMGccCommand.setText(settings.value("ARMGccCommand"))
        self.ui.lineEditARMGccOptions.setText(settings.value("ARMGccOptions"))

    def restoreARMSimDefaults(self):
        self.setFromSettings(self.parent().defaultSettings)

    def ARMSimDirectoryClicked(self):
        dirname = self.ui.lineEditARMSimDirectory.text()
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self, self.tr('Select ARMSim working directory'), dirname)
        if dirname != '':
            self.ui.lineEditARMSimDirectory.setText(dirname)

    def ARMGccCommandClicked(self):
        fname = self.ui.lineEditARMGccCommand.text()
        (fname, selectedFilter) = QtWidgets.QFileDialog.getOpenFileName(self, self.tr('Select file'), fname)
        if fname != '':
            self.ui.lineEditARMGccCommand.setText(fname)

    def accept(self):
        s = self.parent().settings
        # ARMSim tab
        s.setValue("ARMSimServer", self.ui.lineEditARMSimServer.text().strip())
        s.setValue("ARMSimPort", self.ui.spinBoxARMSimPort.text().strip())
        s.setValue("ARMSimCommand", self.ui.lineEditARMSimCommand.text().strip())
        s.setValue("ARMSimDirectory", self.ui.lineEditARMSimDirectory.text().strip())
        s.setValue("ARMSimUseLabels", "1" if self.ui.useLabelsCheckBox.isChecked() else "0")
        s.setValue("ARMGccCommand", self.ui.lineEditARMGccCommand.text().strip())
        s.setValue("ARMGccOptions", self.ui.lineEditARMGccOptions.text().strip())
        return super(PreferencesDialog, self).accept()
