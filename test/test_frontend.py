#!/usr/bin/env python
# coding=utf-8


import pytest
import numpy as np

from itertools import chain

import myhdl
from myhdl import (StopSimulation, block, Signal, ResetSignal, intbv,
                   delay, instance, always_comb, always_seq)
from myhdl.conversion import verify

from jpegenc.subblocks.common import RGB, outputs_frontend
from jpegenc.subblocks.frontend import frontend_top_level, frontend_transform

from jpegenc.testing import sim_available, run_testbench
from jpegenc.testing import clock_driver, reset_on_start, pulse_reset

simsok = sim_available('ghdl') and sim_available('iverilog')

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

        for i in range(self.samples):
            r_rom, g_rom, b_rom = [tuple(list(chain.from_iterable(self.inputs[i][j]))) for j in range(3)]
            y_final_rom, cb_final_rom, cr_final_rom = [tuple(list(chain.from_iterable(self.outputs[i][j]))) for j in range(3)]

        return  r_rom, g_rom, b_rom, y_final_rom, cb_final_rom, cr_final_rom

def out_print(expected_outputs, actual_outputs, N):

    print("Expected Outputs ===> ")
    print(expected_outputs[0])
    print(expected_outputs[1])
    print(expected_outputs[2])
    print("Actual Outputs   ===> ")
    a, b, c = [[] for _ in range(3)]
    for i in range(N**2):
        a.append(int(actual_outputs.y_dct_out[i]))
        b.append(int(actual_outputs.cb_dct_out[i]))
        c.append(int(actual_outputs.cr_dct_out[i]))
    print(a)
    print(b)
    print(c)
    print("-"*40)

def test_frontend():

    samples, N = 5, 8

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)

    inputs = RGB()
    outputs = outputs_frontend()

    in_out_data = InputsAndOutputs(samples, N)
    in_out_data.initialize()

    @block
    def bench_frontend():

        tdut = frontend_top_level(inputs, outputs, clock, reset)
        tbclock = clock_driver(clock)

        @instance
        def tbstim():
            yield pulse_reset(reset, clock)
            inputs.data_valid.next = True

            for i in range(samples):
                for j in range(N):
                    for k in range(N):
                        inputs.red.next = in_out_data.inputs[i][0][j][k]
                        inputs.green.next = in_out_data.inputs[i][1][j][k]
                        inputs.blue.next = in_out_data.inputs[i][2][j][k]
                        yield clock.posedge

        @instance
        def monitor():
            outputs_count = 0
            while outputs_count != samples:
                yield clock.posedge
                yield delay(1)
                if outputs.data_valid:
                    out_print(in_out_data.outputs[outputs_count],
                                outputs, N)
                    outputs_count += 1
            raise StopSimulation

        return tdut, tbclock, tbstim, monitor

    run_testbench(bench_frontend)


test_frontend()



