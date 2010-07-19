#!/usr/bin/env python

from abrek import __version__ as version
import sys

try:
    from DistUtilsExtra.auto import setup
except ImportError:
    print >> sys.stderr, 'To build abrek you need', \
                         'https://launchpad.net/python-distutils-extra'
    sys.exit(1)

setup(
name='abrek',
version=version,
author='Paul Larson',
author_email='paul.larson@linaro.org',
url='https://launchpad.net/abrek',
)
