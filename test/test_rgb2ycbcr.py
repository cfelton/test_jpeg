from random import randrange

import myhdl
from myhdl import (StopSimulation, block, Signal, ResetSignal, intbv,
                   delay, instance, always_comb, always_seq)
from myhdl.conversion import verify

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
    reset.next = True
    yield delay(40)
    yield clock.posedge
    reset.next = not reset


@myhdl.block
def rstonstart(reset, clock):
    @instance
    def ros():
        reset.next = True
        yield delay(40)
        yield clock.posedge
        reset.next = not reset
    return ros


def print_results(inputs, expected_outputs, actual_outputs):
    """Print the results of the Simulation
    """
    for i in range(len(actual_outputs.values()[0])):
        print("Expected Outputs ===> y = %d cb = %d cr = %d"
              % (expected_outputs['y'][i], expected_outputs['cb'][i],
                 expected_outputs['cr'][i]))
        print("Actual Outputs ===> y = %d cb = %d cr = %d"
              % (actual_outputs['y'][i], actual_outputs['cb'][i],
                 actual_outputs['cr'][i]))
        print("-"*40)


def color_translation(convertible=False):
    """
    In the current test are tested the actual outputs
    of the rgb2ycbcr module with the outputs of a
    python color space conversion function.
    If convertible is true then it is tested the converted
    testbench. If not the the implementation in myhdl
    is tested.

    Args:
        convertible
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

    for i in range(samples):
        r, g, b = [randrange(256) for _ in range(3)]
        a = ColorSpace(r, g, b)
        y, cb, cr = [a.get_jfif_ycbcr()[j] for j in range(3)]
        for color, val in zip(('red', 'green', 'blue'), (r, g, b)):
            inputs[color].append(val)
        for ycbcr_out, val in zip(('y', 'cb', 'cr'),
                                  (int(y), int(cb), int(cr))):
            expected_outputs[ycbcr_out].append(val)

    if(not convertible):
        @myhdl.block
        def bench_color_trans():
            tbdut = rgb2ycbcr(rgb, ycbcr, clock, reset, num_fractional_bits)
            tbclk = clock_driver(clock)

            @instance
            def tbstim():
                yield reset_on_start(reset, clock)
                rgb.data_valid.next = True

                for i in range(samples):

                    # rgb signal assignment in the dut
                    rgb.red.next = inputs['red'][i]
                    rgb.green.next = inputs['green'][i]
                    rgb.blue.next = inputs['blue'][i]

                    if ycbcr.data_valid == 1:
                        for ycbcr_act, val in zip(('y', 'cb', 'cr'),
                                                  (int(ycbcr.y), int(ycbcr.cb),
                                                   int(ycbcr.cr))):

                            actual_outputs[ycbcr_act].append(val)

                    yield clock.posedge

                print_results(inputs, expected_outputs, actual_outputs)
                raise StopSimulation

            return tbdut, tbclk, tbstim

        inst = bench_color_trans()
        inst.config_sim(trace=True)
        inst.run_sim()

    else:

        exp_y = tuple(expected_outputs['y'])
        exp_cb = tuple(expected_outputs['cb'])
        exp_cr = tuple(expected_outputs['cr'])

        in_r = tuple(inputs['red'])
        in_g = tuple(inputs['green'])
        in_b = tuple(inputs['blue'])

        y_s, cb_s, cr_s = [Signal(intbv(0)[pixel_bits:])
                           for _ in range(3)]

        @myhdl.block
        def bench_color_trans():
            tbdut = rgb2ycbcr(rgb, ycbcr, clock, reset, num_fractional_bits)
            tbclk = clock_driver(clock)
            tbrst = rstonstart(reset, clock)

            @instance
            def tbstim():
                yield reset.negedge
                rgb.data_valid.next = True

                for i in range(samples):
                    # rgb signal assignment in the dut
                    rgb.red.next = in_r[i]
                    rgb.green.next = in_g[i]
                    rgb.blue.next = in_b[i]

                    if ycbcr.data_valid == 1:

                        # expected_outputs signal assignment
                        y_s.next = exp_y[i-3]
                        cb_s.next = exp_cb[i-3]
                        cr_s.next = exp_cr[i-3]
                        yield delay(1)
                        print("Expected outputs ===>Y:%d Cb:%d Cr:%d"
                              % (y_s, cb_s, cr_s))
                        print("Actual outputs ===>Y:%d Cb:%d Cr:%d"
                              % (ycbcr.y, ycbcr.cb, ycbcr.cr))
                        print("----------------------------")
                    yield clock.posedge

                raise StopSimulation

            return tbdut, tbclk, tbstim, tbrst

        # verify and convert with iverilog
        verify.simulator = 'iverilog'
        assert bench_color_trans().verify_convert() == 0
        # verify and convert with GHDL
        verify.simulator = 'ghdl'
        assert bench_color_trans().verify_convert() == 0


def test_color_translation():
    color_translation(convertible=False)
    color_translation(convertible=True)
