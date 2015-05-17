#!/bin/python
from random import randrange
from myhdl import *
from commons import *
from dctconstructs import *
from dct1sinpout import *

RANGE1_8 = range(8)


def print_list(signalList):
    for i in RANGE1_8:
        print "{:7d}".format(int(signalList[i])),
    print ""


def print_matrix(matrix):
    for i in RANGE1_8:
        print_list(matrix[i])

data = [154, 123, 123, 123, 123, 123, 123, 136]


def test():
    pixelLine = PixelLine()
    pixelValue = Signal(intbv(0)[8:])

    enable_in, enable_out, clk = [Signal(INACTIVE_LOW) for _ in range(3)]
    reset = Signal(INACTIVE_HIGH)

    @always(delay(10))
    def clkgen():
        clk.next = not clk

    @instance
    def stimulus():
        enable_in.next = ACTIVE_HIGH
        for i in RANGE1_8:
            pixelValue.next = data[i]
            yield clk.negedge

    @instance
    def monitor():
        while True:
            yield delay(11)
            print "\t".join(['en_out', 'input', 'en_in', 'reset',
                             ' clk', '  now'])
            print "\t".join(["  %d"]*6) % (enable_out, pixelValue, enable_in,
                                           reset, clk, now())
            print "-" * 72
            print "-" * 72
            print_list(pixelLine.pixels)
            print "-" * 72
            yield delay(9)

    dct_inst = dct1SinPout(
        pixelLine, enable_out, pixelValue, enable_in, clk, reset)

    sim = Simulation(clkgen, dct_inst, stimulus, monitor)
    sim.run(20 * 8 + 1)

if __name__ == '__main__':
    test()
