#!/usr/bin/env python
# coding=utf-8

import numpy as np

import pytest
import myhdl
from myhdl import (StopSimulation, block, Signal, ResetSignal, intbv,
                                      delay, instance, always_comb, always_seq)
from myhdl.conversion import verify

from jpegenc.subblocks.common import outputs_2d, assign_array
from jpegenc.subblocks.zig_zag import zig_zag_scan, zig_zag
from jpegenc.testing import sim_available, run_testbench
from jpegenc.testing import clock_driver, reset_on_start, pulse_reset

from random import randrange

simsok = sim_available('ghdl')
"""default simulator"""
verify.simulator = "ghdl"

class InputsAndOutputs(object):

    """Inputs and Outputs Construction Class

    This class is used to create the inputs and the derive the ouputs from the
    software reference of the zig zag scan. Each element in the input list is fed in the
    test module and the outputs of the module are compared with the elements in the
    outputs list. These list are converted to tuples and used as ROMs in the
    convertible testbench

    """

    def __init__(self, samples, N, precision):
        self.N = N
        self.nrange = 2 ** (precision - 1)
        self.inputs = []
        self.outputs = []
        self.samples = samples

    def initialize(self):
        """Initialize the inputs and outputs lists"""
        zig_zag_obj = zig_zag_scan(self.N)
        for i in range(self.samples):
            random_list = [randrange(-self.nrange, self.nrange-1)
                           for _ in range(self.N**2)]
            self.inputs.append(random_list)
            zig_zag_result = zig_zag_obj.zig_zag(random_list)
            self.outputs.append(zig_zag_result)

    def get_rom_tables(self):
        """Convert the lists to tuples"""
        a, b = [[] for _ in range(2)]
        for i in self.inputs:
            for j in i:
                a.append(j)
        for i in self.outputs:
            for j in i:
                b.append(j)
        inputs_rom = tuple(a)
        expected_outputs_rom = tuple(b)
        return inputs_rom, expected_outputs_rom

def out_print(expected_outputs, actual_outputs, N):
    """Helper function for better printing of the results"""
    print("Expected Outputs ===> ")
    print(expected_outputs)
    print("Actual Outputs   ===> ")
    a = []
    for i in range(N**2):
        a.append(int(actual_outputs[i]))
    print(a)
    print("-"*40)

def test_zig_zag():
    """Zig Zag Scan MyHDL Test

    In this test is verified the correct behavior of the zig zag module
    """

    samples, output_bits, N = 5, 10, 8

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)

    inputs = outputs_2d(output_bits, N)
    outputs = outputs_2d(output_bits, N)

    in_out_data = InputsAndOutputs(samples, N, output_bits)
    in_out_data.initialize()

    @block
    def bench_zig_zag():
        tdut = zig_zag(inputs, outputs, clock, reset, N)
        tbclock = clock_driver(clock)

        @instance
        def tbstim():
            yield pulse_reset(reset, clock)
            inputs.data_valid.next = True

            for i in range(samples):
                for j in range(N**2):
                    inputs.out_sigs[j].next = in_out_data.inputs[i][j]
                yield clock.posedge

        @instance
        def monitor():
            outputs_count = 0
            yield outputs.data_valid.posedge
            yield delay(1)
            while(outputs_count != samples):
                out_print(in_out_data.outputs[outputs_count],
                          outputs.out_sigs, N)
                yield clock.posedge
                yield delay(1)
                outputs_count += 1
            raise StopSimulation

        return tdut, tbclock, tbstim, monitor

    run_testbench(bench_zig_zag)


@pytest.mark.skipif(not simsok, reason="missing installed simulator")
def test_zig_zag_conversion():
    """Convertible Zig Zag Module Test

    This is the convertible testbench which ensures that the overall
    design is convertible and verified for its correct behavior"""

    samples, output_bits, N = 5, 10, 8

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)

    inputs = outputs_2d(output_bits, N)
    outputs = outputs_2d(output_bits, N)

    in_out_data = InputsAndOutputs(samples, N, output_bits)
    in_out_data.initialize()

    inputs_rom, expected_outputs_rom = in_out_data.get_rom_tables()

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)

    @block
    def bench_zig_zag():
        tdut = zig_zag(inputs, outputs, clock, reset, N)
        tbclock = clock_driver(clock)
        tbrst = reset_on_start(reset, clock)

        print_sig = [Signal(intbv(0, min=-2**output_bits, max=2**output_bits))
                     for _ in range(N**2)]
        print_sig_1 = [Signal(intbv(0, min=-2**output_bits, max=2**output_bits))
                     for _ in range(N**2)]
        in_sigs = [Signal(intbv(0, min=-2**output_bits, max=2**output_bits))
                     for _ in range(N**2)]

        @instance
        def tbstim():
            inputs.data_valid.next = True

            for i in range(samples):
                for j in range(N**2):
                    in_sigs[j].next = inputs_rom[i*(N**2) + j]
                yield clock.posedge

        print_assign = assign_array(print_sig_1, outputs.out_sigs)
        input_assign = assign_array(inputs.out_sigs, in_sigs)

        @instance
        def monitor():
            outputs_count = 0
            yield outputs.data_valid.posedge
            yield delay(1)
            while(outputs_count != samples):
                for i in range(N**2):
                    print_sig[i].next = expected_outputs_rom[outputs_count * (N**2) + i]
                yield delay(1)
                print("Expected Outputs")
                for i in range(N**2):
                    print("%d " % print_sig[i])
                print("Actual Outputs")
                for i in range(N**2):
                    print("%d " % print_sig_1[i])
                print("------------------------------")
                outputs_count += 1
                yield clock.posedge
            raise StopSimulation

        return tdut, tbclock, tbstim, monitor, print_assign, input_assign, tbrst


    assert bench_zig_zag().verify_convert() == 0


if __name__ == '__main__':
    test_zig_zag()
    test_zig_zag_conversion()


