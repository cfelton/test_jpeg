#!/usr/bin/env python
# coding=utf-8

import myhdl
from myhdl import (StopSimulation, block, Signal, ResetSignal, intbv,
                                      delay, instance, always_comb, always_seq)
from myhdl.conversion import verify

from dct_1d import input_interface, output_interface, dct_1d


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

def test_dct_1d():

    fract_bits = 14

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)

    inputs = input_interface()
    outputs = output_interface()

    @myhdl.block
    def bench_dct_1d():
        tdut = dct_1d(inputs, outputs, clock, reset, fract_bits)
        tbclk = clock_driver(clock)

        @instance
        def tbstim():
            yield reset_on_start(reset, clock)
            inputs.data_valid.next =True

            for i in range(40):

                inputs.data_in.next = 1

                yield clock.posedge

            raise StopSimulation

        return tdut, tbclk, tbstim

    inst = bench_dct_1d()
    inst.config_sim(trace=True)
    inst.run_sim()



test_dct_1d()
