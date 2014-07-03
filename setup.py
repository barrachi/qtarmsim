from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

# Get version from src/qtarmsim/version.py
version = {}
with open('qtarmsim/version.py') as fp:
    exec(fp.read(), version)
__version__ = version['__version__']

# Get the long description from the README file
with open(path.join(here, 'README'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'qtarmsim',
    version = __version__,
    description = 'Qt graphical frontend to ARMSim',
    long_description = long_description,

    # The project's main homepage.
    url = 'http://lorca.act.uji.es/projects/qtarmsim/',

    # Author details
    author = 'Sergio Barrachina Mir',
    author_email = 'barrachi@uji.es',

    # License
    license='GPLv3+',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Who the project is intended for
        'Intended Audience :: Education',
        'Topic :: Software Development :: Assemblers',
        'Topic :: Software Development :: Debuggers',
        'Topic :: Software Development :: Disassemblers',

        # License long description
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        # Python versions supported
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    # What does the project relate to?
    keywords='ARM simulator Qt assembler disassembler debugger',

    # Packages of the project
    packages = find_packages(exclude=['docs', 'tmp']),

    # List run-time dependencies here.  These will be installed by pip when your
    # project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/technical.html#install-requires-vs-requirements-files
    #install_requires=['peppercorn'],

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
        'qtarmsim': ['armsim/*'],
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages.
    # see http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    #data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'gui_scripts': [
            'qtarmsim=qtarmsim:main',
        ],
    },
)
