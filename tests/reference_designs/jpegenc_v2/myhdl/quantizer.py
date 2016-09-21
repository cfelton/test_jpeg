#!/bin/python
from myhdl import *
from commons import *

PRECISION_FACTOR = 12

MULT_FACTOR = 1 << PRECISION_FACTOR

Y_QUANT_MAT = [
    [16, 11, 10, 16, 24, 40, 51, 61],
    [12, 12, 14, 19, 26, 58, 60, 55],
    [14, 13, 16, 24, 40, 57, 69, 56],
    [14, 17, 22, 29, 51, 87, 80, 62],
    [18, 22, 37, 56, 58, 109, 103, 77],
    [24, 35, 55, 64, 81, 104, 113, 92],
    [49, 64, 78, 87, 103, 121, 120, 101],
    [72, 92, 95, 98, 112, 100, 103, 99]
]

CbCr_QUANT_MAT = [
    [17, 18, 24, 47, 99, 99, 99, 99],
    [18, 21, 26, 66, 99, 99, 99, 99],
    [24, 26, 56, 99, 99, 99, 99, 99],
    [44, 66, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99],
]

for row in range(8):
    for col in range(8):
        Y_QUANT_MAT[row][col] = MULT_FACTOR / Y_QUANT_MAT[row][col]
        CbCr_QUANT_MAT[row][col] = MULT_FACTOR / CbCr_QUANT_MAT[row][col]

ColorComponent = enum('Luminance', 'Chrominance')


def quantizer(qPixelBlock, enable_out, iPixelBlock, enable_in,
              clk, reset, colorComponent=ColorComponent.Luminance):
    """ A Quantizer with option choosing quantization matrix.

    I/O pins:
    --------
    qPixelBlock     : output array of array of 12-bit signed value
    enable_out      : output ACTIVE_HIGH when output is available
    iPixelBlock     : input array of array of 12-bit signed value
    enable_in       : input ACTIVE_HIGH when input is available
    clk             : input clock boolean signal
    reset           : input reset boolean signal
    colorComponent  : input whether color component is Luminance or Chrominance

    """

    temp_nbits = PRECISION_FACTOR + qPixelBlock.bitLength()

    QUANT_MAT = Y_QUANT_MAT \
        if colorComponent == ColorComponent.Luminance \
        else CbCr_QUANT_MAT

    @always_seq(clk.posedge, reset=reset)
    def logic():
        enable_out.next = INACTIVE_LOW

        if enable_in == ACTIVE_HIGH:
            for row in range(8):
                for col in range(8):
                    temp = sintbv(iPixelBlock.pixelLine(row).pixel(col) *
                                  QUANT_MAT[row][col], temp_nbits)

                    qPixelBlock.pixelLine(row).pixel(col).next = \
                        round_signed(temp, temp_nbits, PRECISION_FACTOR)

            enable_out.next = ACTIVE_HIGH

    return logic
