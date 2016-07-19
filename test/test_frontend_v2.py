#!/usr/bin/env python
# coding=utf-8


import pytest
import numpy as np

from itertools import chain

import myhdl
from myhdl import (StopSimulation, block, Signal, ResetSignal, intbv,
                   delay, instance, always_comb, always_seq)
from myhdl.conversion import verify

from jpegenc.subblocks.common import RGB, outputs_frontend_new, assign_array
from jpegenc.subblocks.frontend import frontend_top_level_v2, frontend_transform

from jpegenc.testing import sim_available, run_testbench
from jpegenc.testing import clock_driver, reset_on_start, pulse_reset

simsok = sim_available('ghdl')
"""default simulator"""
verify.simulator = "ghdl"

class InputsAndOutputs(object):

    def __init__(self, samples=1, N=8):
        self.N = N
        self.inputs = []
        self.outputs = []
        self.samples = samples

    def initialize(self):
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
        random_matrix = np.random.rand(self.N, self.N)
        random_matrix = np.rint(255*random_matrix)
        random_matrix = random_matrix.astype(int)
        random_matrix = random_matrix.tolist()
        return random_matrix

    def get_rom_tables(self):
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
    component = ["Y", "Cb", "Cr"]
    print("Color Component Processing", component[i])
    print("Expected Outputs ===> ")
    print(expected_outputs[i])
    print("Actual Outputs   ===> ")
    print(actual_outputs)
    print("-"*40)

def test_frontend():

    samples, N = 1, 8

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)

    inputs = RGB()
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
            while samples_count != samples:
                clock_cycle_counter += 1
                yield clock.posedge
                yield delay(1)
                if outputs.data_valid:
                    for i in range(3):
                        while(outputs_count != 64):
                            yield delay(1)
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

test_frontend()
