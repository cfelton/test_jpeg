#!/usr/bin/env python
# coding=utf-8

import myhdl
from myhdl import (StopSimulation, block, Signal, ResetSignal, intbv,
                                      delay, instance, always_comb, always_seq)
from myhdl.conversion import verify

from dct_1d import input_interface, output_interface, dct_1d

test_block =  [0xa6, 0xa1, 0x9b, 0x9a, 0x9b, 0x9c, 0x97, 0x92,
               0x9f, 0xa3, 0x9d, 0x8e, 0x89, 0x8f, 0x95, 0x94,
               0xa5, 0x97, 0x96, 0xa1, 0x9e, 0x90, 0x90, 0x9e,
               0xa7, 0x9b, 0x91, 0x91, 0x92, 0x91, 0x91, 0x94,
               0xca, 0xda, 0xc8, 0x98, 0x85, 0x98, 0xa2, 0x96,
               0xf0, 0xf7, 0xfb, 0xe8, 0xbd, 0x96, 0x90, 0x9d,
               0xe9, 0xe0, 0xf1, 0xff, 0xef, 0xad, 0x8a, 0x90,
               0xe7, 0xf2, 0xf1, 0xeb, 0xf7, 0xfb, 0xd0, 0x97]

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

            for i in range(68):
                if i<64:
                    inputs.data_in.next = test_block[i]
                yield clock.posedge
                if outputs.data_valid:
                    yield delay(1)
                    out_print()

            raise StopSimulation

        def out_print():
            print("%d %d %d %d %d %d %d %d\n" %(outputs.out0, outputs.out1,
                                                outputs.out2, outputs.out3,
                                                outputs.out4, outputs.out5,
                                                outputs.out6, outputs.out7))




        return tdut, tbclk, tbstim

    inst = bench_dct_1d()
    inst.config_sim(trace=True)
    inst.run_sim()



test_dct_1d()
