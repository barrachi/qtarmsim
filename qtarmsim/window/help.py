# -*- coding: utf-8 -*-

###########################################################################
#                                                                         #
#  This file is part of the Qt ArmSim application.                        #
#                                                                         #
#  Qt ArmSim is free software; you can redistribute it and/or modify      #
#  it under the terms of the GNU General Public License as published by   #
#  the Free Software Foundation; either version 2 of the License, or      #
#  (at your option) any later version.                                    #
#                                                                         #
#  This program is distributed in the hope that it will be useful, but    #
#  WITHOUT ANY WARRANTY; without even the implied warranty of             #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU      #
#  General Public License for more details.                               #
#                                                                         #
###########################################################################

import os
import sys

from PySide import QtCore, QtGui


from .. modulepath import module_path
from .. ui.help import Ui_Help



class HelpWindow(QtGui.QWidget):
    "Help window"
    
    def __init__(self, parent=None):
        super(HelpWindow, self).__init__()
        self.ui = Ui_Help()
        self.ui.setupUi(self)
        rect = self.contentsRect()
        self.editor = QtGui.QTextBrowser(self)
        self.editor.setReadOnly(1)
        self.editor.setAcceptRichText(1)
        self.editor.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.editor.setOpenLinks(1)
        self.editor.setGeometry(rect)
        # @todo: check the following sentence
        policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored,
                                   QtGui.QSizePolicy.Ignored)
        self.editor.setSizePolicy(policy)
        url = QtCore.QUrl.fromLocalFile(os.path.join(module_path, "html", self.trUtf8("Help.html")))
        self.editor.setSource(url)

    def resizeEvent(self, event):
        """Method called when the help window is resized."""
        rect = self.contentsRect()
        self.editor.setGeometry(rect)
        event.accept()
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    helpWindow = HelpWindow()
    helpWindow.show()
    sys.exit(app.exec_())
