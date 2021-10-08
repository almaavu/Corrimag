#!/usr/bin/env python3

from setuptools import setup, find_packages
import os
import sys


    
setup(
    name='element_maps_correlation',
    version='1.0.0',
    url='https://github.com/almaavu/element_maps_correlation/',
    author='almaavu',
    author_email='almaavu@gmail.com',
    description='Correlate element maps',
    packages=find_packages(where=''),  # Required
    install_requires=['numpy', 'pandas', 'matplotlib', 'imageio', 'scipy', 'scikit-image'],
    include_package_data=True,
)
