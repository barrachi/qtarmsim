# A simple setup script to create an executable using PyQt4. This also
# demonstrates the method for creating a Windows executable that does not have
# an associated console.
#
# PyQt4app.py is a very simple type of PyQt4 application
#
# Run the build process by running the command 'python setup.py build'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the application

# Source: https://bitbucket.org/reclosedev/cx_freeze/src/f3cacc2fd45a/samples/PyQt4/setup.py

import sys

from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
        name = "qtarmsim",
        version = "0.1",
        description = "Sample cx_Freeze PyQt4 script",
        options = {"build_exe" : {"includes" : "atexit" }},
        executables = [Executable(
        "qtarmsim.py",
        base = base,
        shortcutName = "Qt ArmSim",
        shortcutDir = "DesktopFolder",
        )])
