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


from PySide import QtGui, QtCore

from .. ui.preferences import Ui_PreferencesDialog

class PreferencesDialog(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
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
        self.ui.lineEditARMGccCommand.setText(settings.value("ARMGccCommand"))
        self.ui.lineEditARMGccOptions.setText(settings.value("ARMGccOptions"))
    
    def restoreARMSimDefaults(self):
        self.setFromSettings(self.parent().defaultSettings)
        
    def ARMSimDirectoryClicked(self):
        dirname = self.ui.lineEditARMSimDirectory.text()
        dirname = QtGui.QFileDialog.getExistingDirectory(self, self.trUtf8('Select ARMSim working directory'), dirname)
        self.ui.lineEditARMSimDirectory.setText(dirname)

    def ARMGccCommandClicked(self):
        fname = self.ui.lineEditARMGccCommand.text()
        fname = QtGui.QFileDialog.getOpenFileName(self, self.trUtf8('Select file'), fname)
        self.ui.lineEditARMGccCommand.setText(fname)

    def accept(self):
        s = self.parent().settings
        # ARMSim tab
        s.setValue("ARMSimServer", self.ui.lineEditARMSimServer.text())
        s.setValue("ARMSimPort", self.ui.spinBoxARMSimPort.text())
        s.setValue("ARMSimCommand", self.ui.lineEditARMSimCommand.text())
        s.setValue("ARMSimDirectory", self.ui.lineEditARMSimDirectory.text())
        s.setValue("ARMGccCommand", self.ui.lineEditARMGccCommand.text())
        s.setValue("ARMGccOptions", self.ui.lineEditARMGccOptions.text())
        return super(PreferencesDialog, self).accept()
    
