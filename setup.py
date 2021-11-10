#!/usr/bin/env python3

from setuptools import setup, find_packages
import os
import sys


    
setup(
    name='ALMA Corrimag',
    version='1.1',
    url='https://github.com/almaavu/Corrimag/',
    author='almaavu',
    author_email='almaavu@gmail.com',
    description='Correlate element maps',
    packages=find_packages(where=''),  # Required
    install_requires=['numpy', 'pandas', 'matplotlib', 'imageio', 'scipy', 'scikit-image'],
    include_package_data=True,
)
