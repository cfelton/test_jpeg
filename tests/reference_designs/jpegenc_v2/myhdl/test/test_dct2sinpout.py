
from __future__ import print_function, division

from random import randrange

from myhdl import *

from commons import *
from dctconstructs import *
from dct2sinpout import *

RANGE1_8 = range(8)


def print_list(signalList):
    for i in RANGE1_8:
        print("{:6d}".format(int(signalList[i])),)
    print("")


def print_matrix(matrix):
    for i in RANGE1_8:
        print_list(matrix.pixelLine(i).pixels)

data = [
    [154, 123, 123, 123, 123, 123, 123, 136],
    [192, 180, 136, 154, 154, 154, 136, 110],
    [254, 198, 154, 154, 180, 154, 123, 123],
    [239, 180, 136, 180, 180, 166, 123, 123],
    [180, 154, 136, 167, 166, 149, 136, 136],
    [128, 136, 123, 136, 154, 180, 198, 154],
    [123, 105, 110, 149, 136, 136, 180, 166],
    [110, 136, 123, 123, 123, 136, 154, 136]
]


def test():
    pixelBlock = PixelBlock()
    pixelVal = Signal(intbv(0)[8:])

    enable_in, enable_out, clk = [Signal(INACTIVE_LOW) for _ in range(3)]
    reset = Signal(INACTIVE_HIGH)

    @always(delay(10))
    def clkgen():
        clk.next = not clk

    @instance
    def stimulus():
        for i in RANGE1_8:
            for j in RANGE1_8:
                pixelVal.next = data[i][j]
                enable_in.next = ACTIVE_HIGH
                yield clk.negedge

    @instance
    def monitor():
        while True:
            yield delay(11)
            print("\t".join(['input', 'en_out', 'en_in', 'reset',
                             'clk', 'now']))
            print("\t".join(["%d"]*6) % (pixelVal, enable_out,
                                         enable_in, reset, clk, now()))
            print("-" * 70)
            print_matrix(pixelBlock)
            print("-" * 70)
            yield delay(9)

    dct_inst = dct2SinPout(
        pixelBlock, enable_out, pixelVal, enable_in, clk, reset)

    sim = Simulation(clkgen, dct_inst, stimulus, monitor)
    sim.run(20 * (8 * 8 + 1) + 1)

if __name__ == '__main__':
    test()
