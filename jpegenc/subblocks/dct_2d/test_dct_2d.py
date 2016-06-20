#!/usr/bin/env python
# coding=utf-8
import myhdl
from myhdl import (StopSimulation, block, Signal, ResetSignal, intbv,
                   delay, instance, always_comb, always_seq)
from myhdl.conversion import verify

from interfaces import (input_interface, output_interface, input_1d_2nd_stage,
                        outputs_2d)
from dct_2d import dct_2d, dct_2d_transformation
import numpy as np


class InputsAndOutputs(object):

    def __init__(self, samples):
        self.inputs = []
        self.outputs = []
        self.samples = samples

    def initialize(self):
        dct_obj = dct_2d_transformation()
        for i in range(self.samples):
            random_matrix = self.random_matrix_8_8()
            self.inputs.append(random_matrix)
            dct_result = dct_obj.dct_2d_transformation(random_matrix)
            self.outputs.append(dct_result)

    def random_matrix_8_8(self):
        random_matrix = np.random.rand(8, 8)
        random_matrix = np.rint(255*random_matrix)
        random_matrix = random_matrix.astype(int)
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


def out_print(expected_outputs, actual_outputs):

    print("Expected Outputs ===> ")
    print expected_outputs
    print("Actual Outputs   ===> ")
    a = []
    attrs = vars(actual_outputs)
    for i in range(8):
        b = []
        for j in range(8):
            y = "y" + str(i) + str(j)
            b.append(int(attrs[y]))
        a.append(b)
    print(np.array(a))
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

    samples, fract_bits, output_bits = 5, 14, 10

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)

    inputs = input_interface()
    outputs = outputs_2d(output_bits)

    in_out_data = InputsAndOutputs(samples)
    in_out_data.initialize()

    @myhdl.block
    def bench_dct_2d():
        tdut = dct_2d(inputs, outputs, clock, reset, fract_bits)
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
                if outputs.data_valid:
                    yield delay(1)
                    out_print(in_out_data.outputs[outputs_count],
                              outputs)
                    outputs_count += 1
            raise StopSimulation

        return tdut, tbclock, tbstim, monitor

    inst = bench_dct_2d()
    inst.config_sim(trace=True)
    inst.run_sim()

def test_dct_2d_conversion():

    samples, fract_bits, output_bits = 5, 14, 10

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)

    inputs = input_interface()
    outputs = outputs_2d(output_bits)

    in_out_data = InputsAndOutputs(samples)
    in_out_data.initialize()

    inputs_rom, expected_outputs_rom = in_out_data.get_rom_tables()
    @myhdl.block
    def bench_dct_2d():
        tdut = dct_2d(inputs, outputs, clock, reset, fract_bits)
        tbclk = clock_driver(clock)
        tbrst = rstonstart(reset, clock)

        print_sig = [Signal(intbv(0, min=-2**output_bits, max=2**output_bits))
                 for _ in range(64)]

        @instance
        def tbstim():
            yield reset.negedge
            inputs.data_valid.next =True

            for i in range(samples * 64):
                inputs.data_in.next = inputs_rom[i]
                yield clock.posedge

        @instance
        def monitor():
            outputs_count = 0
            while(outputs_count != samples):
                yield clock.posedge
                if outputs.data_valid:
                    for i in range(64):
                        print_sig[i].next = expected_outputs_rom[outputs_count * 64 + i]

                    yield delay(1)
                    print("Expected Outputs")
                    for i in range(8):
                        print("%d %d %d %d %d %d %d %d" % (print_sig[i * 8 + 0], print_sig[i * 8 + 1],
                                                           print_sig[i * 8 + 2], print_sig[i * 8 + 3],
                                                           print_sig[i * 8 + 4], print_sig[i * 8 + 5],
                                                           print_sig[i * 8 + 6], print_sig[i * 8 + 7]))
                    print("Actual Outputs")
                    print("%d %d %d %d %d %d %d %d" % (outputs.y00, outputs.y01,
                                                       outputs.y02, outputs.y03,
                                                       outputs.y04, outputs.y05,
                                                       outputs.y06, outputs.y07))
                    print("%d %d %d %d %d %d %d %d" % (outputs.y10, outputs.y11,
                                                       outputs.y12, outputs.y13,
                                                       outputs.y14, outputs.y15,
                                                       outputs.y16, outputs.y17))
                    print("%d %d %d %d %d %d %d %d" % (outputs.y20, outputs.y21,
                                                       outputs.y22, outputs.y23,
                                                       outputs.y24, outputs.y25,
                                                       outputs.y26, outputs.y27))
                    print("%d %d %d %d %d %d %d %d" % (outputs.y30, outputs.y31,
                                                       outputs.y32, outputs.y33,
                                                       outputs.y34, outputs.y35,
                                                       outputs.y36, outputs.y37))
                    print("%d %d %d %d %d %d %d %d" % (outputs.y40, outputs.y41,
                                                       outputs.y42, outputs.y43,
                                                       outputs.y44, outputs.y45,
                                                       outputs.y46, outputs.y47))
                    print("%d %d %d %d %d %d %d %d" % (outputs.y50, outputs.y51,
                                                       outputs.y52, outputs.y53,
                                                       outputs.y54, outputs.y55,
                                                       outputs.y56, outputs.y57))
                    print("%d %d %d %d %d %d %d %d" % (outputs.y60, outputs.y61,
                                                       outputs.y62, outputs.y63,
                                                       outputs.y64, outputs.y65,
                                                       outputs.y66, outputs.y67))
                    print("%d %d %d %d %d %d %d %d" % (outputs.y70, outputs.y71,
                                                       outputs.y72, outputs.y73,
                                                       outputs.y74, outputs.y75,
                                                       outputs.y76, outputs.y77))


                    print("------------------------------")
                    outputs_count += 1

            raise StopSimulation

        return tdut, tbclk, tbstim, monitor, tbrst


    # verify and convert with GHDL
    verify.simulator = 'ghdl'
    assert bench_dct_2d().verify_convert() == 0
    # verify and convert with iverilog
    verify.simulator = 'iverilog'
    assert bench_dct_2d().verify_convert() == 0




#test_dct_2d()
test_dct_2d_conversion()
