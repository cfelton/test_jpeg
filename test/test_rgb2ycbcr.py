from random import randrange

import pytest
import myhdl
from myhdl import (StopSimulation, block, Signal, ResetSignal, intbv,
                   delay, instance, always_comb, always_seq)
from myhdl.conversion import verify

from jpegenc.subblocks.color_converters import ColorSpace, rgb2ycbcr
from jpegenc.subblocks.common import RGB, YCbCr
from jpegenc.testing import sim_available, run_testbench
from jpegenc.testing import clock_driver, reset_on_start, pulse_reset

simsok = sim_available('iverilog') and sim_available('ghdl')


def print_results(inputs, expected_outputs, actual_outputs):
    """Print the results of the Simulation
    """
    for i in range(len(list(actual_outputs.values())[0])):
        print("Expected Outputs ===> y = %d cb = %d cr = %d"
              % (expected_outputs['y'][i], expected_outputs['cb'][i],
                 expected_outputs['cr'][i]))
        print("Actual Outputs ===> y = %d cb = %d cr = %d"
              % (actual_outputs['y'][i], actual_outputs['cb'][i],
                 actual_outputs['cr'][i]))
        print("-"*40)


class InputsAndOutputs(object):

    """Contains the common data and modules
    for the two tests
    """

    def __init__(self, samples):
        """create the test input values and the output values"""
        self.inputs = dict(red=[], green=[], blue=[])
        self.expected_outputs = dict(y=[], cb=[], cr=[])
        self.actual_outputs = dict(y=[], cb=[], cr=[])
        self.samples = samples

    def initialize(self):
        """Initialize the inputs and outputs"""
        for i in range(self.samples):
            r, g, b = [randrange(256) for _ in range(3)]
            a = ColorSpace(r, g, b)
            y, cb, cr = [a.get_jfif_ycbcr()[j] for j in range(3)]
            for color, val in zip(('red', 'green', 'blue'), (r, g, b)):
                self.inputs[color].append(val)
            for ycbcr_out, val in zip(('y', 'cb', 'cr'),
                                      (int(y), int(cb), int(cr))):
                self.expected_outputs[ycbcr_out].append(val)

    def get_rom_tables(self):
        """Construct rom tables for convertible test-bench"""
        exp_y = tuple(self.expected_outputs['y'])
        exp_cb = tuple(self.expected_outputs['cb'])
        exp_cr = tuple(self.expected_outputs['cr'])

        in_r = tuple(self.inputs['red'])
        in_g = tuple(self.inputs['green'])
        in_b = tuple(self.inputs['blue'])

        a = [exp_y, exp_cb, exp_cr]
        b = [in_r, in_g, in_b]
        return a, b


def test_color_translation():
    """
    In the current test are tested the outputs
    of the rgb2ycbcr module with the outputs of a
    python color space conversion function
    """
    samples, frac_bits, nbits = 50, 14, 8
    pixel_bits, num_fractional_bits = nbits, frac_bits

    rgb, ycbcr = RGB(pixel_bits), YCbCr(pixel_bits)

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)

    in_out_data = InputsAndOutputs(samples)
    in_out_data.initialize()

    @myhdl.block
    def bench_color_trans():
        tbdut = rgb2ycbcr(rgb, ycbcr, clock, reset, num_fractional_bits)
        tbclk = clock_driver(clock)

        @instance
        def tbstim():
            yield pulse_reset(reset, clock)
            rgb.data_valid.next = True

            for i in range(samples):

                # rgb signal assignment in the dut
                rgb.red.next = in_out_data.inputs['red'][i]
                rgb.green.next = in_out_data.inputs['green'][i]
                rgb.blue.next = in_out_data.inputs['blue'][i]

                if ycbcr.data_valid == 1:
                    for ycbcr_act, val in zip(('y', 'cb', 'cr'),
                                              (int(ycbcr.y), int(ycbcr.cb),
                                               int(ycbcr.cr))):

                        in_out_data.actual_outputs[ycbcr_act].append(val)

                yield clock.posedge

            print_results(in_out_data.inputs, in_out_data.expected_outputs,
                          in_out_data.actual_outputs)
            raise StopSimulation

        return tbdut, tbclk, tbstim

    run_testbench(bench_color_trans)


@pytest.mark.skipif(not simsok, reason="missing installed simulator")
def test_block_conversion():
    """
    In the current test are tested the outputs of the
    converted testbench in verilog and VHDL with the outputs
    of the myhdl module
    """
    samples, frac_bits, nbits = 50, 14, 8
    pixel_bits, num_fractional_bits = nbits, frac_bits

    rgb, ycbcr = RGB(pixel_bits), YCbCr(pixel_bits)

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)

    in_out_data = InputsAndOutputs(samples)
    in_out_data.initialize()

    exp_y, exp_cb, exp_cr = in_out_data.get_rom_tables()[0]

    in_r, in_g, in_b = in_out_data.get_rom_tables()[1]

    y_s, cb_s, cr_s = [Signal(intbv(0)[pixel_bits:])
                       for _ in range(3)]

    @myhdl.block
    def bench_color_trans():
        tbdut = rgb2ycbcr(rgb, ycbcr, clock, reset, num_fractional_bits)
        tbclk = clock_driver(clock)
        tbrst = reset_on_start(reset, clock)

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
