#!/bin/python
from myhdl import *

ACTIVE_LOW, INACTIVE_HIGH = False, True
INACTIVE_LOW, ACTIVE_HIGH = False, True

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


def sintbv(value, nbits):
    nbits -= 1
    min_value = -1 << nbits
    max_value = -min_value + 1

    return intbv(value, min_value, max_value)


class PixelLine(object):

    def __init__(self):
        self.pixels = [Signal(sintbv(0, 11)) for _ in range(8)]


def dct1SinPout(output, enable_out, input, enable_in, clk, reset):

    @instance
    def logic():
        count = modbv(0)[3:]
        temp = [sintbv(0, 28) for _ in range(8)]
        while True:
            yield clk.posedge, reset.negedge
            enable_out.next = INACTIVE_LOW
            if reset == ACTIVE_LOW:
                count = modbv(0)[3:]
                temp = [sintbv(0, 28) for _ in range(8)]
            elif enable_in == ACTIVE_HIGH:
                for index in range(8):
                    temp[index][:] += MULT_MAT[count][index] * input

                if count == 7:
                    for index in range(8):
                        if index == 0:
                            temp[index][:] -= A_OFFSET

                        output.pixels[index].next = round_signed(
                            temp[index], 28, 18)

                    enable_out.next = True

                count += 1

    def round_signed(val, msb, lsb):
        if val[lsb - 1]:
            return val[msb:lsb].signed() + 1

        return val[msb:lsb].signed()

    return logic
