
from myhdl import *
from random import randrange
from commons import *
from rgb2ycbcr import *


def test():
    ycbcr = YCbCr()
    rgb = RGB()

    clk, enable_in, enable_out = [Signal(INACTIVE_LOW) for _ in range(3)]
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
        rgb.next(randrange(256), randrange(256), randrange(256))
        enable_in.next = INACTIVE_LOW if randrange(6) == 0 else ACTIVE_HIGH

    @instance
    def monitor():
        print("\t".join(
            ['red', 'green', 'blue', 'e_in', 'y', 'cb', 'cr',
             'e_out', 'reset', 'clk', 'now']))
        print("-" * 70)
        while True:
            yield delay(11)
            print("\t".join(["%d"] * 11) %
                  (rgb.red, rgb.green, rgb.blue, enable_in,
                   ycbcr.y, ycbcr.cb, ycbcr.cr, enable_out,
                   reset, clk, now()))
            yield delay(9)

    rgb2ycbcr_inst = rgb2ycbcr(ycbcr, enable_out, rgb, enable_in, clk, reset)

    sim = Simulation(clkgen, rgb2ycbcr_inst, stimulus, monitor, resetOnStart)
    sim.run(500)

if __name__ == '__main__':
    test()
