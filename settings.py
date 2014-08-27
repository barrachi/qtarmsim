from codecs import open  # To use a consistent encoding

class Settings():

    def __init__(self):
        self.name = 'qtarmsim'
        self.version = self._get_version()
        self.description = 'Qt graphical frontend to ARMSim'
        self.url = 'http://lorca.act.uji.es/projects/qtarmsim/'
        self.author = 'Sergio Barrachina Mir'
        self.email = 'barrachi@uji.es'
        self.license = 'GPLV3+'
        self.package_data = {
                             'qtarmsim': ['armsim/*', 'test/add.s', 'html/*.html', 'html/img/*'],
                             }
        # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
        self.classifiers = [
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 5 - Production/Stable',
    
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
            ]
        self.keywords = ['ARM', 'simulator', 'assembler', 'disassembler', 'debugger']


    def _get_version(self):
        """Gets version from 'qtarmsim/version.py'."""
        version_dict = {}
        with open('qtarmsim/version.py') as fp:
            exec(fp.read(), version_dict)
        return version_dict['__version__']
