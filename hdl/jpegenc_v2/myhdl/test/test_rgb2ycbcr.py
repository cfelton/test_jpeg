#!/bin/python
from myhdl import *
from rgb2ycbcr import *
from random import randrange

ACTIVE_LOW, INACTIVE_HIGH = 0, 1


def test():
    ycbcr = YCbCr()
    rgb = RGB()

    clk, reset = Signal(True), ResetSignal(1, active=ACTIVE_LOW, async=True)

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
        rgb.next(randrange(256), randrange(256), randrange(256))

    @instance
    def monitor():
        print "\t".join(
            ['red', 'green', 'blue', 'y', 'cb', 'cr', 'reset', 'clk', 'now'])
        print "-" * 70
        while True:
            yield delay(11)
            print "\t".join(["%d"] * 9) % \
                (rgb.red, rgb.green, rgb.blue, ycbcr.y,
                 ycbcr.cb, ycbcr.cr, reset, clk, now())
            yield delay(9)

    rgb2ycbcr_inst = rgb2ycbcr(ycbcr, rgb, clk, reset)

    sim = Simulation(clkgen, rgb2ycbcr_inst, stimulus, monitor, resetOnStart)
    sim.run(500)

if __name__ == '__main__':
    test()
