#!/bin/python
from myhdl import *
from dctconstructs import *

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

    return logic
