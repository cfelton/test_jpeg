#!/bin/python
from myhdl import *
from commons import *
from dctconstructs import PixelBlock
from quantizer import *

RANGE1_8 = range(8)


def print_list(signalList):
    for i in RANGE1_8:
        print "{:6d}".format(int(signalList[i])),
    print ""


def print_matrix(matrix):
    for i in RANGE1_8:
        print_list(matrix.pixelLine(i).pixels)

data = [
   [ 162, 41,  19,  72,  30,  12, -20, -12],
   [ 30, 109,  10,  32,  28, -16,  18,  -2],
   [-94, -60,  12, -44, -31,   6,  -3,   7],
   [-39, -83,  -6, -22, -13,  16,  -2,   3],
   [-31,  18,  -5, -13,  14,  -6,  11,  -6],
   [ -1, -12,  13,   0,  28,  13,   8,   3],
   [  4,  -3,  12,   6, -18, -13,   7,  13],
   [ -9,  11,   8, -16,  22,   1,   6,  11]
]

def test():
    iPixelBlock = PixelBlock()
    qPixelBlock = PixelBlock(24)

    clk = Signal(INACTIVE_HIGH)
    enable_in, enable_out = [Signal(INACTIVE_LOW) for _ in range(2)]
    reset = ResetSignal(1, active=ACTIVE_LOW, async=True)

    @always(delay(10))
    def clkgen():
        clk.next = not clk

    @instance
    def resetOnStart():
        reset.next = ACTIVE_LOW
        yield clk.negedge
        yield clk.negedge
        yield clk.negedge
        reset.next = INACTIVE_HIGH

    @always(clk.negedge)
    def stimulus():
        enable_in.next = ACTIVE_HIGH        
        
        for row in range(8):
            for col in range(8):
                iPixelBlock.pixelLine(row).pixel(col).next = data[row][col]

    @instance
    def monitor():
        while True:
            yield delay(1)
            print "\t".join(['e_in', 'e_out', 'reset', 'clk', 'now'])
            print "\t".join(["%d"]*5) % (enable_in, enable_out, reset, clk, now())
            print "-" * 70
            print_matrix(iPixelBlock)
            print "-" * 70
            print_matrix(qPixelBlock)
            print "-" * 70
            yield delay(19)

    quantizer_inst = quantizer(qPixelBlock, enable_out, iPixelBlock, enable_in, clk, reset)

    sim = Simulation(clkgen, quantizer_inst, stimulus, monitor)
    sim.run(20 + 1)

if __name__ == '__main__':
    test()
