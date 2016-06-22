#!/usr/bin/env python
# coding=utf-8

import myhdl
from myhdl import *
import numpy as np
from math import sqrt, cos, pi


def tuple_construct(matrix):
    a = []
    for i in matrix:
        for j in i:
            a.append(j)
    return tuple(a)


@myhdl.block
def bug(input, output, clock, reset):

    a = np.zeros((3,3))
    a = a.astype(int)
    rom = tuple_construct(a)

    counter = Signal(intbv(0, min=0, max=3))

    @always_seq(clock.posedge, reset)
    def bug():
        if counter == 3:
            counter.next = 0
        else:
            counter.next = counter + 1
            output.next = rom[int(counter)]




    return bug

input_s, output_s =[Signal(intbv(0, min=0, max=4)) for _ in range(2)]
clock = Signal(bool(0))
reset = ResetSignal(1, active=True, async=True)
inst = bug(input_s, output_s, clock, reset)
inst.convert(hdl='vhdl')

