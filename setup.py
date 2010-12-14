#!/usr/bin/env python

from distutils.core import setup
from libg3 import __version__ as version
import sys

setup(name='pylibgal3' ,
    version=version ,
    author='Jay Deiman' ,
    author_email='admin@splitstreams.com' ,
    url='http://stuffivelearned.org' ,
    description='A library for accessing/manipulating a Gallery 3 install' ,
    packages=['libg3'] ,
    package_dir={'libg3': 'libg3'} ,
)
