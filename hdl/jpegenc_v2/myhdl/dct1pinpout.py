#!/bin/python
from myhdl import *
from dctconstructs import *


def dct1PinPout(pixelBlock, enable_out, pixelLine, enable_in, clk, reset):
    temp_nbits = PRECISION_FACTOR + pixelBlock.bitLength()

    @instance
    def logic():
        count = modbv(0)[3:]
        temp = [[sintbv(0, temp_nbits) for _ in range(8)] for _ in range(8)]

        while True:
            yield clk.posedge, reset.negedge

            enable_out.next = INACTIVE_LOW

            if reset == ACTIVE_LOW:
                count = modbv(0)[3:]
                temp = [[sintbv(0, temp_nbits) for _ in range(8)]
                        for _ in range(8)]

            elif enable_in == ACTIVE_HIGH:
                if count == 0:
                    temp = [[sintbv(0, temp_nbits) for _ in range(8)]
                            for _ in range(8)]

                for row in range(8):
                    for index in range(8):
                        temp[index][row] += MULT_MAT[count][index] * \
                            pixelLine.pixels[row]

                if count == 7:
                    for row in range(8):
                        for index in range(8):
                            pixelBlock.pixelLine(index).pixel(row).next = \
                                round_signed(
                                    temp[index][row], temp_nbits, PRECISION_FACTOR)

                    enable_out.next = True
                count += 1

    return logic
