#!/bin/python
from myhdl import *
from commons import *

PRECISION_FACTOR = 18

A, B, C, D, E, F, G = 92682, 128553, 121095, 108982, 72820, 50159, 25571
MULT_MAT = [
    [A,  B,  C,  D,  A,  E,  F,  G],
    [A,  D,  F, -G, -A, -B, -C, -E],
    [A,  E, -F, -B, -A,  G,  C,  D],
    [A,  G, -C, -E,  A,  D, -F, -B],
    [A, -G, -C,  E,  A, -D, -F,  B],
    [A, -E, -F,  B, -A, -G,  C, -D],
    [A, -D,  F,  G, -A,  B, -C,  E],
    [A, -B,  C, -D,  A, -E,  F, -G]
]

A_OFFSET = 128 * 8 * A


class PixelLine(object):

    def __init__(self, nbits=12):
        self.nbits = nbits
        self.pixels = [Signal(sintbv(0, nbits)) for _ in range(8)]

    def pixel(self, index): return self.pixels[index]

    def bitLength(self): return self.nbits


class PixelBlock(object):

    def __init__(self, nbits=12):
        self.nbits = nbits
        self.pixelLines = [PixelLine(nbits) for _ in range(8)]

    def bitLength(self): return self.nbits

    def pixelLine(self, index): return self.pixelLines[index]
