#!/bin/python
from myhdl import *

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


def dct1SinPout(output, enable_out, input, enable_in, clk, reset):

    @instance
    def logic():
        count = modbv(0)[3:]
        while True:
            yield clk.negedge
            enable_out.next = False
            if reset:
                count = modbv(0)[3:]
            elif enable_in:
                for index in range(8):
                    output[index].next = output[
                        index] + MULT_MAT[count][index] * input
                if count == 7:
                    for index in range(8):
                    	if index == 0:
                    		output[index].next = output[index].next - 128*8*92682
                    		
                        if intbv(output[index].next)[17]:
                            output[index].next = (output[index].next >> 18) + 1
                        else:
                            output[index].next = output[index].next >> 18

                    enable_out.next = True

                count += 1

    return logic
