#!/bin/python
from myhdl import *

Y1, Y2, Y3 = 4899, 9617, 1868
CB1, CB2, CB3 = -2764, -5428, 8192
CR1, CR2, CR3 = 8192, -6860, -1332
Y_OFFSET, CB_OFFSET, CR_OFFSET = 0, 2097152, 2097152


class RGB(object):

    def __init__(self):
        self.red, self.green, self.blue = [
            Signal(intbv(0)[8:]) for _ in range(3)]

    def next(self, r, g, b):
        self.red.next = r
        self.green.next = g
        self.blue.next = b


class YCbCr(object):

    def __init__(self):
        self.y, self.cb, self.cr = [Signal(intbv(0)[8:]) for _ in range(3)]

    def next(self, y, cb, cr):
        self.y.next = y
        self.cb.next = cb
        self.cr.next = cr


def rgb2ycbcr(ycbcr, rgb, clk, reset):
    """ A RGB to YCbCr converter with reset.

    I/O pins:
    --------
    y       : output 8-bit unsigned value in range of 0-255
    cb      : output 8-bit unsigned value in range of 0-255
    cr      : output 8-bit unsigned value in range of 0-255
    r 		: input 8-bit unsigned value in range of 0-255
    g 		: input 8-bit unsigned value in range of 0-255
    b 		: input 8-bit unsigned value in range of 0-255
    clk 	: input clock boolean signal
    reset	: input reset boolean signal

    """

    ytemp, cbtemp, crtemp = [intbv(0)[22:] for _ in range(3)]

    @always_seq(clk.posedge, reset=reset)
    def logic():
        ytemp[:] = intbv(
            Y_OFFSET + Y1 * rgb.red + Y2 * rgb.green + Y3 * rgb.blue)[22:]
        cbtemp[:] = intbv(
            CB_OFFSET + CB1 * rgb.red + CB2 * rgb.green + CB3 * rgb.blue)[22:]
        crtemp[:] = intbv(
            CR_OFFSET + CR1 * rgb.red + CR2 * rgb.green + CR3 * rgb.blue)[22:]

        if ytemp[13]:
            ycbcr.y = ytemp[21:14] + 1
        else:
            ycbcr.y = ytemp[21:14]

        if cbtemp[21:14] != 255 and cbtemp[13]:
            ycbcr.cb = cbtemp[21:14] + 1
        else:
            ycbcr.cb = cbtemp[21:14]

        if crtemp[21:14] != 255 and crtemp[13]:
            ycbcr.cr = crtemp[21:14] + 1
        else:
            ycbcr.cr = crtemp[21:14]

    return logic
