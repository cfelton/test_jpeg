#!/usr/bin/env python
# coding=utf-8


import pytest
import numpy as np

from itertools import chain

import myhdl
from myhdl import (StopSimulation, block, Signal, ResetSignal, intbv,
                   delay, instance, always_comb, always_seq)
from myhdl.conversion import verify

from jpegenc.subblocks.common import RGB, outputs_frontend, assign_array
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

@pytest.mark.skipif(not simsok, reason="missing installed simulator")
def test_frontend_conversion():

    samples, N = 1, 8

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)

    inputs = RGB()
    outputs = outputs_frontend()

    output_bits = outputs.out_precision
    in_out_data = InputsAndOutputs(samples, N)
    in_out_data.initialize()

    r_rom, g_rom, b_rom, y_out_rom, cb_out_rom, cr_out_rom =\
    in_out_data.get_rom_tables()

    @block
    def bench_frontend():

        tdut = frontend_top_level(inputs, outputs, clock, reset)
        tbclock = clock_driver(clock)

        print_sig_y = [Signal(intbv(0, min=-2**output_bits, max=2**output_bits))
                     for _ in range(N**2)]
        print_sig_cb = [Signal(intbv(0, min=-2**output_bits, max=2**output_bits))
                     for _ in range(N**2)]
        print_sig_cr = [Signal(intbv(0, min=-2**output_bits, max=2**output_bits))
                        for _ in range(N**2)]
        print_sig_y_1 = [Signal(intbv(0, min=-2**output_bits, max=2**output_bits))
                            for _ in range(N**2)]
        print_sig_cb_1 = [Signal(intbv(0, min=-2**output_bits, max=2**output_bits))
                            for _ in range(N**2)]
        print_sig_cr_1 = [Signal(intbv(0, min=-2**output_bits, max=2**output_bits))
                       for _ in range(N**2)]

        @instance
        def tbstim():
            yield pulse_reset(reset, clock)
            inputs.data_valid.next = True

            for i in range(samples):
                for j in range(N**2):
                        inputs.red.next = r_rom[i * (N ** 2) + j]
                        inputs.green.next = g_rom[i * (N ** 2) + j]
                        inputs.blue.next = b_rom[i * (N ** 2) + j]
                        yield clock.posedge

        print_assign = []
        print_assign += [assign_array(print_sig_y_1, outputs.y_dct_out)]
        print_assign += [assign_array(print_sig_cb_1, outputs.cb_dct_out)]
        print_assign += [assign_array(print_sig_cr_1, outputs.cr_dct_out)]

        @instance
        def monitor():
            outputs_count = 0
            while outputs_count != samples:
                yield clock.posedge
                yield delay(1)
                if outputs.data_valid:

                    for i in range(N**2):
                        print_sig_y[i].next = y_out_rom[outputs_count*(N**2) + i]
                        print_sig_cb[i].next = cb_out_rom[outputs_count*(N**2) + i]
                        print_sig_cr[i].next = cr_out_rom[outputs_count*(N**2) + i]

                    yield delay(1)
                    print("Expected Outputs Y")
                    for i in range(N**2):
                        print("%d " % print_sig_y[i])
                    print("Actual Outputs Y")
                    for i in range(N**2):
                        print("%d " % print_sig_y_1[i])
                    print("------------------------------")

                    print("Expected Outputs Cb")
                    for i in range(N**2):
                        print("%d " % print_sig_cb[i])
                    print("Actual Outputs Cb")
                    for i in range(N**2):
                        print("%d " % print_sig_cb_1[i])
                    print("------------------------------")

                    print("Expected Outputs Cr")
                    for i in range(N**2):
                        print("%d " % print_sig_cr[i])
                    print("Actual Outputs Cr")
                    for i in range(N**2):
                        print("%d " % print_sig_cr_1[i])
                    print("------------------------------")

                    outputs_count += 1
            raise StopSimulation

        return tdut, tbclock, tbstim, monitor, print_assign

    run_testbench(bench_frontend)

if __name__ == '__main__':
    test_frontend()
    test_frontend_conversion()
