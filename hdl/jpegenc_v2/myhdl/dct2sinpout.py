#!/bin/python
from myhdl import *
from commons import *
from dctconstructs import *
from dct1sinpout import dct1SinPout
from dct1pinpout import dct1PinPout


def dct2SinPout(pixelBlock, enable_out, pixelValue, enable_in, clk, reset):
    """ A DCT2 Serial-in Parallel-out calculator with reset.

    I/O pins:
    --------
    pixelBlock  : output array of array of 12-bit signed value
    enable_out  : output ACTIVE_HIGH when output is available
    pixelValue  : input 8-bit unsigned value in range of 0-255
    enable_in   : input ACTIVE_HIGH when input is available
    clk         : input clock boolean signal
    reset       : input reset boolean signal

    """

    enable_out_in = Signal(INACTIVE_LOW)
    outin = PixelLine()

    dct1sinpout_inst = dct1SinPout(
        outin, enable_out_in, pixelValue, enable_in, clk, reset)
    dct1pinpout_inst = dct1PinPout(
        pixelBlock, enable_out, outin, enable_out_in, clk, reset)

    return dct1sinpout_inst, dct1pinpout_inst
