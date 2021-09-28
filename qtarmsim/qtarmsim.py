# -*- coding: utf-8 -*-

###########################################################################
#  QtARMSim -- A graphical ARM simulator                                  #
#                                                                         #
#  Copyright 2014-20 Sergio Barrachina Mir <barrachi@uji.es>              #
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

import PySide2
from PySide2 import QtCore, QtSvg, QtXml, QtWidgets

from qtarmsim.mainwindow import QtARMSimMainWindow
from qtarmsim.modulepath import module_path


def __stub():
    """
    This function does nothing. It exists only to avoid QtSvg and QtXml imports to be removed.
    QtSvg and QtXml must be imported in order to use SVG icons.
    """
    return QtSvg.Object(), QtXml.Object()


def _help():
    print("""Usage: qtarmsim.py [options] [file.s]

QtARMSim is a graphical ARM simulator. It provides an easy to use
multiplatform ARM emulation environment that has been designed to be
used on Computer Architecture Introductory courses.

If a file.s is provided, it will be opened.

Options:
   -d, --debug     provides a terminal to interact with ARMSim
   -v, --verbose   increments the output verbosity
   -h, --help      displays this help and exit

Please, report bugs to <barrachi@uji.es>.
""")


def _get_opts():
    """Processes the options passed to the executable"""
    debug = False
    verbose = False
    file_name = ""
    optlist, args = getopt.getopt(sys.argv[1:],  # @UnusedVariable
                                  'dvh',
                                  ['debug', 'verbose', 'help', ])
    for opt, arg in optlist:  # @UnusedVariable arg
        if opt in ('-h', '--help'):
            _help()
            sys.exit()
        elif opt in ('-d', '--debug'):
            debug = True
        elif opt in ('-v', '--verbose'):
            verbose = True
    if len(args) and args[0][-2:] in ('.s', '.c'):
        file_name = args[0]
    return file_name, debug, verbose


def main():
    # Make CTRL+C work
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    if sys.platform == 'darwin':
        # Big Sur requires the next environment variable to be set
        # (otherwise the PySide2 windows won't be shown)
        # https://www.loekvandenouweland.com/content/pyside2-big-sur-does-not-show-window.html
        os.environ['QT_MAC_WANTS_LAYER'] = '1'
    # Create the application
    qApp = QtWidgets.QApplication(sys.argv)
    # ------------------------------------------------------------
    #  In order to use SVG images on @##!![] Windows, you need to import QtSvg
    #  and QtXml and also ensure that the plugins directory is
    #  properly imported.
    #  https://stackoverflow.com/questions/9933358/pyside-svg-image-formats-not-found
    # ------------------------------------------------------------
    for plugins_dir in [os.path.join(p, "plugins") for p in PySide2.__path__]:
        qApp.addLibraryPath(plugins_dir)
    # Process the command line options
    (file_name, debug, verbose) = _get_opts()
    # Create the main window and show it
    main_window = QtARMSimMainWindow(debug=debug, verbose=verbose)
    main_window.show()
    # If there is a file_name on the command line, open it
    if file_name:
        main_window.readFile(file_name)
    # Set style
    # print(QtWidgets.QStyleFactory.keys())
    # qApp.setStyle("Fusion")
    url = QtCore.QUrl.fromLocalFile(os.path.join(module_path, "stylesheets", "lightblue.css"))
    f = open(url.toLocalFile())
    qApp.setStyleSheet("".join(f.readlines()))
    f.close()
    # Enter the main loop of the application
    sys.exit(qApp.exec_())


if __name__ == "__main__":
    main()
