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


from PyQt4 import QtGui, QtCore

from ui.settings import Ui_SettingsDialog

class SettingsDialog(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)
        self.setFromSettings(self.parent().settings)
        self.connect(self.ui.pushButtonARMSimRestoreDefaults, QtCore.SIGNAL('clicked()'), self.restoreARMSimDefaults)
        self.connect(self.ui.toolButtonARMSimCommand, QtCore.SIGNAL('clicked()'), self.ARMSimCommandClicked)
        self.connect(self.ui.toolButtonARMGccCommand, QtCore.SIGNAL('clicked()'), self.ARMGccCommandClicked)
        
    def setFromSettings(self, settings):
        # ARMSim tab
        self.ui.lineEditARMSimCommand.setText(settings.value("ARMSimCommand"))
        self.ui.lineEditARMSimServer.setText(settings.value("ARMSimServer"))
        self.ui.spinBoxARMSimPort.setValue(int(settings.value("ARMSimPort")))
        self.ui.spinBoxARMSimPort.setMinimum(int(settings.value("ARMSimPortMinimum")))
        self.ui.spinBoxARMSimPort.setMaximum(int(settings.value("ARMSimPortMaximum")))
        self.ui.lineEditARMGccCommand.setText(settings.value("ARMGccCommand"))
        self.ui.lineEditARMGccOptions.setText(settings.value("ARMGccOptions"))
    
    def restoreARMSimDefaults(self):
        self.setFromSettings(self.parent().defaultSettings)
        
    def ARMSimCommandClicked(self):
        fname = self.ui.lineEditARMSimCommand.text()
        fname = QtGui.QFileDialog.getOpenFileName(self, self.tr('Open file'), fname)
        self.ui.lineEditARMSimCommand.setText(fname)

    def ARMGccCommandClicked(self):
        fname = self.ui.lineEditARMGccCommand.text()
        fname = QtGui.QFileDialog.getOpenFileName(self, self.tr('Open file'), fname)
        self.ui.lineEditARMGccCommand.setText(fname)

    def accept(self):
        s = self.parent().settings
        # ARMSim tab
        s.setValue("ARMSimCommand", self.ui.lineEditARMSimCommand.text())
        s.setValue("ARMSimServer", self.ui.lineEditARMSimServer.text())
        s.setValue("ARMSimPort", self.ui.spinBoxARMSimPort.text())
        s.setValue("ARMGccCommand", self.ui.lineEditARMGccCommand.text())
        s.setValue("ARMGccOptions", self.ui.lineEditARMGccOptions.text())
        return super(SettingsDialog, self).accept()
    