import sys
import os
import glob
from setuptools import setup, find_packages

assert sys.version_info >= (3, 0)


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()


examples_path = 'share/calligra/python{}.{}/examples'.format(
    sys.version_info.major, sys.version_info.minor
)

setup(
    name = 'calligra',
    version = '0.2',
    author = 'Elie ROUDNINSKI',
    author_email = 'xademax@gmail.com',
    description = (
        'C language metaprogramming and code generation from Python'
    ),
    license = 'MIT',
    url = 'https://github.com/marmeladema/calligra',
    download_url = 'https://github.com/marmeladema/calligra/archive/0.2.tar.gz',
    packages = find_packages(),
    data_files = [(examples_path, glob.iglob('examples/*.py'))],
    package_data = {'calligra': ['importer/cparser.h']},
    long_description = read('README.rst'),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Code Generators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    install_requires = [],
    python_requires = '>=3',
    test_suite = 'tests',
)
