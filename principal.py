#!/usr/bin/env python3
# -*- coding: utf-8 -*-


##Módulo principal
#
#Construir la ventana principal



import sys, os
import resources.prin_rc as prin_rc
from PyQt4 import QtCore, QtGui
from ui.principal2 import Ui_MainWindow
from op import Opciones
from ej import Ejecutar
from mu import Multipasos
from br import Breakpoi
from va import Valor
from co import Conso
from im import Imprimir
from ay import Ayuda


##Clase que define la ventana principal que hereda de la clase QMainWindow del módulo QtGui
class Principal(QtGui.QMainWindow):
    ##Valor inicial de la ruta del archivo de interrupciones
    pathini=os.path.join("excepcion.s")
    ##Vector que almacena el valor por defecto de las opciones del simulador
    opci=[1, 0, 0, 0]

    ##Constructor de la página principal
    def __init__(self, parent = None):
    
        #Constructor
        QtGui.QMainWindow.__init__(self, parent)
        #Cargar la MainWindow creada con el designer
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        
        
        #Llamada para introducir el icono de la MainWindow
        self.setWindowIcon(QtGui.QIcon(":/images/spi.bmp"))
        #Llamada para poner título a la ventana principal
        self.setWindowTitle(self.tr("Simulador GlSpim"))
        #Llamada para cambiar el tamaño de MainWindow
        self.resize(500, 400)
 
        #Inicialización de diálogos
        #Diálogo de puntos de ruptura
        self.br=Breakpoi(self)
        ##Almacena los puntos de ruptura introducidos
        self.ptosrup=QtGui.QListWidget(self.br)
        #Ventana de consola
        self.consol=Conso()
        self.consol.move(self.x()+600, self.y())
        #Ventana de ayuda
        self.ay=Ayuda()
        self.ay.move(self.x()+600, self.y())
        
        #LLamda a función para crear las barras de herramientas
        self.createToolBars()
        #Llamada para crear los DockWidgets
        self.createPaneles()
        #Llamada para asociar acciones a botones
        self.createActions()
        #Llamda para crear la barra de estado
        self.createStatusBar()


        #Salva el estado inicial de la interfaz
        self.estados=self.saveState (1)
        
     
    ##Función que traduce una cadena dada a codificación UTF8
    #
    #Recibe como parámetro la cadena a traducir
    def tr(self, string):
        return QtGui.QApplication.translate("MainWindow", string, None, QtGui.QApplication.UnicodeUTF8)
        
    ##Acción asociada a actionAbrir
    #
    #Abre el diálogo de abrir fichero para abir un fichero en ensamblador y cargarlo en el simulador 
    def open(self):
        #Llamada a funcion que abre el dialogo OpenFile
        fileName = QtGui.QFileDialog.getOpenFileName(self, self.tr("Abrir Archivo"),
                                                     QtCore.QDir.currentPath(), self.tr("Archivos de ensamblador (*.s *.asm);;Todos los archivos (*)"), self.tr("Archivos de ensamblador (*.s *.asm)") )
        if not fileName.isEmpty():
            QtGui.QMessageBox.information(self, self.tr("Simulador GlSpim"),
                                              self.tr("Cargando %1.").arg(fileName))
 
    ##Acción asociada a actionSalir
    #
    #Realiza las acciones necesarias para abandonar el programa
    def closes(self):
        #Cierra la ventana de la consola
        self.consol.close()
        #Cierra la ventana principal
        self.close()
        
    ##Acción asociada a actionGuardar
    #
    #Abre el diálogo de guardar fichero y llama a la función saveFile
    def load(self):
        #Llamada a función que abre el diálogo SaveFile
        ruta=os.path.join("untitled.out")
        fileName = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save File"),ruta,self.tr("Archivos de salida (*.out)"))
        
        if fileName.isEmpty():
            return False
        #Llamada a la función saveFile
        self.saveFile(fileName)
        
    ##Método llamado por la función load
    #
    #Crea el fichero .out de nombre pasado como parámetro y guarda el estado actual de los distintos paneles en él
    def saveFile(self, fileName):
        #Llamada que crea un fichero con el nombre que pasamos como argumento
        file = QtCore.QFile(fileName)
        if not file.open( QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, self.tr("Error"),
                    self.tr("No se puede escribir %1:\n%2.").arg(fileName).arg(file.errorString()))
            return False
        
        #Escribimos la información de los distintos paneles en el fichero .out
        a=QtCore.QByteArray()
        a.insert(0, self.tr("Regitros:\n\n"))
        a.insert (a.size(), self.registers.toPlainText())
        a.insert(a.size(), self.tr("\nSegmento de Datos:\n\n"))
        a.insert(a.size(),self.data.toPlainText())
        a.insert(a.size(), self.tr("\nSegmento de Texto:\n\n"))
        a.insert(a.size(),self.texto.toPlainText())
        a.insert(a.size(), self.tr("\n\nMensajes:\n\n"))
        a.insert(a.size(),self.mens.toPlainText())
        a.insert(a.size(), self.tr("\n\nConsola:\n\n"))
        a.insert(a.size(), self.consol.consolEdit.text())
        file.write(a)

        self.statusBar().showMessage(self.tr("File saved"), 2000)
        return True        
        
    ##Acción asociada a actionOpciones2
    #
    #Abre el diálogo de opciones del Spim
    def opciones_2(self):
        opc=Opciones(self)
        opc.exec_()

    ##Acción asociada a actionImprimir
    #
    #Abre el diálogo que permite imprimir valores en el panel de mensajes
    def imp(self):
        im=Imprimir(self)
        im.exec_()

    
    ##Acción asociada a actionMensajes
    #
    #Función para ocultar o hacer visible el panel de mensajes
    def mensajes(self):
        if self.dock4.isVisible():
            self.dock4.setVisible(False)
            self.ui.actionMensajes.setChecked(0)
        else:
            self.dock4.setVisible(True)
            self.ui.actionMensajes.setChecked(1)

    
    ##Acción asociada a actionRegistros
    #
    #Función para ocultar o hacer visible el panel de registros
    def registros(self):
        if self.dock1.isVisible():
            self.dock1.setVisible(False)
            self.ui.actionRegistros.setChecked(0)
        else:
            self.dock1.setVisible(True)
            self.ui.actionRegistros.setChecked(1)


    ##Acción asociada a actionSegmento_de_texto
    #
    #Función para ocultar o hacer visible el panel de segmento de texto
    def segmento_de_texto(self):
        if self.dock3.isVisible():
            self.dock3.setVisible(False)
            self.ui.actionSegmento_de_texto.setChecked(0)
        else:
            self.dock3.setVisible(True)
            self.ui.actionSegmento_de_texto.setChecked(1)

        
    ##Acción asociada a actionSegmento_de_datos
    #
    #Función para ocultar o hacer visible el panel de segmento de datos
    def segmento_de_datos(self):
        if self.dock2.isVisible():
            self.dock2.setVisible(False)
            self.ui.actionSegmento_de_datos.setChecked(0)
        else:
            self.dock2.setVisible(True)
            self.ui.actionSegmento_de_datos.setChecked(1)
    
    ##Acción asociada a actionEjecutar
    #
    #Abre el diálogo de parámetros de ejecución del simulador
    def ejecutar(self):
        eje=Ejecutar(self)
        eje.exec_()
    
    ##Acción asociada a actionEjecuci_n_multipasos
    #
    #Abre el diálogo para seleccionar el número de pasos a ejecutar
    def ejecutar_multi(self):
        ej=Multipasos(self)
        ej.exec_()

        
    ##Acción asociada a actionEjecuci_n_pasos
    def ejecutar_single(self):
        self.mens.append(self.tr("Ejecutando instrucción"))
        
    ##Acción asociada a actionPunto_de_corte
    #
    #Abre el diálogo que permite añadir y suprimir puntos de ruptura
    def cortes(self):
        self.br.layout.addWidget(self.ptosrup)
        self.br.exec_()

    ##Acción asociada a actionFijar_valor
    #
    #Abre el diálogo que permite asignar un valor a un registro
    def fijar_valor(self):
        va=Valor(self)
        va.exec_()
    

    ##Acción asociada al botón de parar ejecución de la barra de herramientas
    #
    #Función para parar la ejecución en curso
    def parar(self):
        para = QtGui.QMessageBox.warning(self, self.tr("Detener ejecución"),
                            self.tr("Quieres detener la ejecución del programa?"),QtGui.QMessageBox.Yes | QtGui.QMessageBox.Default,QtGui.QMessageBox.No | QtGui.QMessageBox.Escape)
                            
    ##Acción asociada a actionBarra_de_herramientas
    #
    #Función para ocultar o hacer visible la barra de herramientas
    def barraH(self):
        if self.ui.fileToolBar.isVisible():
            self.ui.fileToolBar.setHidden(1)
        else:
            self.ui.fileToolBar.setVisible(1)
            
    ##Acción asociada a actionBarra_de_estado
    #
    #Función para ocultar o hacer visible la barra de estado 
    def barraE(self):
        if self.ui.statusbar.isVisible():
            self.ui.statusbar.setHidden(1)
            self.actionBarra_de_estado.setChecked(0)
        else:
            self.ui.statusbar.setVisible(1)
            self.actionBarra_de_estado.setChecked(1)
    
    ##Acción asociada a actionLimpiar_Consola
    #
    #Función para limpiar la consola
    def conso_clear(self):
        self.mens.append(self.tr("Limpiando consola"))
        self.consol.consolEdit.clear()
        
    ##Acción asociada a actionVista_inicial
    #
    #Función para restaurar la disposición por defecto de la ventana principal
    def recuperar(self):
        if self.ui.statusbar.isVisible() != True:
            self.ui.statusbar.setVisible(1)
            self.actionBarra_de_estado.setChecked(1)
        if self.dock1.isVisible()!=True:
            self.dock1.setVisible(1)
        if self.dock2.isVisible()!=True:
            self.dock2.setVisible(1)
        if self.dock3.isVisible()!=True:
            self.dock3.setVisible(1)
        if self.dock4.isVisible()!=True:
            self.dock4.setVisible(1)
        self.restoreState (self.estados,  1)
        self.restoreState(self.estados, 1)
        
        
    ##Acción asociada a actionLimpiar_registros
    #
    #Función para poner todos los registros a 0
    def limpiar_registros(self):
        self.mens.append(self.tr("Limpiando registros"))
     
    ##Acción asociada a actionRecargar
    #
    #Función para volver a ensamblar el archivo actual en el simulador
    def recargar(self):
        self.mens.append(self.tr("Recargando el archivo actual"))
        
        
    ##Acción asociada a actionReinicializar
    #
    #Función para restaurar el contenido de los registros y la memoria
    def reinicializar(self):
        self.mens.append(self.tr("Restaurando contenidos de registros y memoria"))
        
    ##Método para redefinir los eventos que se producen tras el cierre de la ventana principal
    #
    #Se cierran todas las ventanas abiertas de la aplicación
    def closeEvent(self, event):
        self.consol.close()
        self.ay.close()
        event.accept()
    ##Método para redefinir los eventos que se producen tras restaurar la ventana principal
    #
    #Se restauran todas las ventanas abiertas de la aplicación
    def showEvent(self, event):
        event.accept()
        if self.consol.isVisible()==True:
            self.consol.showNormal()
        if self.ay.isVisible()==True:
            self.ay.showNormal()
    ##Método para redefinir los eventos que se producen tras minimizar la ventana principal
    #
    #Se minimizan todas las ventanas abiertas de la aplicación
    def hideEvent(self, event):
        event.accept()
        if self.consol.isVisible()==True:
            self.consol.showMinimized()
        if self.ay.isVisible()==True:
            self.ay.showMinimized()


    ##Acción asociada a actionTemas_de_ayuda
    #
    #Activa el modo ¿Qué es esto?
    def whatsThis(self):
        QtGui.QWhatsThis.enterWhatsThisMode()
        self.helpB.setChecked (1)
        
    ##Acción asociada a actionSobre_spim
    #
    #Muestra una pequeña información sobre la aplicación
    def sobre(self):
        QtGui.QMessageBox.about(self, self.tr("Sobre XSpim"), self.tr("SPIMGLORIA Version 1.0 of March,6 2008\nby Gloria Edo (al060338@alumail.uji.es).\nNo Rights Reserved."))
    
    ##Acción asociada a actionAyuda
    #
    #Abre una nueva ventana para consultar los distintos temas de ayuda sobre la aplicación
    def ayudaTemas(self):
        self.ay=Ayuda()
        self.ay.setVisible(1)
    
    ##Método para asociar signals y slots de los ítems de los menús
    def createActions(self):
        
        self.actionAbrir = QtGui.QAction(self.tr("Abrir"), self)
        self.connect(self.ui.actionAbrir, QtCore.SIGNAL("triggered()"), self.open)

        self.actionSalir = QtGui.QAction(self.tr("Salir"), self)
        self.connect(self.ui.actionSalir, QtCore.SIGNAL("triggered()"), self.closes)

        self.actionGuardar = QtGui.QAction(self.tr("Guardar"), self)
        self.connect(self.ui.actionGuardar, QtCore.SIGNAL("triggered()"), self.load)
        
        self.actionImprimir=QtGui.QAction(self.tr("Imprimir"), self)
        self.connect(self.ui.actionImprimir, QtCore.SIGNAL("triggered()"), self.imp)

        self.actionOpciones2 = QtGui.QAction(self.tr("Opciones"), self)
        self.connect(self.ui.actionOpciones_2, QtCore.SIGNAL("triggered()"), self.opciones_2)
        
        self.actionEjecutar = QtGui.QAction(self.tr("Ejecutar"), self)
        self.connect(self.ui.actionEjecutar, QtCore.SIGNAL("triggered()"), self.ejecutar)
        
        self.actionEjecuci_n_multipasos = QtGui.QAction(self.tr("Ejecución multipasos"), self)
        self.connect(self.ui.actionEjecuci_n_multipasos, QtCore.SIGNAL("triggered()"), self.ejecutar_multi)
        
        self.actionEjecuci_n_pasos = QtGui.QAction(self.tr("Ejecución multipasos"), self)
        self.connect(self.ui.actionEjecuci_n_pasos, QtCore.SIGNAL("triggered()"), self.ejecutar_single)
        
        self.actionPunto_de_corte = QtGui.QAction(self.tr("Puntos de ruptura"), self)
        self.connect(self.ui.actionPunto_de_corte, QtCore.SIGNAL("triggered()"), self.cortes)
        
        self.actionFijar_valor = QtGui.QAction(self.tr("Fijar valor"), self)
        self.connect(self.ui.actionFijar_valor, QtCore.SIGNAL("triggered()"), self.fijar_valor)
        
        self.actionTemas_de_ayuda= QtGui.QAction(self.tr("Ayuda"), self)
        self.connect(self.ui.actionTemas_de_ayuda, QtCore.SIGNAL("triggered()"), self.whatsThis)
        
        self.actionLimpiar_Registros = QtGui.QAction(self.tr("Limpiar registros"), self)
        self.connect(self.ui.actionLimpiar_Registros, QtCore.SIGNAL("triggered()"), self.limpiar_registros)
        
        self.actionReinicializar = QtGui.QAction(self.tr("Reinicializar"), self)
        self.connect(self.ui.actionReinicializar, QtCore.SIGNAL("triggered()"), self.reinicializar)
        
        self.actionRecargar = QtGui.QAction(self.tr("Recargar"), self)
        self.connect(self.ui.actionRecargar, QtCore.SIGNAL("triggered()"), self.recargar)
        
        self.actionParar = QtGui.QAction(self.tr("Parar"), self)
        self.connect(self.ui.actionParar, QtCore.SIGNAL("triggered()"), self.parar)
        
        self.actionLimpiar_Consola=QtGui.QAction(self.tr("Limpiar Consola"), self)
        self.connect(self.ui.actionLimpiar_Consola, QtCore.SIGNAL("triggered()"), self.conso_clear)
        
        
        self.actionBarra_de_estado = QtGui.QAction(self.tr("B&arra de estado"), self)
        self.connect(self.actionBarra_de_estado, QtCore.SIGNAL("triggered()"), self.barraE)
        self.actionBarra_de_estado.setCheckable(1)
        self.actionBarra_de_estado.setChecked(1)
        self.actionBarra_de_estado.setWhatsThis(self.tr("Oculta o hace visible la barra de estado"))
        self.actionBarra_de_estado.setStatusTip(self.tr("Barra de estado"))
        
        self.actionVista_inicial=QtGui.QAction(self.tr("R&estaurar disposición por defecto"), self)
        self.connect(self.actionVista_inicial, QtCore.SIGNAL("triggered()"), self.recuperar)
        self.actionVista_inicial.setWhatsThis(self.tr("Recupera la disposición por defecto de la ventana principal del programa"))
        self.actionVista_inicial.setStatusTip(self.tr("Recuperar disposición por defecto"))
        
        
        self.actionSobre_spim = QtGui.QAction(self.tr("Sobre GlSpim"), self)
        self.connect(self.ui.actionSobre_spim, QtCore.SIGNAL("triggered()"), self.sobre)
        
        self.actionAyuda = QtGui.QAction(self.tr("&Temas de ayuda..."), self)
        self.connect(self.actionAyuda, QtCore.SIGNAL("triggered()"), self.ayudaTemas)
        self.actionAyuda.setWhatsThis(self.tr("Abre la ventana de ayuda sobre la aplicación"))
        self.ui.menuAyuda.addAction(self.actionAyuda)
        self.actionAyuda.setStatusTip(self.tr("Abrir temas de ayuda"))
        
        accionBarra_H=self.ui.fileToolBar.toggleViewAction()
        accionBarra_H.setStatusTip(self.tr("Barra de herramientas"))
        accionBarra_H.setWhatsThis(self.tr("Oculta o hace visible la barra de tareas"))
        self.ui.menuVer.addAction(accionBarra_H)
        
        self.ui.menuVer.addAction(self.actionBarra_de_estado)
 
        self.ui.menuVer.addSeparator()
        self.ui.menuVer.addAction(self.consol.actionConsola)
        
        

        self.accionRegistros.setStatusTip(self.tr("Panel de registros"))
        self.accionRegistros.setWhatsThis(self.tr("Oculta o hace visible el panel de registros"))
        self.accionRegistros.setText ("&Registros")
        self.ui.menuVer.addAction(self.accionRegistros)

        self.accionSegmento_de_texto.setStatusTip(self.tr("Panel de segmento de texto"))
        self.accionSegmento_de_texto.setWhatsThis(self.tr("Oculta o hace visible el panel de segmento de texto"))
        self.accionSegmento_de_texto.setText ("Segmento de &texto")
        self.ui.menuVer.addAction(self.accionSegmento_de_texto)
        
        
        self.accionSegmento_de_datos.setStatusTip(self.tr("Panel de segmento de datos"))
        self.accionSegmento_de_datos.setWhatsThis(self.tr("Oculta o hace visible el panel de segmento de datos"))
        self.accionSegmento_de_datos.setText ("Segmento de &datos")
        self.ui.menuVer.addAction(self.accionSegmento_de_datos)
        
        
        
        self.accionMensajes.setStatusTip(self.tr("Panel de mensajes"))
        self.accionMensajes.setWhatsThis(self.tr("Oculta o hace visible el panel de mensajes"))
        self.accionMensajes.setText ("&Mensajes")
        self.ui.menuVer.addAction(self.accionMensajes)
        
        self.ui.menuVer.addSeparator()
        self.ui.menuVer.addAction(self.actionVista_inicial)
        


    ##Método que añade acciones a la barra de tareas
    def createToolBars(self):
        abrirIcono=QtGui.QIcon(":/images/open.png")
        guardarIcono=QtGui.QIcon(":/images/screenCapture.png")
        ejecutarIcono=QtGui.QIcon(":/images/runProject.png")
        pararIcono=QtGui.QIcon(":/images/break.png")
        pararIconoDis=QtGui.QIcon(":/images/breakDisabled.png")
        breakpIcono=QtGui.QIcon(":/images/breakpointToggle.png")
        helpIcono=QtGui.QIcon(":/images/whatsThis.png")
        #abrir=QtGui.QAction(icono, self.tr(""), self.ui.actionAbrir)
        #abrir=self.ui.fileToolBar.addAction(icono, self.tr(""))
        self.abrirB=self.ui.fileToolBar.addAction(abrirIcono, self.tr(""), self.open)
        self.abrirB.setWhatsThis(self.tr("Permite especificar el nombre del fichero que debe ser cargado y ensamblado en memoria"))
        self.abrirB.setStatusTip(self.tr("Abrir un archivo existente"))
        self.abrirB.setToolTip(self.tr("Abrir"))
        self.guardarB=self.ui.fileToolBar.addAction(guardarIcono, self.tr(""), self.load)
        self.guardarB.setWhatsThis(self.tr("Permite guardar en un archivo .out el estado actual de los segmentos de texto y datos, de los registros, los mensajes y la consola"))
        self.guardarB.setStatusTip(self.tr("Capturar el estado actual en un archivo .out"))
        self.guardarB.setToolTip(self.tr("Capturar estado actual"))
        self.ejecutarB=self.ui.fileToolBar.addAction(ejecutarIcono, self.tr(""), self.ejecutar)
        self.ejecutarB.setWhatsThis(self.tr("Sirve para ejecutar el programa cargado en memoria. Antes de comenzar la ejecución un diálogo permite especificar la dirección de comienzo de la ejecución"))
        self.ejecutarB.setStatusTip(self.tr("Ejecutar el programa actual"))
        self.ejecutarB.setToolTip(self.tr("Ejecutar"))
        self.pararB=self.ui.fileToolBar.addAction(pararIcono, self.tr(""), self.parar)
        self.pararB.setWhatsThis(self.tr("Permite detener la ejecución en curso"))
        self.pararB.setStatusTip(self.tr("Detener la ejecución"))
        self.pararB.setToolTip(self.tr("Detener"))
        self.cortesB=self.ui.fileToolBar.addAction(breakpIcono, self.tr(""), self.cortes)
        self.cortesB.setWhatsThis(self.tr("Sirve para introducir o borrar puntos de ruptura en la ejecución del programa. Un cuadro de diálogo permite añadir las direcciones de memoria en las que se desea detener la ejecución"))
        self.cortesB.setStatusTip(self.tr("Añadir punto de ruptura"))
        self.cortesB.setToolTip(self.tr("Puntos de ruptura"))
        self.helpB=self.ui.fileToolBar.addAction(helpIcono, self.tr(""), self.whatsThis)
        self.helpB.setWhatsThis(self.tr("Activa la ayuda"))
        self.helpB.setStatusTip(self.tr("Activar la ayuda"))
        self.helpB.setToolTip(self.tr("¿Qué es esto?"))

    


    ##Método para crear la barra de estado
    def createStatusBar(self):
        self.statusBar().showMessage(self.tr("Listo"))
        

    ##Método para crear el panel de registros, segmentos de datos y texto y mensajes
    def createPaneles(self):  

        #Llamada que crea panel Registros
        
        self.dock1 = QtGui.QDockWidget(self.tr("Registros"), self)
        self.dock1.setObjectName ("Registros1")
        #Llamada que crea cuadro de edicion de texto
        self.registers = QtGui.QTextEdit(self.dock1)
        self.registers.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        fuente=QtGui.QFont()
        fuente.setFamily(self.tr("Courier"))
        fuente.setStyleHint(QtGui.QFont.TypeWriter)
        self.registers.setCurrentFont(fuente)
        #Añade el estado de los registros guardado en el fichero reg al panel
        f = QtCore.QFile(":/dictionary/reg.txt")
        f.open(QtCore.QFile.ReadOnly)
        self.registers.setText(QtCore.QTextStream(f).readAll())
        f.close()
        
        #Anyade el cuadro de edicion de texto al panel
        self.dock1.setWidget(self.registers)
        self.dock1.setWhatsThis(self.tr("Panel de visualización de registros, muestra los valores de los registros del procesador MIPS"))
        #Anyade el panel a la ventana principal
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.dock1)
        title=self.dock1.titleBarWidget()
        
        self.accionRegistros=self.dock1.toggleViewAction()
        
        self.dock2 = QtGui.QDockWidget(self.tr("Segmento de texto"), self)
        self.dock2.setObjectName ("Segmento de texto1")
        self.dock2.setMinimumHeight(0)
        self.texto = QtGui.QTextEdit(self.dock2)
        self.texto.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.texto.setCurrentFont(fuente)

        f = QtCore.QFile(":/dictionary/text.txt")
        f.open(QtCore.QFile.ReadOnly)
        self.texto.setText(QtCore.QTextStream(f).readAll())
        f.close()
        self.dock2.setWidget(self.texto)
        self.dock2.setWhatsThis(self.tr("Panel de visualización de código, muestra las instrucciones del programa de usuario y del núcleo del sistema que se carga automáticamente cuando se inicia XSPIM"))
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.dock2)
        self.accionSegmento_de_texto=self.dock2.toggleViewAction()
        
        #Llamada que divide al espacio que alberga el panel de registros y anyade el panel de segmento de datos a el
        self.splitDockWidget (self.dock1, self.dock2, QtCore.Qt.Vertical)
        
        self.dock3 = QtGui.QDockWidget(self.tr("Segmento de datos"), self)
        self.dock3.setObjectName ("Segmento de datos1")
        self.dock3.setMinimumHeight(0)
        self.data = QtGui.QTextEdit(self.dock3)
        self.data.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.data.setCurrentFont(fuente)

        f = QtCore.QFile(":/dictionary/data.txt")
        f.open(QtCore.QFile.ReadOnly)
        self.data.setText(QtCore.QTextStream(f).readAll())
        f.close()
        self.dock3.setWidget(self.data)
        self.dock3.setWhatsThis(self.tr("Panel de visualización de datos, muestra el contenido de la memoria"))
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.dock3)
        self.accionSegmento_de_datos=self.dock3.toggleViewAction()





        #Llamada que divide al espacio que alberga el panel de segmento de datos y añade el panel de segmento de texto a él
        self.splitDockWidget (self.dock2, self.dock3, QtCore.Qt.Vertical)
        
        self.dock4 = QtGui.QDockWidget(self.tr("Mensajes"), self)
        self.dock4.setObjectName ("Mensajes1")
        self.dock4.setMinimumHeight(0)
        self.mens = QtGui.QTextEdit(self.dock4)
        self.mens.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.mens.setCurrentFont(fuente)
        f = QtCore.QFile(":/dictionary/mens.txt")
        f.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
        self.mens.setText(QtCore.QTextStream(f).readAll())
        f.close()
        self.dock4.setWidget(self.mens)
        self.dock4.setWhatsThis(self.tr("Panel de visualización de mensajes, lo utiliza el simulador para informar de qué está haciendo y avisar de los errores que ocurran durante el ensamblado o ejecución de un programa"))
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.dock4)
        self.accionMensajes=self.dock4.toggleViewAction()

        #Llamada que divide al espacio que alberga el panel de segmento de texto y añade el panel de mensajes a él
        self.splitDockWidget (self.dock3, self.dock4, QtCore.Qt.Vertical)

        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    princi = Principal()
    princi.show()
    sys.exit(app.exec_())
