#!/usr/bin/env python
# coding=utf-8

import myhdl
from myhdl import (StopSimulation, block, Signal, ResetSignal, intbv,
                                      delay, instance, always_comb, always_seq)
from myhdl.conversion import verify
from interfaces import input_interface, output_interface
from dct_1d import dct_1d, dct_1d_transformation
from random import randrange


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

    def __init__(self, samples):
        self.inputs = []
        self.outputs = []
        self.samples = samples

    def initialize(self):
        dct_obj = dct_1d_transformation()
        for i in range(self.samples):
            vector = [randrange(256) for _ in range(8)]
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
    attrs = vars(actual_outputs)
    for i in range(len(expected_outputs)):
        out = "out" + str(i)
        print (" %d " % attrs[out]),
    print("\n" + " -"*40)


def test_dct_1d():

    samples, fract_bits, out_prec = 10, 14, 10

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)

    inputs = input_interface()
    outputs = output_interface(out_prec)

    in_out_data = InputsAndOutputs(samples)
    in_out_data.initialize()

    @myhdl.block
    def bench_dct_1d():
        tdut = dct_1d(inputs, outputs, clock, reset, fract_bits)
        tbclk = clock_driver(clock)

        @instance
        def tbstim():
            yield reset_on_start(reset, clock)
            inputs.data_valid.next = True

            for i in range(samples):
                for j in range(8):
                    inputs.data_in.next = in_out_data.inputs[i][j]
                    yield clock.posedge

        @instance
        def monitor():
            outputs_count = 0
            while(outputs_count != samples):
                yield clock.posedge
                if outputs.data_valid:
                    yield delay(1)
                    out_print(in_out_data.outputs[outputs_count],
                              outputs)
                    outputs_count += 1

            raise StopSimulation

        return tdut, tbclk, tbstim, monitor

    inst = bench_dct_1d()
    inst.config_sim(trace=True)
    inst.run_sim()


def test_dct_1d_conversion():

    samples, fract_bits, out_prec = 10, 14, 10

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)

    inputs = input_interface()
    outputs = output_interface(out_prec)

    in_out_data = InputsAndOutputs(samples)
    in_out_data.initialize()

    inputs_rom, expected_outputs_rom = in_out_data.get_rom_tables()
    print_sig = output_interface(out_prec)

    @myhdl.block
    def bench_dct_1d():
        tdut = dct_1d(inputs, outputs, clock, reset, fract_bits)
        tbclk = clock_driver(clock)
        tbrst = rstonstart(reset, clock)

        @instance
        def tbstim():
            yield reset.negedge
            inputs.data_valid.next =True

            for i in range(samples * 8):
                inputs.data_in.next = inputs_rom[i]
                yield clock.posedge

        @instance
        def monitor():
            outputs_count = 0
            while(outputs_count != samples):
                yield clock.posedge
                if outputs.data_valid:
                    print_sig.out0.next = expected_outputs_rom[outputs_count * 8 + 0]
                    print_sig.out1.next = expected_outputs_rom[outputs_count * 8 + 1]
                    print_sig.out2.next = expected_outputs_rom[outputs_count * 8 + 2]
                    print_sig.out3.next = expected_outputs_rom[outputs_count * 8 + 3]
                    print_sig.out4.next = expected_outputs_rom[outputs_count * 8 + 4]
                    print_sig.out5.next = expected_outputs_rom[outputs_count * 8 + 5]
                    print_sig.out6.next = expected_outputs_rom[outputs_count * 8 + 6]
                    print_sig.out7.next = expected_outputs_rom[outputs_count * 8 + 7]
                    yield delay(1)
                    print("Expected Outputs")
                    print("%d %d %d %d %d %d %d %d" % (print_sig.out0, print_sig.out1,
                                                       print_sig.out2, print_sig.out3,
                                                       print_sig.out4, print_sig.out5,
                                                       print_sig.out5, print_sig.out6))
                    print("Actual Outputs")
                    print("%d %d %d %d %d %d %d %d" %(outputs.out0, outputs.out1,
                                                      outputs.out2, outputs.out3,
                                                      outputs.out4, outputs.out5,
                                                      outputs.out5, outputs.out6))
                    outputs_count += 1

            raise StopSimulation

        return tdut, tbclk, tbstim, monitor, tbrst


    # verify and convert with GHDL
    verify.simulator = 'ghdl'
    assert bench_dct_1d().verify_convert() == 0
    # verify and convert with iverilog
    verify.simulator = 'iverilog'
    assert bench_dct_1d().verify_convert() == 0



