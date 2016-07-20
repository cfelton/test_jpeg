from random import randrange

import pytest
import myhdl
from myhdl import (StopSimulation, block, Signal, ResetSignal, intbv,
                   delay, instance, always_comb, always_seq)
from myhdl.conversion import verify

from jpegenc.subblocks.color_converters import ColorSpace, rgb2ycbcr_v2
from jpegenc.subblocks.common import RGB_v2, YCbCr_v2
from jpegenc.testing import sim_available, run_testbench
from jpegenc.testing import clock_driver, reset_on_start, pulse_reset

simsok = sim_available('ghdl')
"""default simulator"""
verify.simulator = "ghdl"


def print_results(expected_outputs, actual_outputs, i):
    """Print the results of the Simulation
    """
    print("Expected Outputs ===> y = %d cb = %d cr = %d"
          % (expected_outputs['y'][i], expected_outputs['cb'][i],
             expected_outputs['cr'][i]))
    print("Actual Outputs ===> y = %d cb = %d cr = %d"
          % (actual_outputs[0], actual_outputs[1],
             actual_outputs[2]))
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
    samples, frac_bits, nbits = 8, 14, 8
    pixel_bits, num_fractional_bits = nbits, frac_bits

    rgb, ycbcr = RGB_v2(pixel_bits), YCbCr_v2(pixel_bits)

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)

    in_out_data = InputsAndOutputs(samples)
    in_out_data.initialize()

    @myhdl.block
    def bench_color_trans():
        tbdut = rgb2ycbcr_v2(rgb, ycbcr, clock, reset, num_fractional_bits)
        tbclk = clock_driver(clock)

        @instance
        def tbstim():
            yield pulse_reset(reset, clock)
            rgb.data_valid.next = True

            for i in range(samples):
                for j in range(3):
                    # rgb signal assignment in the dut
                    rgb.red.next = in_out_data.inputs['red'][i]
                    rgb.green.next = in_out_data.inputs['green'][i]
                    rgb.blue.next = in_out_data.inputs['blue'][i]
                    rgb.color_mode.next = j
                    yield clock.posedge

        @instance
        def monitor():
            samples_count = 0
            output_list = []
            yield ycbcr.data_valid.posedge
            yield delay(1)
            while samples_count != samples:
                    for i in range(3):
                        output_list.append(int(ycbcr.data_out))
                        yield clock.posedge
                        yield delay(1)
                    print_results(in_out_data.expected_outputs, output_list,
                                  samples_count)
                    output_list = []
                    samples_count += 1
            raise StopSimulation

        return tbdut, tbclk, tbstim, monitor

    run_testbench(bench_color_trans)

test_color_translation()
#TODO Create the convertible testbench
