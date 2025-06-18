# Progress bar example
# Adapted from http://stackoverflow.com/questions/19442443/busy-indication-with-pyqt-progress-bar

import sys
import time
from PySide import QtGui, QtCore


class MyCustomWidget(QtGui.QWidget):

    def __init__(self, parent=None):
        super(MyCustomWidget, self).__init__(parent)
        layout = QtGui.QVBoxLayout(self)

        # Create a progress bar and a button and add them to the main layout
        self.progressBar = QtGui.QProgressBar(self)
        self.progressBar.setRange(0,1)
        layout.addWidget(self.progressBar)
        button = QtGui.QPushButton("Start", self)
        layout.addWidget(button)      

        button.clicked.connect(self.onStart)

        self.myLongTask = TaskThread()
        self.myLongTask.taskFinished.connect(self.onFinished)

    def onStart(self): 
        self.progressBar.setRange(0,0)
        self.myLongTask.start()

    def onFinished(self):
        # Stop the pulsation
        self.progressBar.setRange(0,1)


class TaskThread(QtCore.QThread):
    taskFinished = QtCore.pyqtSignal()
    def run(self):
        time.sleep(3)
        self.taskFinished.emit()
        
def main():
    # Create the application
    app = QtGui.QApplication(sys.argv)
    # Create the main window and show it
    main_window = MyCustomWidget()
    main_window.show()
    # Enter the main loop of the application
    sys.exit(app.exec_())
    
        
if __name__ == "__main__":
    main()
