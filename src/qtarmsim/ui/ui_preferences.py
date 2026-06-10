# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'preferences.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDialog, QDialogButtonBox, QFormLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QRadioButton, QSizePolicy, QSpacerItem, QSpinBox,
    QTabWidget, QToolButton, QVBoxLayout, QWidget)

class Ui_PreferencesDialog(object):
    def setupUi(self, PreferencesDialog):
        if not PreferencesDialog.objectName():
            PreferencesDialog.setObjectName(u"PreferencesDialog")
        PreferencesDialog.setWindowModality(Qt.WindowModal)
        PreferencesDialog.resize(660, 498)
        self.verticalLayout = QVBoxLayout(PreferencesDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(PreferencesDialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabARMSim = QWidget()
        self.tabARMSim.setObjectName(u"tabARMSim")
        self.verticalLayout_4 = QVBoxLayout(self.tabARMSim)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.groupBox = QGroupBox(self.tabARMSim)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setTitle(u"ARMSim")
        self.groupBox.setFlat(False)
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        self.labelARMSimBackend = QLabel(self.groupBox)
        self.labelARMSimBackend.setObjectName(u"labelARMSimBackend")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelARMSimBackend)

        self.comboBoxARMSimBackend = QComboBox(self.groupBox)
        self.comboBoxARMSimBackend.setObjectName(u"comboBoxARMSimBackend")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.comboBoxARMSimBackend)

        self.labelARMSimCommand = QLabel(self.groupBox)
        self.labelARMSimCommand.setObjectName(u"labelARMSimCommand")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.labelARMSimCommand)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lineEditARMSimDirectory = QLineEdit(self.groupBox)
        self.lineEditARMSimDirectory.setObjectName(u"lineEditARMSimDirectory")
        self.lineEditARMSimDirectory.setText(u"")

        self.horizontalLayout.addWidget(self.lineEditARMSimDirectory)

        self.toolButtonARMSimDirectory = QToolButton(self.groupBox)
        self.toolButtonARMSimDirectory.setObjectName(u"toolButtonARMSimDirectory")

        self.horizontalLayout.addWidget(self.toolButtonARMSimDirectory)


        self.formLayout.setLayout(4, QFormLayout.ItemRole.FieldRole, self.horizontalLayout)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label)

        self.lineEditARMSimCommand = QLineEdit(self.groupBox)
        self.lineEditARMSimCommand.setObjectName(u"lineEditARMSimCommand")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.lineEditARMSimCommand)

        self.labelARMSimServer = QLabel(self.groupBox)
        self.labelARMSimServer.setObjectName(u"labelARMSimServer")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelARMSimServer)

        self.lineEditARMSimServer = QLineEdit(self.groupBox)
        self.lineEditARMSimServer.setObjectName(u"lineEditARMSimServer")
        self.lineEditARMSimServer.setText(u"")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lineEditARMSimServer)

        self.labelARMSimPort = QLabel(self.groupBox)
        self.labelARMSimPort.setObjectName(u"labelARMSimPort")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelARMSimPort)

        self.spinBoxARMSimPort = QSpinBox(self.groupBox)
        self.spinBoxARMSimPort.setObjectName(u"spinBoxARMSimPort")
        self.spinBoxARMSimPort.setMinimum(8000)
        self.spinBoxARMSimPort.setMaximum(9999)
        self.spinBoxARMSimPort.setValue(8010)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinBoxARMSimPort)

        self.useLabelsLabel = QLabel(self.groupBox)
        self.useLabelsLabel.setObjectName(u"useLabelsLabel")

        self.formLayout.setWidget(5, QFormLayout.ItemRole.LabelRole, self.useLabelsLabel)

        self.useLabelsCheckBox = QCheckBox(self.groupBox)
        self.useLabelsCheckBox.setObjectName(u"useLabelsCheckBox")

        self.formLayout.setWidget(5, QFormLayout.ItemRole.FieldRole, self.useLabelsCheckBox)


        self.verticalLayout_2.addLayout(self.formLayout)


        self.verticalLayout_4.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(self.tabARMSim)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setTitle(u"Gcc ARM")
        self.groupBox_2.setFlat(False)
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.lineEditARMGccOptions = QLineEdit(self.groupBox_2)
        self.lineEditARMGccOptions.setObjectName(u"lineEditARMGccOptions")
        self.lineEditARMGccOptions.setText(u"")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lineEditARMGccOptions)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.lineEditARMGccCommand = QLineEdit(self.groupBox_2)
        self.lineEditARMGccCommand.setObjectName(u"lineEditARMGccCommand")
        self.lineEditARMGccCommand.setText(u"")

        self.horizontalLayout_2.addWidget(self.lineEditARMGccCommand)

        self.toolButtonARMGccCommand = QToolButton(self.groupBox_2)
        self.toolButtonARMGccCommand.setObjectName(u"toolButtonARMGccCommand")

        self.horizontalLayout_2.addWidget(self.toolButtonARMGccCommand)


        self.formLayout_2.setLayout(0, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_2)

        self.labelARMGccOptions = QLabel(self.groupBox_2)
        self.labelARMGccOptions.setObjectName(u"labelARMGccOptions")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelARMGccOptions)

        self.labelARMGccCommand = QLabel(self.groupBox_2)
        self.labelARMGccCommand.setObjectName(u"labelARMGccCommand")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelARMGccCommand)


        self.verticalLayout_3.addLayout(self.formLayout_2)


        self.verticalLayout_4.addWidget(self.groupBox_2)

        self.verticalSpacer = QSpacerItem(20, 43, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.pushButtonARMSimRestoreDefaults = QPushButton(self.tabARMSim)
        self.pushButtonARMSimRestoreDefaults.setObjectName(u"pushButtonARMSimRestoreDefaults")

        self.horizontalLayout_3.addWidget(self.pushButtonARMSimRestoreDefaults)


        self.verticalLayout_4.addLayout(self.horizontalLayout_3)

        self.tabWidget.addTab(self.tabARMSim, "")
        self.tabAppearance = QWidget()
        self.tabAppearance.setObjectName(u"tabAppearance")
        self.verticalLayout_5 = QVBoxLayout(self.tabAppearance)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.groupBoxColorTheme = QGroupBox(self.tabAppearance)
        self.groupBoxColorTheme.setObjectName(u"groupBoxColorTheme")
        self.verticalLayout_6 = QVBoxLayout(self.groupBoxColorTheme)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.radioButtonSystemTheme = QRadioButton(self.groupBoxColorTheme)
        self.radioButtonSystemTheme.setObjectName(u"radioButtonSystemTheme")
        self.radioButtonSystemTheme.setChecked(True)

        self.verticalLayout_6.addWidget(self.radioButtonSystemTheme)

        self.radioButtonLightTheme = QRadioButton(self.groupBoxColorTheme)
        self.radioButtonLightTheme.setObjectName(u"radioButtonLightTheme")

        self.verticalLayout_6.addWidget(self.radioButtonLightTheme)

        self.radioButtonDarkTheme = QRadioButton(self.groupBoxColorTheme)
        self.radioButtonDarkTheme.setObjectName(u"radioButtonDarkTheme")

        self.verticalLayout_6.addWidget(self.radioButtonDarkTheme)


        self.verticalLayout_5.addWidget(self.groupBoxColorTheme)

        self.groupBoxFontSize = QGroupBox(self.tabAppearance)
        self.groupBoxFontSize.setObjectName(u"groupBoxFontSize")
        self.horizontalLayout_font = QHBoxLayout(self.groupBoxFontSize)
        self.horizontalLayout_font.setObjectName(u"horizontalLayout_font")
        self.labelFontSize = QLabel(self.groupBoxFontSize)
        self.labelFontSize.setObjectName(u"labelFontSize")

        self.horizontalLayout_font.addWidget(self.labelFontSize)

        self.comboBoxFontSize = QComboBox(self.groupBoxFontSize)
        self.comboBoxFontSize.setObjectName(u"comboBoxFontSize")

        self.horizontalLayout_font.addWidget(self.comboBoxFontSize)

        self.horizontalSpacer_font = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_font.addItem(self.horizontalSpacer_font)


        self.verticalLayout_5.addWidget(self.groupBoxFontSize)

        self.verticalSpacer_2 = QSpacerItem(20, 43, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer_2)

        self.tabWidget.addTab(self.tabAppearance, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.buttonBox = QDialogButtonBox(PreferencesDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)

        QWidget.setTabOrder(self.comboBoxARMSimBackend, self.lineEditARMSimServer)
        QWidget.setTabOrder(self.lineEditARMSimServer, self.spinBoxARMSimPort)
        QWidget.setTabOrder(self.spinBoxARMSimPort, self.lineEditARMSimCommand)
        QWidget.setTabOrder(self.lineEditARMSimCommand, self.lineEditARMSimDirectory)
        QWidget.setTabOrder(self.lineEditARMSimDirectory, self.toolButtonARMSimDirectory)
        QWidget.setTabOrder(self.toolButtonARMSimDirectory, self.useLabelsCheckBox)
        QWidget.setTabOrder(self.useLabelsCheckBox, self.lineEditARMGccCommand)
        QWidget.setTabOrder(self.lineEditARMGccCommand, self.toolButtonARMGccCommand)
        QWidget.setTabOrder(self.toolButtonARMGccCommand, self.lineEditARMGccOptions)
        QWidget.setTabOrder(self.lineEditARMGccOptions, self.pushButtonARMSimRestoreDefaults)
        QWidget.setTabOrder(self.pushButtonARMSimRestoreDefaults, self.tabWidget)
        QWidget.setTabOrder(self.tabWidget, self.radioButtonSystemTheme)
        QWidget.setTabOrder(self.radioButtonSystemTheme, self.radioButtonLightTheme)
        QWidget.setTabOrder(self.radioButtonLightTheme, self.radioButtonDarkTheme)
        QWidget.setTabOrder(self.radioButtonDarkTheme, self.comboBoxFontSize)

        self.retranslateUi(PreferencesDialog)
        self.buttonBox.accepted.connect(PreferencesDialog.accept)
        self.buttonBox.rejected.connect(PreferencesDialog.reject)

        QMetaObject.connectSlotsByName(PreferencesDialog)
    # setupUi

    def retranslateUi(self, PreferencesDialog):
        PreferencesDialog.setWindowTitle(QCoreApplication.translate("PreferencesDialog", u"QtARMSim Preferences", None))
        self.labelARMSimBackend.setText(QCoreApplication.translate("PreferencesDialog", u"Backend", None))
        self.labelARMSimCommand.setText(QCoreApplication.translate("PreferencesDialog", u"ARMSim directory", None))
        self.toolButtonARMSimDirectory.setText(QCoreApplication.translate("PreferencesDialog", u"...", None))
        self.label.setText(QCoreApplication.translate("PreferencesDialog", u"Command line", None))
        self.labelARMSimServer.setText(QCoreApplication.translate("PreferencesDialog", u"Server", None))
        self.labelARMSimPort.setText(QCoreApplication.translate("PreferencesDialog", u"Port", None))
        self.useLabelsLabel.setText(QCoreApplication.translate("PreferencesDialog", u"Use labels", None))
#if QT_CONFIG(tooltip)
        self.useLabelsCheckBox.setToolTip(QCoreApplication.translate("PreferencesDialog", u"Use labels on the disassembled code instead of the corresponding numeric value", None))
#endif // QT_CONFIG(tooltip)
        self.toolButtonARMGccCommand.setText(QCoreApplication.translate("PreferencesDialog", u"...", None))
        self.labelARMGccOptions.setText(QCoreApplication.translate("PreferencesDialog", u"Options", None))
        self.labelARMGccCommand.setText(QCoreApplication.translate("PreferencesDialog", u"Command line", None))
        self.pushButtonARMSimRestoreDefaults.setText(QCoreApplication.translate("PreferencesDialog", u"Restore Defaults", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabARMSim), QCoreApplication.translate("PreferencesDialog", u"ARMSim", None))
        self.groupBoxColorTheme.setTitle(QCoreApplication.translate("PreferencesDialog", u"Color theme", None))
        self.radioButtonSystemTheme.setText(QCoreApplication.translate("PreferencesDialog", u"System default", None))
        self.radioButtonLightTheme.setText(QCoreApplication.translate("PreferencesDialog", u"Light", None))
        self.radioButtonDarkTheme.setText(QCoreApplication.translate("PreferencesDialog", u"Dark", None))
        self.groupBoxFontSize.setTitle(QCoreApplication.translate("PreferencesDialog", u"Font size", None))
        self.labelFontSize.setText(QCoreApplication.translate("PreferencesDialog", u"Point size:", None))
#if QT_CONFIG(tooltip)
        self.comboBoxFontSize.setToolTip(QCoreApplication.translate("PreferencesDialog", u"Font size for all application fonts. Auto uses the system default + 1 pt.", None))
#endif // QT_CONFIG(tooltip)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabAppearance), QCoreApplication.translate("PreferencesDialog", u"Appearance", None))
    # retranslateUi

