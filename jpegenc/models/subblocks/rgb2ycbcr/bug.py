#!/usr/bin/env python
# coding=utf-8


from myhdl import *
from myhdl.conversion import *
from random import randrange

const = [-2, -3]

@block
def negative_assignment(a, b):

    #bug
    s1 = Signal(intbv(const[0], min=-10, max=10))
    s2 = Signal(intbv(const[1], min=-10, max=10))

    s3 = Signal(intbv(0, min=-100, max=100))
    s4=Signal(intbv(0,min=-2**33,max=2**33))

    @always_comb
    def logic():

        s3.next = s1+s2

        b.next = a

    return logic


def convert():

    a, b = [Signal(bool(0)) for _ in range(2)]
    instance = negative_assignment(a, b)
    instance.convert(hdl='verilog')

    # analysis of converted code
    analyze.simulator = 'iverilog'
    assert negative_assignment(a, b).analyze_convert == 0

if __name__ == '__main__':
    convert()
