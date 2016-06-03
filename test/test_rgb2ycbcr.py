from random import randrange

import myhdl
from myhdl import (StopSimulation, block, Signal, ResetSignal, intbv,
                   delay, instance, always_comb, always_seq)
from myhdl.conversion import verify

# never use import *
from jpegenc.subblocks.rgb2ycbcr import ColorSpace, RGB, YCbCr, rgb2ycbcr

@myhdl.block
def clock_driver(clock):
    @instance
    def clkgen():
        clock.next = False
        while True:
            yield delay(10)
            clock.next = not clock
    return clkgen


def reset_on_start(reset, clock):
    @instance
    def ros():
        reset.next = reset.active
        yield delay(40)
        yield clock.posedge
        reset.next = not reset.active


def test_color_translation(args=None):
    """
    ADD DESCRIPTION OF TEST, WHAT IS CHECKED, WHAT IS NOT, EXPECTED
    RESULTS, ETC.

    Arguments:
        args:
    """
    samples, frac_bits, nbits = 50, 14, 8
    pixel_bits, num_fractional_bits = nbits, frac_bits

    rgb, ycbcr = RGB(pixel_bits), YCbCr(pixel_bits)

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)

    # create the test input values and the output values
    inputs = dict(red=[], green=[], blue=[])
    expected_outputs = dict(y=[], cb=[], cr=[])
    actual_outputs = dict(y=[], cb=[], cr=[])

    @myhdl.block
    def bench_color_trans():
        tbdut = rgb2ycbcr(rgb, ycbcr, clock, reset, num_fractional_bits)
        tbclk = clock_driver(clock)

        @instance
        def tbstim():
            yield reset_on_start(reset, clock)

            for i in range(samples):
                r, g, b = [randrange(256) for _ in range(3)]
                for color, val in zip(('red', 'green', 'blue'), (r, g, b)):
                    inputs[color].append(val)

                yield clock.posedge

            raise StopSimulation

        return myhdl.instances()

    inst = bench_color_trans()
    inst.config_sim(trace=True)
    inst.run_sim()


def test_block_conversion():
    pass
