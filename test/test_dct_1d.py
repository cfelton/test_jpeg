#!/usr/bin/env python
# coding=utf-8

from random import randrange

import pytest
import myhdl
from myhdl import (StopSimulation, block, Signal, ResetSignal, intbv,
                                      delay, instance, always_comb, always_seq)
from myhdl.conversion import verify
from jpegenc.subblocks.common import output_interface, input_1d_1st_stage
from jpegenc.subblocks.dct import dct_1d
from jpegenc.subblocks.dct.dct_1d import dct_1d_transformation
from jpegenc.testing import sim_available

simsok = sim_available('iverilog') and sim_available('ghdl')


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


class InputsAndOutputs(object):

    def __init__(self, samples, N):
        self.N = N
        self.inputs = []
        self.outputs = []
        self.samples = samples

    def initialize(self):
        dct_obj = dct_1d_transformation(self.N)
        for i in range(self.samples):
            vector = [randrange(-128, 128) for _ in range(self.N)]
            self.inputs.append(vector)
            dct_result = dct_obj.dct_1d_transformation(vector)
            self.outputs.append(dct_result)

    def get_rom_tables(self):
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


def out_print(expected_outputs, actual_outputs):

    print("Expected Outputs ===> "),
    for i in range(len(expected_outputs)):
        print(" %d " % expected_outputs[i]),
    print("")
    print("Actual Outputs   ===> "),
    for i in range(len(actual_outputs)):
        print(" %d " % actual_outputs[i]),
    print("\n" + " -"*40)


def test_dct_1d():

    samples, fract_bits, out_prec, N = 10, 14, 10, 9

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)

    inputs = input_1d_1st_stage()
    outputs = output_interface(out_prec, N)

    in_out_data = InputsAndOutputs(samples, N)
    in_out_data.initialize()

    @myhdl.block
    def bench_dct_1d():
        tdut = dct_1d(inputs, outputs, clock, reset, fract_bits, out_prec, N)
        tbclk = clock_driver(clock)

        @instance
        def tbstim():
            yield reset_on_start(reset, clock)
            inputs.data_valid.next = True

            for i in range(samples):
                for j in range(N):
                    inputs.data_in.next = in_out_data.inputs[i][j]
                    yield clock.posedge

        @instance
        def monitor():
            outputs_count = 0
            while(outputs_count != samples):
                yield clock.posedge
                yield delay(1)
                if outputs.data_valid:
                    # convert flat signal to array of signals
                    out_print(in_out_data.outputs[outputs_count],
                              outputs.out_sigs)
                    outputs_count += 1

            raise StopSimulation

        return tdut, tbclk, tbstim, monitor

    inst = bench_dct_1d()
    inst.config_sim(trace=True)
    inst.run_sim()


@pytest.mark.skipif(not simsok, reason="missing installed simulator")
def test_dct_1d_conversion():

    samples, fract_bits, out_prec, N = 10, 14, 10, 8

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)

    inputs = input_1d_1st_stage()
    outputs = output_interface(out_prec, N)

    in_out_data = InputsAndOutputs(samples, N)
    in_out_data.initialize()

    inputs_rom, expected_outputs_rom = in_out_data.get_rom_tables()

    @myhdl.block
    def bench_dct_1d():
        print_sig = [Signal(intbv(0, min=-2**out_prec, max=2**out_prec))
                 for _ in range(N)]
        print_sig_1 = [Signal(intbv(0, min=-2**out_prec, max=2**out_prec))
                 for _ in range(N)]

        tdut = dct_1d(inputs, outputs, clock, reset, fract_bits, out_prec, N)
        tbclk = clock_driver(clock)
        tbrst = rstonstart(reset, clock)

        @instance
        def tbstim():
            yield reset.negedge
            inputs.data_valid.next =True

            for i in range(samples * N):
                inputs.data_in.next = inputs_rom[i]
                yield clock.posedge

        print_assign = outputs.assignment_2(print_sig_1)

        @instance
        def monitor():
            outputs_count = 0
            while(outputs_count != samples):
                yield clock.posedge
                yield delay(1)
                if outputs.data_valid:
                    for i in range(N):
                        print_sig[i].next = expected_outputs_rom[outputs_count * 8 + i]
                    yield delay(1)
                    print("Expected Outputs")
                    for i in range(N):
                        print("%d" % print_sig[i])
                    print("Actual Outputs")
                    for i in range(N):
                        print("%d" % print_sig_1[i])
                    print("------------------------")
                    outputs_count += 1

            raise StopSimulation

        return tdut, tbclk, tbstim, monitor, tbrst, print_assign

    # verify and convert with GHDL
    verify.simulator = 'ghdl'
    assert bench_dct_1d().verify_convert() == 0
    # verify and convert with iverilog
    verify.simulator = 'iverilog'
    assert bench_dct_1d().verify_convert() == 0


if __name__ == '__main__':
    test_dct_1d()
    test_dct_1d_conversion()
