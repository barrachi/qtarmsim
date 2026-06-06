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

from ..comm.exceptions import RunTimeOut
from ..comm.responses import ExecuteResponse


class RunProgressBarDialog(QtWidgets.QDialog):

    def __init__(self, simulator, parent: QtWidgets.QWidget | None = None) -> None:
        self.response = ExecuteResponse()
        super(RunProgressBarDialog, self).__init__(parent)

        self.setWindowTitle("Running...")
        self.mainLayout = QtWidgets.QVBoxLayout(self)

        # Create a label and a progress bar and add them to the main layout
        self.label = QtWidgets.QLabel(self.tr("Running..."), self)
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

        self.myLongTask = RunThread(simulator)
        self.myLongTask.taskFinished.connect(self.onFinished)
        self.progressBar.setRange(0, 0)
        self.myLongTask.start()

    def onFinished(self, result: str, assembly_line: str, registers: list[tuple[int, str]], memory: list[tuple[str, str]], errmsg: str) -> None:
        self.progressBar.setRange(0, 1)  # Stop the pulsation
        self.response.result = result
        self.response.assembly_line = assembly_line
        self.response.registers = registers
        self.response.memory = memory
        self.response.errmsg = errmsg
        self.accept()

    def getResponse(self) -> ExecuteResponse:
        return self.response


class RunThread(QtCore.QThread):
    taskFinished = QtCore.Signal(str, str, list, list, str)

    def __init__(self, simulator) -> None:
        super(RunThread, self).__init__()
        self.simulator = simulator

    def run(self) -> None:
        try:
            response = self.simulator.getExecuteAll()
        except RunTimeOut:
            self.taskFinished.emit("ERROR", "", [], [], "Timeout error: maybe an infinite loop?")
            return
        self.taskFinished.emit(response.result,
                               response.assembly_line,
                               response.registers,
                               response.memory,
                               response.errmsg)
