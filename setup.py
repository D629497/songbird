#!/usr/bin/env python

# ----------------------------------------------------------------------------
# Copyright (c) 2016--, gneiss development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

import re
import ast
import os
from glob import glob
from setuptools import find_packages, setup
from setuptools.command.build_ext import build_ext as _build_ext


class build_ext(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)
        # Prevent numpy from thinking it is still in its setup process:
        __builtins__.__NUMPY_SETUP__ = False
        import numpy
        self.include_dirs.append(numpy.get_include())


classes = """
    Development Status :: 4 - Beta
    License :: OSI Approved :: BSD License
    Topic :: Software Development :: Libraries
    Topic :: Scientific/Engineering
    Topic :: Scientific/Engineering :: Bio-Informatics
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3 :: Only
    Operating System :: Unix
    Operating System :: POSIX
    Operating System :: MacOS :: MacOS X
"""
classifiers = [s.strip() for s in classes.split('\n') if s]

description = ('Regression methods')

version='0.1.0'

setup(name='songbird',
      version=version,
      license='BSD',
      description='',
      long_description='',
      author="gneiss development team",
      author_email="jamietmorton@gmail.com",
      maintainer="gneiss development team",
      maintainer_email="jamietmorton@gmail.com",
      packages=['songbird'],
      scripts=glob('scripts/songbird'),
      setup_requires=['numpy >= 1.9.2'],
      ext_modules=extensions,
      cmdclass={'build_ext': build_ext},
      install_requires=[
          'IPython >= 3.2.0',
          'numpy >= 1.9.2',
          'pandas >= 0.18.0',
          'scipy >= 0.15.1',
          'nose >= 1.3.7',
          'patsy',
          'scikit-bio>=0.5.1',
          'scikit-learn',
          'biom-format',
          'seaborn'
      ],
      classifiers=classifiers,
      package_data={
          },
      )
