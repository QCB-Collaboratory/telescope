"""
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Telescope',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.5.0',

    description='Web application to keep track of job progress in remote servers',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/QCB-Collaboratory/telescope',

    # Author details
    author='',
    author_email='',

    license='GPL-3.0',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: GPL-3.0',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='unix, SGE, genomics',

    packages = [ 'telescope' ],

    package_data = {
        '' : ['telescope/pages/*.html',   # this makes GLOB avoid matching folders as files
                'telescope/pages/css/*', 'telescope/pages/js/*', 'telescope/pages/fonts/*']
    },

    install_requires=['paramiko','tornado','configparser'],
    extras_require={},

)
