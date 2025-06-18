from PySide import QtGui
import sys

def main():
    app     = QtGui.QApplication (sys.argv)
    window       = QtGui.QMainWindow() 
    statusBar    = QtGui.QStatusBar()  
    
    window.setWindowTitle("QStatusBar Add Widgets Example")
    window.resize(300,100)
    window.setStatusBar(statusBar)

    statusBar.addWidget(QtGui.QLabel("Click."),10)
    statusBar.addWidget(QtGui.QLabel("Flags:"),1)
    flagsLabel = QtGui.QLabel("N Z C V")
    flagsLabel.setFrameStyle(QtGui.QFrame.Sunken | QtGui.QFrame.Panel)
    statusBar.addWidget(flagsLabel,0)    
    statusBar.addWidget(QtGui.QPushButton("Error Info"),1)
    window.statusBar().showMessage("Connecting to ARMSim...", 2000)
    window.show()    
    sys.exit(app.exec_())
 
if __name__ == '__main__':
    main()
    