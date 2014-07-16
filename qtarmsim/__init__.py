# -*- coding: utf-8 -*-

###########################################################################
#  Qt ARMSim -- a Qt graphical interface to ARMSim                        #
#                                                                         #
#  Copyright 2014 Sergio Barrachina Mir <barrachi@uji.es>                 #
#                                                                         #
#  This application is based on a previous work of Gloria Edo Piñana who  #
#  developed the graphical part of a Qt graphical interface to the SPIM   #
#  simulator on 2008.                                                     #
#                                                                         #
#  This program is free software: you can redistribute it and/or modify   #
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

import os
import signal
import sys

from PyQt4 import QtGui


from . mainwindow import QtARMSimMainWindow 


def main():
    # Make CTRL+C work
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    # Create the application
    app = QtGui.QApplication(sys.argv)
    # Create the main window and show it
    main_window = QtARMSimMainWindow()
    main_window.show()
    # If there is an assembly file on the command line, open it
    if sys.argv[1:] and sys.argv[1][-2:]==".s":
        main_window.readFile(sys.argv[1])
    # Enter the main loop of the application
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()
