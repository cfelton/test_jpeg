#!/bin/python
from myhdl import *
from dctconstructs import *
from dct1pinpout import *
from random import randrange

RANGE1_8 = range(8)


def print_list(signalList):
    for i in RANGE1_8:
        print "{:15d}".format(int(signalList[i])),
    print ""


def print_matrix(matrix):
    for i in RANGE1_8:
        print_list(matrix.pixelLine(i).pixels)

da = [[1, 9, 20, 7, 16, 5, 8, 2],
      [68, 54, 2, 39, 1, -1, -13, -12],
      [112, 93, 22, 54, 29, -11, 2, 5],
      [107, 72, 1, 57, 41, 1, 0, -17],
      [71, 26, -7, 23,  26, 3, -6, -7],
      [65, -56, 2, 28, -23, 10, -16, 0],
      [29, -58, 9, -1, 15, 28, -17, -1],
      [6, -24, 6, -3, -20, 0, -14, -3]]


def test():
    pixelBlock = PixelBlock()
    pixelLine = PixelLine()

    enable_in, enable_out, clk = [Signal(INACTIVE_LOW) for _ in range(3)]
    reset = Signal(INACTIVE_HIGH)

    @always(delay(10))
    def clkgen():
        clk.next = not clk

    @instance
    def stimulus():
        for i in RANGE1_8:
            for j in RANGE1_8:
                if j == 0:
                    pixelLine.pixels[j].next = da[i][j]
                else:
                    pixelLine.pixels[j].next = da[i][j]
            enable_in.next = True
            yield clk.negedge

        # reset.next = True if (randrange(6) == 0) else False

    @instance
    def monitor():
        while True:
            yield delay(11)
            print "\t".join(['en_out', 'en_in', 'reset', 'clk', 'now'])
            print "\t".join(["%d"]*5) % (enable_out, enable_in, reset, clk, now())
            print "-" * 72
            print_list(pixelLine.pixels)
            print "-" * 70
            print_matrix(pixelBlock)
            print "-" * 70
            yield delay(9)

    dct_inst = dct1PinPout(pixelBlock, enable_out, pixelLine, enable_in, clk, reset)

    sim = Simulation(clkgen, dct_inst, stimulus, monitor)
    sim.run(20 * 8 + 1)

if __name__ == '__main__':
    test()
