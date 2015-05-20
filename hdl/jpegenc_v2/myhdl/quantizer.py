#!/bin/python
from myhdl import *
from commons import *

PRECISION_FACTOR = 12

MULT_FACTOR = 1 << PRECISION_FACTOR

QUANT_MAT = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
]

for row in range(8):
    for col in range(8):
        QUANT_MAT[row][col] = MULT_FACTOR / QUANT_MAT[row][col]


def quantizer(qPixelBlock, enable_out, iPixelBlock, enable_in, clk, reset):

    temp_nbits = PRECISION_FACTOR + qPixelBlock.bitLength()

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
