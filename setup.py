#!/usr/bin/env python

from setuptools import setup

setup(
    name='JPEG Encoder',
    version='0.1dev',
    author='Merkourios Katsimpris',
    author_email='merkourioskatsimpris@gmail.com',
    url='https://github.com/mkatsimpris/test_jpeg',
    packages=['jpegenc'],
    description='JPEG Encoder',
    install_requires = ['myhdl >= 1.0.dev'],
    classifiers=[
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
        ],
)
