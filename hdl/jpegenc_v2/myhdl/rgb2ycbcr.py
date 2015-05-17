#!/bin/python
from myhdl import *
from commons import *

Y1, Y2, Y3 = 4899, 9617, 1868
CB1, CB2, CB3 = -2764, -5428, 8192
CR1, CR2, CR3 = 8192, -6860, -1332
Y_OFFSET, CB_OFFSET, CR_OFFSET = 0, 2097152, 2097152

PRECISION_FACTOR = 14


class RGB(object):

    def __init__(self, nbits=8):
        self.red = Signal(intbv(0)[nbits:])
        self.green = Signal(intbv(0)[nbits:])
        self.blue = Signal(intbv(0)[nbits:])

    def next(self, r, g, b):
        self.red.next = r
        self.green.next = g
        self.blue.next = b

    def bitLength(self): return self.nbits


class YCbCr(object):

    def __init__(self, nbits=8):
        self.nbits = nbits
        self.y = Signal(intbv(0)[nbits:])
        self.cb = Signal(intbv(0)[nbits:])
        self.cr = Signal(intbv(0)[nbits:])

    def bitLength(self): return self.nbits


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

    temp_nbits = PRECISION_FACTOR + ycbcr.bitLength()
    ytemp, cbtemp, crtemp = [intbv(0)[temp_nbits:] for _ in range(3)]

    @always_seq(clk.posedge, reset=reset)
    def logic():
        enable_out.next = INACTIVE_LOW

        if enable_in == ACTIVE_HIGH:
            ytemp[:] = intbv(Y_OFFSET + Y1 * rgb.red +
                             Y2 * rgb.green + Y3 * rgb.blue)[temp_nbits-1:]

            cbtemp[:] = intbv(CB_OFFSET + CB1 * rgb.red +
                              CB2 * rgb.green + CB3 * rgb.blue)[temp_nbits-1:]

            crtemp[:] = intbv(CR_OFFSET + CR1 * rgb.red +
                              CR2 * rgb.green + CR3 * rgb.blue)[temp_nbits-1:]

            ycbcr.y.next = round_unsigned(
                ytemp, temp_nbits, PRECISION_FACTOR)

            ycbcr.cb.next = round_unsigned(
                cbtemp, temp_nbits, PRECISION_FACTOR)

            ycbcr.cr.next = round_unsigned(
                crtemp, temp_nbits, PRECISION_FACTOR)

            enable_out.next = ACTIVE_HIGH
    return logic
