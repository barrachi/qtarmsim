# -*- coding: utf-8 -*-

##Módulo co
#
#Construir la consola de entrada salida


from PySide import QtCore, QtGui
from ..ui.consola import Ui_Consola
from ..res import console_rc
import sys

##Clase que define la consola que hereda de la clase QWidget del módulo QtGui
class Conso(QtGui.QMainWindow):
    ##Constructor de la consola
    def __init__(self,parent=None):
        QtGui.QMainWindow.__init__(self,parent)
        self.ui=Ui_Consola()
        self.ui.setupUi(self)
        
        rect=self.contentsRect()
        
        self.consolEdit = QtGui.QTextEdit()
        self.consolEdit.setGeometry(rect)
        self.consolEdit.setReadOnly(1)

        self.scrollArea = QtGui.QScrollArea(self)
        self.scrollArea.setWidget(self.consolEdit)
        self.scrollArea.setGeometry(rect)

        self.setWindowTitle(self.trUtf8("Consola"))
        self.setWindowIcon(QtGui.QIcon(":/images/consol.bmp"))
        
        
        self.actionConsola=QtGui.QAction(self.trUtf8("&Consola"), self)
        self.connect(self.actionConsola, QtCore.SIGNAL("triggered()"), self.con)
        
        self.actionConsola.setWhatsThis(self.trUtf8("Oculta o hace visible la consola"))
        self.actionConsola.setStatusTip(self.trUtf8("Consola"))
        self.actionConsola.setCheckable(1)
    
    ##Método asociado a actionConsola del menú Ventana de la ventana principal padre de la consola
    #
    #Oculta o hace visible la ventana Consola
    def con(self):
        if self.isHidden():
            self.setVisible(1)
            self.actionConsola.setChecked(1)
        else:
            self.setVisible(0)
        
    ##Función que traduce una cadena dada a codificación UTF8
    #
    #Recibe como parámetro la cadena a traducir
    def tr(self, string):
        return QtGui.QApplication.translate("MainWindow", string, None, QtGui.QApplication.UnicodeUTF8)
    
    ##Método para cambiar los eventos producidos tras el cierre de la consola
    def closeEvent(self, event):
        #padre=self.topLevelWidget()
        self.actionConsola.setChecked(0)
        event.accept()
        
    ##Método para redefinir los eventos que se producen al redimensionarse la consola 
    def resizeEvent(self, event):
        rect=self.contentsRect()
        self.consolEdit.setGeometry(rect)
        self.scrollArea.setGeometry(rect)
        event.accept()    
    
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    co=Conso()
    co.show()
    sys.exit(app.exec_())
