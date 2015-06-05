# Use the following command to create a source distribution and upload it to the
# testpypi repository:
#
# python3 ./setup.py sdist upload -r testpypi
#
# Documentation for python packaging:
# https://the-hitchhikers-guide-to-packaging.readthedocs.org/en/latest/
#
# Documentation for distutils
# https://docs.python.org/3.3/distutils/
#
# Known limitations:
#
# * 'install_requires = s.requires,' could be used to automatically
#    install PySide when installing qtarmsim. The problem is that this
#    option will make the installation of PySide harder on binary
#    based GNU/Linux distributions, because PySide will be downloaded
#    as source code and pip3 will try to compile it (which requires
#    the correct compilers, etc.  being already installed on the
#    system). This happens even if PySide has been previously
#    installed by the own package manager of that distribution.
#
#    Some python packages appear as installed when you execute 'pip3
#    list', even if they have been installed by the package manager
#    and not by pip3 itself. So, it seems, IMHO, that the problem is
#    due to PySide (or the PySide package) not saying that it is
#    already installed.
#

from distutils.core import setup, Command
import fnmatch
import os
from subprocess import call
import sys

from setuptools import find_packages

from settings import Settings


# Common settings used by distutils and cx_freeze
s = Settings()

# Find files and dirs from the given path
def findFilesAndDirs(path, filePatterns=[], dirPatterns=[]):
    files = []
    dirs = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        for filePattern in filePatterns:
            files += [os.path.join(dirpath, fn) for fn in fnmatch.filter(filenames, filePattern)]
        for dirPattern in dirPatterns:
            dirs += [os.path.join(dirpath, dn) for dn in fnmatch.filter(dirnames, dirPattern)]
    return (files, dirs)

def findFiles(path, filePatterns):
    return findFilesAndDirs(path, filePatterns, [])[0]

# Clean class (see /usr/lib64/python3.3/distutils/command/command_template)
class QtClean(Command):

    # Brief (40-50 characters) description of the command
    description = "Removes temporary files"

    # List of option tuples
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        files = []
        dirs = []
        (files, dirs) = findFilesAndDirs('.', ('*.pyc', ), ('__pycache__', ))
        filesToBeRemoved = files
        dirsToBeRemoved = dirs
        files = findFiles('./examples', ('*.o', '*.err', '*.lst'))
        filesToBeRemoved += files
        print("Removing temporary files...")
        for fileName in filesToBeRemoved:
            os.remove(fileName)
        print("Removing temporary directories...")
        for dirName in dirsToBeRemoved:
            os.rmdir(dirName)

# Clean class (see /usr/lib64/python3.3/distutils/command/command_template)
class QtCompile(Command):

    # Brief (40-50 characters) description of the command
    description = "Runs the PySide development tools on the current project"

    # List of option tuples
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # Run pysyde-uic
        CMD = 'pyside-uic'
        inputFileNames = findFiles('.', ('*.ui',))
        for fileName in inputFileNames:
            outputFileName = os.path.splitext(fileName)[0] + '.py'
            cmdArray = [CMD, '-o', outputFileName, fileName]
            print("Executing {}...".format(' '.join(cmdArray)))
            error = call(cmdArray) #, cwd = os.getcwd())
            if error:
                sys.exit(-1)
        # Run pyside-rcc
        CMD = 'pyside-rcc'
        inputFileNames = findFiles('.', ('*.qrc',))
        for fileName in inputFileNames:
            outputFileName = os.path.splitext(fileName)[0] + '_rc.py'
            cmdArray = [CMD, '-py3', '-o', outputFileName, fileName]
            print("Executing {}...".format(' '.join(cmdArray)))
            error = call(cmdArray)
            if error:
                sys.exit(-1)
        # Run lrelease
        CMD = 'lrelease'
        cmdArray = [CMD, './qtarmsim/qtarmsim.pro']
        print("Executing {}...".format(' '.join(cmdArray)))
        error = call(cmdArray)
        if error:
            sys.exit(-1)
        # Run pyside-lupdate
        CMD = 'pyside-lupdate'
        cmdArray = [CMD, './qtarmsim/qtarmsim.pro']
        print("Executing {}...".format(' '.join(cmdArray)))
        error = call(cmdArray)
        if error:
            sys.exit(-1)
        # Run linguist
        print("Now you can run 'linguist ./qtarmsim/lang/qtarmsim_es.ts'")

# Setup
setup(
        # Application details
        name = s.name,
        version = s.version,
        description = s.description,
        url = s.url,
        # Author details
        author = s.author,
        author_email = s.email,
        # License
        license = s.license,
        # Application classifiers
        classifiers = s.classifiers,
        # Application keywords
        keywords = s.keywords,

        # --------------------------------
        #  distutils parameters
        # --------------------------------
        packages = find_packages(exclude=['build', 'dist', 'distfiles', 'docs', 'examples', 'scripts', 'tmp']),
        package_data = s.package_data,
        entry_points={
            'gui_scripts': [
                'qtarmsim=qtarmsim:main',
            ],
        },
        cmdclass={'qtclean': QtClean, 'qtcompile': QtCompile}
      )
