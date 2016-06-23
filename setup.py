#!/usr/bin/env python

from setuptools import setup
from setuptools import find_packages

setup(

    name='jpegenc',
    version='0.1.dev0',
    description='JPEG Encoder',
    author='Merkourios Katsimpris, Christopher Felton, Vikram Raigur',
    author_email='merkourioskatsimpris@gmail.com',
    url='https://github.com/cfelton/test_jpeg',
    packages=find_packages(),
    install_requires = ['myhdl >= 1.0.dev', 'Pillow >= 3.0.0'],
    classifiers=[
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
        ],
)
