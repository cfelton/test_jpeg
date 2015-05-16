#!/bin/python
from myhdl import *
from dctconstructs import *


def dct1SinPout(pixelLine, enable_out, pixelValue, enable_in, clk, reset):
    temp_nbits = PRECISION_FACTOR + pixelLine.bitLength()

    @instance
    def logic():
        count = modbv(0)[3:]
        temp = [sintbv(0, temp_nbits) for _ in range(8)]

        while True:
            yield clk.posedge, reset.negedge

            enable_out.next = INACTIVE_LOW

            if reset == ACTIVE_LOW:
                count = modbv(0)[3:]
                temp = [sintbv(0, temp_nbits) for _ in range(8)]

            elif enable_in == ACTIVE_HIGH:
                if count == 0:
                    temp = [sintbv(0, temp_nbits) for _ in range(8)]

                for index in range(8):
                    temp[index][:] += MULT_MAT[count][index] * pixelValue

                if count == 7:

                    for index in range(8):
                        if index == 0:
                            temp[index][:] -= A_OFFSET

                        pixelLine.pixel(index).next = round_signed(
                            temp[index], temp_nbits, PRECISION_FACTOR)

                    enable_out.next = ACTIVE_HIGH

                count += 1

    return logic
