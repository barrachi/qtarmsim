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

from __future__ import annotations

from PySide6 import QtCore, QtWidgets


class ConnectProgressBarDialog(QtWidgets.QDialog):

    def __init__(self, simulator, ARMSimCommand: str, ARMSimDirectory: str, ARMSimServer: str, ARMSimPort: int, parent: QtWidgets.QWidget | None = None) -> None:
        self.errmsg = ""

        super(ConnectProgressBarDialog, self).__init__(parent)
        self.setWindowTitle("Connecting...")
        self.mainLayout = QtWidgets.QVBoxLayout(self)

        # Create a label and a progress bar and add them to the main layout
        self.label = QtWidgets.QLabel(self.tr("Connecting to ARMSim..."), self)
        self.mainLayout.addWidget(self.label)
        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.setRange(0, 1)
        self.mainLayout.addWidget(self.progressBar)

        # Cancel button        
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        self.mainLayout.addWidget(self.buttonBox)
        _ = self.buttonBox.rejected.connect(self.reject)

        # button = QtWidgets.QPushButton("Start", self)
        # self.mainLayout.addWidget(button)
        # button.clicked.connect(self.a)

        self.myLongTask = ConnectThread(simulator, ARMSimCommand, ARMSimDirectory, ARMSimServer, ARMSimPort)
        self.myLongTask.taskFinished.connect(self.onFinished)
        self.progressBar.setRange(0, 0)
        self.myLongTask.start()

    def onFinished(self, errmsg: str) -> None:
        self.progressBar.setRange(0, 1)  # Stop the pulsation
        self.errmsg = errmsg
        self.accept()

    def getMsg(self) -> str:
        return self.errmsg


class ConnectThread(QtCore.QThread):
    taskFinished = QtCore.Signal(str)

    def __init__(self, simulator, ARMSimCommand: str, ARMSimDirectory: str, ARMSimServer: str, ARMSimPort: int) -> None:
        super(ConnectThread, self).__init__()
        self.simulator = simulator
        self.ARMSimCommand = ARMSimCommand
        self.ARMSimDirectory = ARMSimDirectory
        self.ARMSimServer = ARMSimServer
        self.ARMSimPort = ARMSimPort

    def run(self) -> None:
        errmsg = self.simulator.connectTo(self.ARMSimCommand,
                                          self.ARMSimDirectory,
                                          self.ARMSimServer,
                                          self.ARMSimPort
                                          )
        self.taskFinished.emit(errmsg)
