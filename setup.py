#!/usr/bin/env python

import imp
import sys

from setuptools import setup, find_packages

if sys.version_info < (2, 7):
    sys.exit("Sorry, Python < 2.7 is not supported")

VERSION = imp.load_source("", "nsg_bluepyopt_job/version.py").__version__

setup(
    name="nsg-bluepyopt-job",
    author="jean-denis courcol",
    version=VERSION,
    description="utilities to manage bluepyopt jobs on the nsg-portal",
    license="apache 2.0",
    install_requires=[
    ],
    packages=find_packages(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
)
