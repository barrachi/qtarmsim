# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'principal2.ui'
#
# Created: Sat Apr 26 12:04:20 2008
#      by: PyQt4 UI code generator 4-snapshot-20070727
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(QtCore.QSize(QtCore.QRect(0,0,630,547).size()).expandedTo(MainWindow.minimumSizeHint()))

        #self.centralwidget = QtGui.QWidget(MainWindow)
        #self.centralwidget.setObjectName("centralwidget")
        #MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0,0,630,21))
        self.menubar.setObjectName("menubar")

        self.menuArchivo = QtGui.QMenu(self.menubar)
        self.menuArchivo.setObjectName("menuArchivo")

        self.menuEdicion = QtGui.QMenu(self.menubar)
        self.menuEdicion.setObjectName("menuEdicion")

        self.menuVer = QtGui.QMenu(self.menubar)
        self.menuVer.setObjectName("menuVer")

        self.menuAyuda = QtGui.QMenu(self.menubar)
        self.menuAyuda.setObjectName("menuAyuda")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.fileToolBar = QtGui.QToolBar(MainWindow)
        self.fileToolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.fileToolBar.setObjectName("fileToolBar")
        MainWindow.addToolBar(self.fileToolBar)

        self.actionAbrir = QtGui.QAction(MainWindow)
        self.actionAbrir.setCheckable(False)
        self.actionAbrir.setObjectName("actionAbrir")

        self.actionGuardar = QtGui.QAction(MainWindow)
        self.actionGuardar.setObjectName("actionGuardar")

        self.actionLimpiar_Registros = QtGui.QAction(MainWindow)
        self.actionLimpiar_Registros.setObjectName("actionLimpiar_Registros")

        self.actionReinicializar = QtGui.QAction(MainWindow)
        self.actionReinicializar.setObjectName("actionReinicializar")

        self.actionRecargar = QtGui.QAction(MainWindow)
        self.actionRecargar.setObjectName("actionRecargar")

        self.actionEjecutar = QtGui.QAction(MainWindow)
        self.actionEjecutar.setObjectName("actionEjecutar")

        self.actionParar = QtGui.QAction(MainWindow)
        self.actionParar.setObjectName("actionParar")

        self.actionEjecuci_n_pasos = QtGui.QAction(MainWindow)
        self.actionEjecuci_n_pasos.setObjectName("actionEjecuci_n_pasos")

        self.actionEjecuci_n_multipasos = QtGui.QAction(MainWindow)
        self.actionEjecuci_n_multipasos.setObjectName("actionEjecuci_n_multipasos")

        self.actionPunto_de_corte = QtGui.QAction(MainWindow)
        self.actionPunto_de_corte.setObjectName("actionPunto_de_corte")

        self.actionOpciones = QtGui.QAction(MainWindow)
        self.actionOpciones.setObjectName("actionOpciones")

        self.actionFuente = QtGui.QAction(MainWindow)
        self.actionFuente.setObjectName("actionFuente")

        self.actionMensajes = QtGui.QAction(MainWindow)
        self.actionMensajes.setCheckable(False)
        self.actionMensajes.setObjectName("actionMensajes")

        self.actionSegmento_de_texto = QtGui.QAction(MainWindow)
        self.actionSegmento_de_texto.setCheckable(False)
        self.actionSegmento_de_texto.setObjectName("actionSegmento_de_texto")

        self.actionSegmento_de_datos = QtGui.QAction(MainWindow)
        self.actionSegmento_de_datos.setCheckable(False)
        self.actionSegmento_de_datos.setObjectName("actionSegmento_de_datos")

        self.actionRegistros = QtGui.QAction(MainWindow)
        self.actionRegistros.setCheckable(False)
        self.actionRegistros.setObjectName("actionRegistros")

        self.actionConsola = QtGui.QAction(MainWindow)
        self.actionConsola.setCheckable(False)
        self.actionConsola.setObjectName("actionConsola")

        self.actionLimpiar_Consola = QtGui.QAction(MainWindow)
        self.actionLimpiar_Consola.setObjectName("actionLimpiar_Consola")

        self.actionBarra_de_herramientas = QtGui.QAction(MainWindow)
        self.actionBarra_de_herramientas.setCheckable(True)
        self.actionBarra_de_herramientas.setChecked(True)
        self.actionBarra_de_herramientas.setObjectName("actionBarra_de_herramientas")

        self.actionBarra_de_estado = QtGui.QAction(MainWindow)
        self.actionBarra_de_estado.setCheckable(True)
        self.actionBarra_de_estado.setChecked(True)
        self.actionBarra_de_estado.setObjectName("actionBarra_de_estado")

        self.actionTemas_de_ayuda = QtGui.QAction(MainWindow)
        self.actionTemas_de_ayuda.setObjectName("actionTemas_de_ayuda")

        self.actionSobre_spim = QtGui.QAction(MainWindow)
        self.actionSobre_spim.setObjectName("actionSobre_spim")

        self.actionSalir = QtGui.QAction(MainWindow)
        self.actionSalir.setObjectName("actionSalir")

        self.actionFijar_valor = QtGui.QAction(MainWindow)
        self.actionFijar_valor.setObjectName("actionFijar_valor")

        self.actionModo = QtGui.QAction(MainWindow)
        self.actionModo.setObjectName("actionModo")

        self.actionImprimir = QtGui.QAction(MainWindow)
        self.actionImprimir.setObjectName("actionImprimir")

        self.actionOpciones_2 = QtGui.QAction(MainWindow)
        self.actionOpciones_2.setObjectName("actionOpciones_2")

        self.actionVista_incial = QtGui.QAction(MainWindow)
        self.actionVista_incial.setObjectName("actionVista_incial")
        self.menuArchivo.addAction(self.actionAbrir)
        self.menuArchivo.addAction(self.actionGuardar)
        self.menuArchivo.addSeparator()
        self.menuArchivo.addAction(self.actionSalir)
        self.menuEdicion.addAction(self.actionLimpiar_Registros)
        self.menuEdicion.addAction(self.actionReinicializar)
        self.menuEdicion.addAction(self.actionRecargar)
        self.menuEdicion.addSeparator()
        self.menuEdicion.addAction(self.actionEjecutar)
        self.menuEdicion.addAction(self.actionParar)
        self.menuEdicion.addSeparator()
        self.menuEdicion.addAction(self.actionEjecuci_n_pasos)
        self.menuEdicion.addAction(self.actionEjecuci_n_multipasos)
        self.menuEdicion.addSeparator()
        self.menuEdicion.addAction(self.actionPunto_de_corte)
        self.menuEdicion.addSeparator()
        self.menuEdicion.addAction(self.actionFijar_valor)
        self.menuEdicion.addAction(self.actionImprimir)
        self.menuEdicion.addSeparator()
        self.menuEdicion.addAction(self.actionOpciones_2)
        self.menuVer.addAction(self.actionLimpiar_Consola)
        self.menuVer.addSeparator()
        self.menuAyuda.addAction(self.actionTemas_de_ayuda)
        self.menuAyuda.addSeparator()
        self.menuAyuda.addAction(self.actionSobre_spim)
        self.menubar.addAction(self.menuArchivo.menuAction())
        self.menubar.addAction(self.menuEdicion.menuAction())
        self.menubar.addAction(self.menuVer.menuAction())
        self.menubar.addAction(self.menuAyuda.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.menuArchivo.setTitle(QtGui.QApplication.translate("MainWindow", "&Archivo", None, QtGui.QApplication.UnicodeUTF8))
        self.menuEdicion.setTitle(QtGui.QApplication.translate("MainWindow", "&Simulación", None, QtGui.QApplication.UnicodeUTF8))
        self.menuVer.setTitle(QtGui.QApplication.translate("MainWindow", "&Ver", None, QtGui.QApplication.UnicodeUTF8))
        self.menuAyuda.setTitle(QtGui.QApplication.translate("MainWindow", "A&yuda", None, QtGui.QApplication.UnicodeUTF8))
        self.fileToolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "&Barra de herramientas", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbrir.setText(QtGui.QApplication.translate("MainWindow", "&Abrir...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbrir.setStatusTip(QtGui.QApplication.translate("MainWindow", "Abrir un archivo existente", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbrir.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Permite especificar el nombre del fichero que debe ser cargado y ensamblado en memoria", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbrir.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+O", None, QtGui.QApplication.UnicodeUTF8))
        self.actionGuardar.setText(QtGui.QApplication.translate("MainWindow", "&Capturar estado actual...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionGuardar.setStatusTip(QtGui.QApplication.translate("MainWindow", "Capturar el estado actual en un archivo .out", None, QtGui.QApplication.UnicodeUTF8))
        self.actionGuardar.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Permite guardar en un archivo .out el estado actual de los segmentos de texto y datos, de los registros, los mensajes y la consola", None, QtGui.QApplication.UnicodeUTF8))
        self.actionGuardar.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+S", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLimpiar_Registros.setText(QtGui.QApplication.translate("MainWindow", "&Limpiar registros", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLimpiar_Registros.setStatusTip(QtGui.QApplication.translate("MainWindow", "Limpiar  registros", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLimpiar_Registros.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Restaura al valor inicial el contenido de los registros", None, QtGui.QApplication.UnicodeUTF8))
        self.actionReinicializar.setText(QtGui.QApplication.translate("MainWindow", "&Reinicializar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionReinicializar.setStatusTip(QtGui.QApplication.translate("MainWindow", "Limpiar registros y memoria", None, QtGui.QApplication.UnicodeUTF8))
        self.actionReinicializar.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Restaura a su valor incial el contenido de los registros y la memoria", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRecargar.setText(QtGui.QApplication.translate("MainWindow", "Re&cargar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRecargar.setStatusTip(QtGui.QApplication.translate("MainWindow", "Recargar el archivo actual", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRecargar.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Permite ensamblar de nuevo el archivo actualmente ensamblado", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEjecutar.setText(QtGui.QApplication.translate("MainWindow", "&Ejecutar...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEjecutar.setStatusTip(QtGui.QApplication.translate("MainWindow", "Ejecutar el programa actual", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEjecutar.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Sirve para ejecutar el programa cargado en memoria. Antes de comenzar la ejecución un diálogo permite especificar la dirección de comienzo de la ejecución", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEjecutar.setShortcut(QtGui.QApplication.translate("MainWindow", "F5", None, QtGui.QApplication.UnicodeUTF8))
        self.actionParar.setText(QtGui.QApplication.translate("MainWindow", "&Detener ejecución", None, QtGui.QApplication.UnicodeUTF8))
        self.actionParar.setStatusTip(QtGui.QApplication.translate("MainWindow", "Detener la ejecución", None, QtGui.QApplication.UnicodeUTF8))
        self.actionParar.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Permite detener la ejecución en curso", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEjecuci_n_pasos.setText(QtGui.QApplication.translate("MainWindow", "Ejecución &paso a paso", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEjecuci_n_pasos.setStatusTip(QtGui.QApplication.translate("MainWindow", "Ejecutar paso a paso", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEjecuci_n_pasos.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Permite ejecutar el programa instrucción por instrucción", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEjecuci_n_pasos.setShortcut(QtGui.QApplication.translate("MainWindow", "F10", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEjecuci_n_multipasos.setText(QtGui.QApplication.translate("MainWindow", "Ejecución &multipaso...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEjecuci_n_multipasos.setStatusTip(QtGui.QApplication.translate("MainWindow", "Ejecutar múltiples pasos", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEjecuci_n_multipasos.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Mediante un cuadro de diálogo se especifica el número de instrucciones que se deben ejecutar en cada paso", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEjecuci_n_multipasos.setShortcut(QtGui.QApplication.translate("MainWindow", "F11", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPunto_de_corte.setText(QtGui.QApplication.translate("MainWindow", "P&untos de ruptura...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPunto_de_corte.setStatusTip(QtGui.QApplication.translate("MainWindow", "Añadir punto de ruptura", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPunto_de_corte.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Sirve para introducir o borrar puntos de ruptura en la ejecución del programa. Un cuadro de diálogo permite añadir las direcciones de memoria en las que se desea detener la ejecución", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPunto_de_corte.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+B", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpciones.setText(QtGui.QApplication.translate("MainWindow", "Opciones", None, QtGui.QApplication.UnicodeUTF8))
        self.actionFuente.setText(QtGui.QApplication.translate("MainWindow", "Fuente", None, QtGui.QApplication.UnicodeUTF8))
        self.actionMensajes.setText(QtGui.QApplication.translate("MainWindow", "Mensajes", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSegmento_de_texto.setText(QtGui.QApplication.translate("MainWindow", "Segmento de texto", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSegmento_de_datos.setText(QtGui.QApplication.translate("MainWindow", "Segmento de datos", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRegistros.setText(QtGui.QApplication.translate("MainWindow", "Registros", None, QtGui.QApplication.UnicodeUTF8))
        self.actionConsola.setText(QtGui.QApplication.translate("MainWindow", "Consola", None, QtGui.QApplication.UnicodeUTF8))
        self.actionConsola.setStatusTip(QtGui.QApplication.translate("MainWindow", "Consola", None, QtGui.QApplication.UnicodeUTF8))
        self.actionConsola.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Oculta o hace visible la consola", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLimpiar_Consola.setText(QtGui.QApplication.translate("MainWindow", "&Limpiar consola", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLimpiar_Consola.setStatusTip(QtGui.QApplication.translate("MainWindow", "Limpiar Consola", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLimpiar_Consola.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Limpia el contenido de la consola", None, QtGui.QApplication.UnicodeUTF8))
        self.actionBarra_de_herramientas.setText(QtGui.QApplication.translate("MainWindow", "Barra de herramientas", None, QtGui.QApplication.UnicodeUTF8))
        self.actionBarra_de_herramientas.setStatusTip(QtGui.QApplication.translate("MainWindow", "Barra de herramientas", None, QtGui.QApplication.UnicodeUTF8))
        self.actionBarra_de_herramientas.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Oculta o hace visible la barra de herramientas", None, QtGui.QApplication.UnicodeUTF8))
        self.actionBarra_de_estado.setText(QtGui.QApplication.translate("MainWindow", "Barra de estado", None, QtGui.QApplication.UnicodeUTF8))
        self.actionBarra_de_estado.setStatusTip(QtGui.QApplication.translate("MainWindow", "Barra de estado", None, QtGui.QApplication.UnicodeUTF8))
        self.actionBarra_de_estado.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Oculta o hace visible la barra de estado", None, QtGui.QApplication.UnicodeUTF8))
        self.actionTemas_de_ayuda.setText(QtGui.QApplication.translate("MainWindow", "¿&Qué es esto?", None, QtGui.QApplication.UnicodeUTF8))
        self.actionTemas_de_ayuda.setStatusTip(QtGui.QApplication.translate("MainWindow", "Activar la ayuda", None, QtGui.QApplication.UnicodeUTF8))
        self.actionTemas_de_ayuda.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Activa la ayuda", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSobre_spim.setText(QtGui.QApplication.translate("MainWindow", "&Sobre  GlSpim", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSobre_spim.setStatusTip(QtGui.QApplication.translate("MainWindow", "Abrir información sobre GlSpim", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSobre_spim.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Muestra un mensaje con información sobre GlSpim", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSalir.setText(QtGui.QApplication.translate("MainWindow", "&Salir", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSalir.setStatusTip(QtGui.QApplication.translate("MainWindow", "Salir de la aplicación", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSalir.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Se utiliza para terminar la sesión del simulador", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSalir.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+Q", None, QtGui.QApplication.UnicodeUTF8))
        self.actionFijar_valor.setText(QtGui.QApplication.translate("MainWindow", "&Fijar valor...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionFijar_valor.setStatusTip(QtGui.QApplication.translate("MainWindow", "Fijar valor", None, QtGui.QApplication.UnicodeUTF8))
        self.actionFijar_valor.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Permite cambiar el contenido de un registro o una posición de memoria", None, QtGui.QApplication.UnicodeUTF8))
        self.actionModo.setText(QtGui.QApplication.translate("MainWindow", "Modo", None, QtGui.QApplication.UnicodeUTF8))
        self.actionImprimir.setText(QtGui.QApplication.translate("MainWindow", "&Imprimir valor...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionImprimir.setStatusTip(QtGui.QApplication.translate("MainWindow", "Imprimir valor", None, QtGui.QApplication.UnicodeUTF8))
        self.actionImprimir.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Permite mostrar en el panel de mensajes el contenido de un rango de memoria o el valor asociado a las etiquetas globales", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpciones_2.setText(QtGui.QApplication.translate("MainWindow", "&Opciones...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpciones_2.setStatusTip(QtGui.QApplication.translate("MainWindow", "Opciones", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpciones_2.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Permite modificar el modo de funcionamiento de XSPIM y la ruta de la rutina de servicio de interrupción", None, QtGui.QApplication.UnicodeUTF8))
        self.actionVista_incial.setText(QtGui.QApplication.translate("MainWindow", "Vista incial", None, QtGui.QApplication.UnicodeUTF8))
        self.actionVista_incial.setStatusTip(QtGui.QApplication.translate("MainWindow", "Vista inicial", None, QtGui.QApplication.UnicodeUTF8))
        self.actionVista_incial.setWhatsThis(QtGui.QApplication.translate("MainWindow", "Recupera la disposición por defecto de la barra de tareas y de estado además de la disposición de los paneles del simulador", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
