#!/usr/bin/env python
# coding=utf-8


import pytest
import numpy as np

from itertools import chain

import myhdl
from myhdl import (StopSimulation, block, Signal, ResetSignal, intbv,
                   delay, instance, always_comb, always_seq)
from myhdl.conversion import verify

from jpegenc.subblocks.common import outputs_frontend_new, inputs_frontend_new, assign_array
from jpegenc.subblocks.frontend import frontend_top_level_v2, frontend_transform

from jpegenc.testing import sim_available, run_testbench
from jpegenc.testing import clock_driver, reset_on_start, pulse_reset

simsok = sim_available('ghdl')
"""default simulator"""
verify.simulator = "ghdl"

class InputsAndOutputs(object):

    """Inputs and Outputs Construction Class

    This class is used to create the inputs and the derive the ouputs from the
    software reference of the frontend part of the encoder. Each element in the input
    list is fed in the test module and the outputs of the module are compared with the
    elements in the outputs list. These list are converted to tuples and used as ROMs
    in the convertible testbench

    """

    def __init__(self, samples=1, N=8):
        self.N = N
        self.inputs = []
        self.outputs = []
        self.samples = samples

    def initialize(self):
        """Initialize the inputs and outputs lists"""
        for i in range(self.samples):
            rgb_blocks = []
            for i in range(3):
                random_matrix = self.random_matrix()
                rgb_blocks.append(random_matrix)
            self.inputs.append(rgb_blocks)
            front_result = frontend_transform(rgb_blocks[0], rgb_blocks[1],
                                              rgb_blocks[2])
            self.outputs.append(front_result)

    def random_matrix(self):
        """Create a random NxN matrix with values from 0 to 255"""
        random_matrix = np.random.rand(self.N, self.N)
        random_matrix = np.rint(255*random_matrix)
        random_matrix = random_matrix.astype(int)
        random_matrix = random_matrix.tolist()
        return random_matrix

    def get_rom_tables(self):
        """Convert the lists to tuples"""
        r_temp, g_temp, b_temp = [[] for _ in range(3)]
        y_dct_temp, cb_dct_temp, cr_dct_temp = [[] for _ in range(3)]
        for i in range(self.samples):
            r_temp += self.inputs[i][0]
            g_temp += self.inputs[i][1]
            b_temp += self.inputs[i][2]
            y_dct_temp += self.outputs[i][0]
            cb_dct_temp += self.outputs[i][1]
            cr_dct_temp += self.outputs[i][2]

        r_rom = tuple(list(chain.from_iterable(r_temp)))
        g_rom = tuple(list(chain.from_iterable(g_temp)))
        b_rom = tuple(list(chain.from_iterable(b_temp)))
        y_out_rom = tuple(y_dct_temp)
        cb_out_rom = tuple(cb_dct_temp)
        cr_out_rom = tuple(cr_dct_temp)

        return  r_rom, g_rom, b_rom, y_out_rom, cb_out_rom, cr_out_rom

def out_print(expected_outputs, actual_outputs, N, i):
    """Helper function for better printing of the results"""
    component = ["Y", "Cb", "Cr"]
    print("Color Component Processing", component[i])
    print("Expected Outputs ===> ")
    print(expected_outputs[i])
    print("Actual Outputs   ===> ")
    print(actual_outputs)
    print("-"*40)

def test_frontend():
    """Frontend Part of the JPEG Encoder MyHDL Test

    In this test is verified the correct behavior of the frontend part
    of the endocer
    """

    samples, N = 2, 8

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)

    inputs = inputs_frontend_new()
    outputs = outputs_frontend_new()

    in_out_data = InputsAndOutputs(samples, N)
    in_out_data.initialize()

    @block
    def bench_frontend():

        tdut = frontend_top_level_v2(inputs, outputs, clock, reset)
        tbclock = clock_driver(clock)

        @instance
        def tbstim():
            yield pulse_reset(reset, clock)
            inputs.data_valid.next = True
            inputs.ready_backend.next = True

            for i in range(samples):
                for n in range(3):
                    for j in range(N):
                        for k in range(N):
                            inputs.red.next = in_out_data.inputs[i][0][j][k]
                            inputs.green.next = in_out_data.inputs[i][1][j][k]
                            inputs.blue.next = in_out_data.inputs[i][2][j][k]
                            yield clock.posedge

        @instance
        def monitor():
            samples_count = 0
            outputs_count = 0
            outputs_list = []
            clock_cycle_counter = 0
            while(outputs.data_valid == False):
                yield clock.posedge
                clock_cycle_counter += 1
            while samples_count != samples:
                print("Processing Block %d" %(samples_count+1))
                for i in range(3):
                    while(outputs_count != 64):
                        outputs_list.append(int(outputs.data_out))
                        outputs_count += 1
                        clock_cycle_counter += 1
                        yield clock.posedge
                    out_print(in_out_data.outputs[samples_count],
                                outputs_list, N, i)
                    outputs_count = 0
                    outputs_list = []
                samples_count += 1
            print("Clock Cycles taken for the block conversion:",
                  clock_cycle_counter)
            raise StopSimulation

        return tdut, tbclock, tbstim, monitor

    run_testbench(bench_frontend)

@pytest.mark.skipif(not simsok, reason="missing installed simulator")
def test_frontend_conversion():
    """Convertible Frontend Part of the JPEG Encoder Test

    This is the convertible testbench which ensures that the overall
    design is convertible and verified for its correct behavior"""

    samples, N = 2, 8

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)

    inputs = inputs_frontend_new()
    outputs = outputs_frontend_new()

    in_out_data = InputsAndOutputs(samples, N)
    in_out_data.initialize()

    r_rom, g_rom, b_rom, y_out_rom,\
    cb_out_rom, cr_out_rom = in_out_data.get_rom_tables()


    @block
    def bench_frontend():
        print_sig = Signal(intbv(0, min=-outputs.out_range, max=outputs.out_range))
        tdut = frontend_top_level_v2(inputs, outputs, clock, reset)
        tbclock = clock_driver(clock)
        tbrst = reset_on_start(reset, clock)

        @instance
        def tbstim():
            yield reset.negedge
            inputs.data_valid.next = True

            for i in range(samples):
                for n in range(3):
                    for j in range(64 * i, 64 * (i + 1)):
                        inputs.red.next = r_rom[j]
                        inputs.green.next = g_rom[j]
                        inputs.blue.next = b_rom[j]
                        yield clock.posedge

        @instance
        def monitor():
            samples_count = 0
            outputs_count = 0
            clock_cycle_counter = 0
            yield outputs.data_valid.posedge
            while(samples_count < samples):
                print("Processing Block %d" % (samples_count))
                for i in range(3):
                    while(outputs_count != 64):
                        if i == 0:
                            print_sig.next = y_out_rom[outputs_count + samples_count*64]
                        elif i == 1:
                            print_sig.next = cb_out_rom[outputs_count + samples_count*64]
                        else:
                            print_sig.next = cr_out_rom[outputs_count + samples_count*64]
                        yield delay(1)
                        print("%d %d" % (outputs.data_out, print_sig))
                        outputs_count += 1
                        clock_cycle_counter += 1
                        yield clock.posedge
                    outputs_count = 0
                samples_count += 1
            raise StopSimulation

        return tdut, tbclock, tbstim, monitor, tbrst

    assert bench_frontend().verify_convert() == 0

if __name__ == '__main__':
    test_frontend()
    test_frontend_conversion()
