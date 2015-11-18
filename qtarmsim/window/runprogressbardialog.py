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

from PySide import QtGui, QtCore

from .. comm.responses import ExecuteResponse
from .. comm.exceptions import RunTimeOut

class RunProgressBarDialog(QtGui.QDialog):

    def __init__(self, simulator, parent=None):
        self.response = ExecuteResponse()
        super(RunProgressBarDialog, self).__init__(parent)

        self.setWindowTitle("Running...")
        self.layout = QtGui.QVBoxLayout(self)
        
        # Create a label and a progress bar and add them to the main layout
        self.label = QtGui.QLabel(self.trUtf8("Running..."), self)
        self.layout.addWidget(self.label)
        self.progressBar = QtGui.QProgressBar(self)
        self.progressBar.setRange(0,1)
        self.layout.addWidget(self.progressBar)

        # Cancel button        
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel)
        self.layout.addWidget(self.buttonBox)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)

        #button = QtGui.QPushButton("Start", self)
        #self.layout.addWidget(button)      
        #button.clicked.connect(self.a)

        self.myLongTask = RunThread(simulator)
        self.myLongTask.taskFinished.connect(self.onFinished)
        self.progressBar.setRange(0,0)
        self.myLongTask.start()

    def onFinished(self, result, assembly_line, registers, memory, errmsg):
        self.progressBar.setRange(0,1) # Stop the pulsation
        self.response.result = result
        self.response.assembly_line = assembly_line
        self.response.registers = registers
        self.response.memory = memory
        self.response.errmsg = errmsg
        self.accept()

    def getResponse(self):
        return self.response

class RunThread(QtCore.QThread):
    taskFinished = QtCore.Signal(str, str, list, list, str)

    def __init__(self, simulator):
        super(RunThread, self).__init__()
        self.simulator = simulator
        
    def run(self):
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
