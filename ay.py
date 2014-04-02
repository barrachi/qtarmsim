# -*- coding: utf-8 -*-

##Módulo ay
#
#Construir la ventana que muestra la ayuda

import sys, os
import prin_rc
from PyQt4 import QtCore, QtGui, Qt
from ui.ayuda import Ui_Ayuda

##Clase que define la ventana de ayuda que hereda de la clase QWidget del módulo QtGui
class Ayuda(QtGui.QWidget):
    ##Constructor de la ventana de ayuda
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.ui=Ui_Ayuda()
        self.ui.setupUi(self)
        
        
        #layoutH=QtGui.QHBoxLayout(self)
        #Region=self.visibleRegion ()
        #rect=self.rect()
        rect=self.contentsRect()
        self.editor = QtGui.QTextBrowser(self)
        self.editor.setReadOnly(1)
        self.editor.setAcceptRichText(1)
        self.editor.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.editor.setOpenLinks(1)
        self.editor.setGeometry(rect)
        policy=QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
        self.editor.setSizePolicy(policy)
        #layoutH.addWidget(self.editor)
        #self.setViewport(self.editor)


        url=QtCore.QUrl("qrc:/dictionary/Ayuda.html")
        self.editor.setSource(url)

    ##Función que traduce una cadena dada a codificación UTF8
    #
    #Recibe como parámetro la cadena a traducir
    def tr(self, string):
        return QtGui.QApplication.translate("MainWindow", string, None, QtGui.QApplication.UnicodeUTF8)
                

    ##Método para redefinir los eventos que se producen al redimensionarse la ventana de ayuda   
    def resizeEvent(self, event):
        rect=self.contentsRect()
        self.editor.setGeometry(rect)
        event.accept()
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    ay=Ayuda()
    ay.show()
    sys.exit(app.exec_())
