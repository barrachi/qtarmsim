# -*- coding: utf-8 -*-

###########################################################################
#  QtARMSim -- A Qt graphical interface to ARMSim                         #
#                                                                         #
#  Copyright 2014-15 Sergio Barrachina Mir <barrachi@uji.es>              #
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
#  You should have received a copy of the GNU General Public License      #
#  along with this program.  If not, see <http://www.gnu.org/licenses/>   #
#                                                                         #
###########################################################################

import getopt
import os
import signal
import sys

from PySide import QtGui


from . mainwindow import QtARMSimMainWindow 


def _help():
    print("""Usage: qtarmsim.py [options] [asmfile.s]

QtARMSim is a graphical frontend to the ARMSim ARM simulator. It provides
an easy to use multiplatform ARM emulation environment that has been designed
to be used on Computer Architecture Introductory courses.

If an asmfile.s is provided, it will be opened.

Options:
   -v, --verbose     increments the output verbosity
   -h, --help        displays this help and exit

Please, report bugs to <barrachi@uji.es>.
""")


def _getopts():
    "Processes the options passed to the executable"
    verbose = False
    file_name = ""
    optlist, args = getopt.getopt(sys.argv[1:],         # @UnusedVariable
                                  'vh',
                                  ['verbose', 'help', ])
    for opt, arg in optlist:  # @UnusedVariable arg
        if opt in ('-h', '--help'):
            _help()
            sys.exit()
        elif opt in ('-v', '--verbose'):
            verbose = True
    if len(args) and args[0][-2:] in ('.s', '.c'):
        file_name = args[0]
    return (file_name, verbose)


def main():
    # Make CTRL+C work
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    # Create the application
    app = QtGui.QApplication(sys.argv)
    # Process the command line options
    (file_name, verbose) = _getopts()
    # Create the main window and show it
    main_window = QtARMSimMainWindow(verbose = verbose)
    main_window.show()
    # If there is a file_name from the command line, open it
    if file_name:
        main_window.readFile(file_name)
    # Enter the main loop of the application
    sys.exit(app.exec_())
    
    
if __name__ == "__main__":
    main()
