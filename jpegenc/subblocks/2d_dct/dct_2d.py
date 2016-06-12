#!/usr/bin/env python
# coding=utf-8

import numpy as np

from math import cos, pi, sqrt


def random_matrix_8_8():

    random_matrix = np.random.rand(8, 8)
    random_matrix = np.rint(255*random_matrix)
    random_matrix = random_matrix.astype(int)

    return random_matrix


def two_d_dct_numpy(block):

    const = sqrt(2.0/8)
    a = const * cos(pi/4)
    b = const * cos(pi/16)
    c = const * cos(pi/8)
    d = const * cos(3*pi/16)
    e = const * cos(5*pi/16)
    f = const * cos(3*pi/8)
    g = const * cos(7*pi/16)

    coeff_matrix = [[a, a, a, a, a, a, a, a],
                    [b, d, e, g, -g, -e, -d, -b],
                    [c, f, -f, -c, -c, -f, f, c],
                    [d, -g, -b, -e, e, b, g, -d],
                    [a, -a, -a, a, a, -a, -a, a],
                    [e, -b, g, d, -d, -g, b, -e],
                    [f, -c, c, -f, -f, c, -c, f],
                    [g, -e, d, -b, b, -d, e, -g]]
    coeff_matrix = np.asarray(coeff_matrix)
    block = np.asarray(block)

    print block

    # first 1d-dct with rows
    dct_result = np.dot(coeff_matrix, np.transpose(block))
    # second 1d-dct with columns
    print np.rint(dct_result)
    dct_result = np.dot(coeff_matrix, np.transpose(dct_result))
    dct_result = np.rint(dct_result).astype(int)
    dct_result[0][0] -= 1024
    print dct_result

# block = random_matrix_8_8()

block = [[0xa6, 0xa1, 0x9b, 0x9a, 0x9b, 0x9c, 0x97, 0x92],
         [0x9f, 0xa3, 0x9d, 0x8e, 0x89, 0x8f, 0x95, 0x94],
         [0xa5, 0x97, 0x96, 0xa1, 0x9e, 0x90, 0x90, 0x9e],
         [0xa7, 0x9b, 0x91, 0x91, 0x92, 0x91, 0x91, 0x94],
         [0xca, 0xda, 0xc8, 0x98, 0x85, 0x98, 0xa2, 0x96],
         [0xf0, 0xf7, 0xfb, 0xe8, 0xbd, 0x96, 0x90, 0x9d],
         [0xe9, 0xe0, 0xf1, 0xff, 0xef, 0xad, 0x8a, 0x90],
         [0xe7, 0xf2, 0xf1, 0xeb, 0xf7, 0xfb, 0xd0, 0x97]]

two_d_dct_numpy(block)
