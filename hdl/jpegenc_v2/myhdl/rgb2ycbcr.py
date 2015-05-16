#!/bin/python
from myhdl import *

Y1, Y2, Y3 = 4899, 9617, 1868
CB1, CB2, CB3 = -2764, -5428, 8192
CR1, CR2, CR3 = 8192, -6860, -1332
Y_OFFSET, CB_OFFSET, CR_OFFSET = 0, 2097152, 2097152


class RGB(object):

    def __init__(self):
        self.red = Signal(intbv(0)[8:])
        self.green = Signal(intbv(0)[8:])
        self.blue = Signal(intbv(0)[8:])

    def next(self, r, g, b):
        self.red.next = r
        self.green.next = g
        self.blue.next = b


class YCbCr(object):

    def __init__(self):
        self.y = Signal(intbv(0)[8:])
        self.cb = Signal(intbv(0)[8:])
        self.cr = Signal(intbv(0)[8:])


def rgb2ycbcr(ycbcr, enable_out, rgb, enable_in, clk, reset):
    """ A RGB to YCbCr converter with reset.

    I/O pins:
    --------
    y           : output 8-bit unsigned value in range of 0-127
    cb          : output 8-bit unsigned value in range of 0-128
    cr          : output 8-bit unsigned value in range of 0-128
    enable_out  : output True when output is available
    r           : input 8-bit unsigned value in range of 0-255
    g           : input 8-bit unsigned value in range of 0-255
    b           : input 8-bit unsigned value in range of 0-255
    enable_in   : input True when input is available
    clk         : input clock boolean signal
    reset       : input reset boolean signal

    """

    ytemp, cbtemp, crtemp = [intbv(0)[22:] for _ in range(3)]

    @always_seq(clk.posedge, reset=reset)
    def logic():
        enable_out.next = False

        if enable_in == True:
            ytemp[:] = intbv(Y_OFFSET + Y1 * rgb.red +
                             Y2 * rgb.green + Y3 * rgb.blue)[22:]

            cbtemp[:] = intbv(CB_OFFSET + CB1 * rgb.red +
                              CB2 * rgb.green + CB3 * rgb.blue)[22:]

            crtemp[:] = intbv(CR_OFFSET + CR1 * rgb.red +
                              CR2 * rgb.green + CR3 * rgb.blue)[22:]

            ycbcr.y.next = ytemp[21:14] + 1 \
                if ytemp[21:14] != 255 and ytemp[13] \
                else ytemp[21:14]

            ycbcr.cb.next = cbtemp[21:14] + 1 \
                if cbtemp[21:14] != 255 and cbtemp[13] \
                else cbtemp[21:14]

            ycbcr.cr.next = crtemp[21:14] + 1 \
                if crtemp[21:14] != 255 and crtemp[13] \
                else crtemp[21:14]

            enable_out.next = True
    return logic
