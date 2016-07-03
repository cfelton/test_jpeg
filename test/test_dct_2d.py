#!/usr/bin/env python
# coding=utf-8

import numpy as np

import pytest
import myhdl
from myhdl import (StopSimulation, block, Signal, ResetSignal, intbv,
                   delay, instance, always_comb, always_seq)
from myhdl.conversion import verify

from jpegenc.subblocks.common import (input_interface, output_interface,
                                                 input_1d_2nd_stage,outputs_2d)

from jpegenc.subblocks.dct import dct_2d
from jpegenc.subblocks.dct.dct_2d import dct_2d_transformation
from jpegenc.testing import sim_available

simsok = sim_available('ghdl') and sim_available('iverilog')


class InputsAndOutputs(object):

    def __init__(self, samples, N):
        self.N = N
        self.inputs = []
        self.outputs = []
        self.samples = samples

    def initialize(self):
        dct_obj = dct_2d_transformation(self.N)
        for i in range(self.samples):
            random_matrix = self.random_matrix_8_8()
            self.inputs.append(random_matrix)
            dct_result = dct_obj.dct_2d_transformation(random_matrix)
            self.outputs.append(dct_result)

    def random_matrix_8_8(self):
        random_matrix = np.random.rand(self.N, self.N)
        random_matrix = np.rint(255*random_matrix)
        random_matrix = random_matrix.astype(int)
        random_matrix = random_matrix.tolist()
        return random_matrix

    def get_rom_tables(self):
        a, b = [[] for _ in range(2)]
        for i in self.inputs:
            for j in i:
                for k in j:
                  a.append(k)
        for i in self.outputs:
            for j in i:
                for k in j:
                    b.append(k)
        inputs_rom = tuple(a)
        expected_outputs_rom = tuple(b)
        return inputs_rom, expected_outputs_rom


def out_print(expected_outputs, actual_outputs, N):

    print("Expected Outputs ===> ")
    print(expected_outputs)
    print("Actual Outputs   ===> ")
    a = []
    for i in range(N):
        b = []
        for j in range(N):
            b.append(int(actual_outputs[i*N + j]))
        a.append(b)
    print(a)
    print("-"*40)


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


def test_dct_2d():

    samples, fract_bits, output_bits, stage_1_prec, N = 5, 14, 10, 10, 8

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)

    inputs = input_interface()
    outputs = outputs_2d(output_bits, N)

    in_out_data = InputsAndOutputs(samples, N)
    in_out_data.initialize()

    @myhdl.block
    def bench_dct_2d():
        tdut = dct_2d(inputs, outputs, clock, reset, fract_bits, stage_1_prec,
                      output_bits, N)
        tbclock = clock_driver(clock)

        @instance
        def tbstim():
            yield reset_on_start(reset, clock)
            inputs.data_valid.next = True

            for i in range(samples):
                for j in in_out_data.inputs[i]:
                    for k in j:
                        inputs.data_in.next = k
                        yield clock.posedge

        @instance
        def monitor():
            outputs_count = 0
            while(outputs_count != samples):
                yield clock.posedge
                yield delay(1)
                if outputs.data_valid:
                    out_print(in_out_data.outputs[outputs_count],
                              outputs.out_sigs, N)
                    outputs_count += 1
            raise StopSimulation

        return tdut, tbclock, tbstim, monitor

    inst = bench_dct_2d()
    inst.config_sim(trace=True)
    inst.run_sim()


@pytest.mark.skipif(not simsok, reason="missing installed simulator")
def test_dct_2d_conversion():

    samples, fract_bits, output_bits, stage_1_prec, N = 5, 14, 10, 10, 8

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)

    inputs = input_interface()
    outputs = outputs_2d(output_bits, N)

    in_out_data = InputsAndOutputs(samples, N)
    in_out_data.initialize()


    inputs_rom, expected_outputs_rom = in_out_data.get_rom_tables()

    @myhdl.block
    def bench_dct_2d():
        tdut = dct_2d(inputs, outputs, clock, reset, fract_bits, output_bits,
                      stage_1_prec, N)
        tbclk = clock_driver(clock)
        tbrst = rstonstart(reset, clock)

        print_sig = [Signal(intbv(0, min=-2**output_bits, max=2**output_bits))
                     for _ in range(N**2)]
        print_sig_1 = [Signal(intbv(0, min=-2**output_bits, max=2**output_bits))
                     for _ in range(N**2)]

        @instance
        def tbstim():
            yield reset.negedge
            inputs.data_valid.next =True

            for i in range(samples * (N**2)):
                inputs.data_in.next = inputs_rom[i]
                yield clock.posedge

        print_assign = outputs.assignment_2(print_sig_1)

        @instance
        def monitor():
            outputs_count = 0
            while(outputs_count != samples):
                yield clock.posedge
                if outputs.data_valid:
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

            raise StopSimulation

        return tdut, tbclk, tbstim, monitor, tbrst, print_assign

    # verify and convert with GHDL
    verify.simulator = 'ghdl'
    assert bench_dct_2d().verify_convert() == 0
    # verify and convert with iverilog
    verify.simulator = 'iverilog'
    assert bench_dct_2d().verify_convert() == 0


if __name__ == '__main__':
    test_dct_2d()
    test_dct_2d_conversion()
