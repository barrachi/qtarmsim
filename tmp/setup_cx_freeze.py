# Use the following command to create a frozen binary distribution and upload it
# to the testpypi repository:
#
# python3 ./setup_cx_freeze.py bdist upload -r testpypi
#

from glob import glob
import os
import sys

from cx_Freeze import setup, Executable

from settings import Settings


# Common settings to setuptools and cx_freeze
s = Settings()

# Base command
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# Include files vector
include_files = [("distfiles/libqscintilla2.so.9", ""),]
for pattern in s.package_data['qtarmsim']:
    for fname in glob("qtarmsim/{}".format(pattern)):
        include_files.append((fname, fname.replace("qtarmsim/", "")))

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
        #  cx_freeze parameters
        # --------------------------------
        options = {"build_exe" :
                   { 
                       "includes" : ("atexit", ),
                       "include_files": include_files,
                    }},
        executables = [ \
                        Executable(
                            "./qtarmsim.py",
                            base = base,
                            shortcutName = "Qt ARMSim",
                            shortcutDir = "DesktopFolder",
                            )
                        ]
        )
