# Use the following command to create a source distribution and upload it to the
# testpypi repository:
#
# python3 ./setup.py sdist upload -r testpypi
#

from setuptools import setup, find_packages  # Always prefer setuptools over distutils

from settings import Settings

# Common settings to setuptools and cx_freeze
s = Settings()

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
        #  setuptools parameters
        # --------------------------------
        packages = find_packages(exclude=['build', 'dist', 'distfiles', 'docs', 'examples', 'scripts', 'tmp']),
        package_data = s.package_data,
        entry_points={
            'gui_scripts': [
                'qtarmsim=qtarmsim:main',
            ],
        },
      )
