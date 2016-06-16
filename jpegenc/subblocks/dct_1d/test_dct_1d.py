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

def out_print(expected_outputs, actual_outputs):

    print("Expected Outputs ===> "),
    for i in range(len(expected_outputs)):
        print(" %d "% expected_outputs[i]),
    print("")
    print("Actual Outputs   ===> "),
    attrs = vars(actual_outputs)
    for i in range(len(expected_outputs)):
        out = "out" + str(i)
        print (" %d "% attrs[out]),
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
            inputs.data_valid.next =True

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



test_dct_1d()
