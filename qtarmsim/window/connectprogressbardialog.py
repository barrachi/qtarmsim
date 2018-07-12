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

# Adapted from:
# http://stackoverflow.com/questions/19442443/busy-indication-with-pyqt-progress-bar

from PySide2 import QtCore, QtWidgets


class ConnectProgressBarDialog(QtWidgets.QDialog):

    def __init__(self, simulator, ARMSimCommand, ARMSimDirectory, ARMSimServer, ARMSimPort, parent=None):
        self.errmsg = ""

        super(ConnectProgressBarDialog, self).__init__(parent)
        self.setWindowTitle("Connecting...")
        self.layout = QtWidgets.QVBoxLayout(self)

        # Create a label and a progress bar and add them to the main layout
        self.label = QtWidgets.QLabel(self.tr("Connecting to ARMSim..."), self)
        self.layout.addWidget(self.label)
        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.setRange(0, 1)
        self.layout.addWidget(self.progressBar)

        # Cancel button        
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel)
        self.layout.addWidget(self.buttonBox)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)

        # button = QtWidgets.QPushButton("Start", self)
        # self.layout.addWidget(button)
        # button.clicked.connect(self.a)

        self.myLongTask = ConnectThread(simulator, ARMSimCommand, ARMSimDirectory, ARMSimServer, ARMSimPort)
        self.myLongTask.taskFinished.connect(self.onFinished)
        self.progressBar.setRange(0, 0)
        self.myLongTask.start()

    def onFinished(self, errmsg):
        self.progressBar.setRange(0, 1)  # Stop the pulsation
        self.errmsg = errmsg
        self.accept()

    def getMsg(self):
        return self.errmsg


class ConnectThread(QtCore.QThread):
    taskFinished = QtCore.Signal(str)

    def __init__(self, simulator, ARMSimCommand, ARMSimDirectory, ARMSimServer, ARMSimPort):
        super(ConnectThread, self).__init__()
        self.simulator = simulator
        self.ARMSimCommand = ARMSimCommand
        self.ARMSimDirectory = ARMSimDirectory
        self.ARMSimServer = ARMSimServer
        self.ARMSimPort = ARMSimPort

    def run(self):
        errmsg = self.simulator.connect(self.ARMSimCommand,
                                        self.ARMSimDirectory,
                                        self.ARMSimServer,
                                        self.ARMSimPort
                                        )
        self.taskFinished.emit(errmsg)
