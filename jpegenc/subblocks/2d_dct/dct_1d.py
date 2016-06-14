#!/usr/bin/env python
# coding=utf-8

import numpy as np
from math import sqrt, pi, cos, sin
import myhdl
from myhdl import Signal, ResetSignal, intbv, always_comb, always_seq
from myhdl.conversion import analyze
from interfaces import input_interface, output_interface


def dct_int_coeffs(precision_factor):
    # create b,c,..,g with cos(pk/16) for less code, and a=sqrt(2)/2 or
    # a=cos(p/4)
    const = sqrt(2.0/8)
    a = const * cos(pi/4)
    b = const * cos(pi/16)
    c = const * cos(pi/8)
    d = const * cos(3*pi/16)
    e = const * cos(5*pi/16)
    f = const * cos(3*pi/8)
    g = const * cos(7*pi/16)

    coeff_matrix = [[a, a, a, a, a, a, a, a],
                    [b, d, e, g, -g, -e, -d, -b],
                    [c, f, -f, -c, -c, -f, f, c],
                    [d, -g, -b, -e, e, b, g, -d],
                    [a, -a, -a, a, a, -a, -a, a],
                    [e, -b, g, d, -d, -g, b, -e],
                    [f, -c, c, -f, -f, c, -c, f],
                    [g, -e, d, -b, b, -d, e, -g]]
    coeff_matrix = np.asarray(coeff_matrix)
    coeff_matrix = coeff_matrix * (2**precision_factor)
    coeff_matrix = np.rint(coeff_matrix)
    coeff_matrix = coeff_matrix.astype(int)
    return coeff_matrix


def tuple_construct(matrix):
    a = []
    for i in matrix:
        for j in i:
            a.append(j)
    return tuple(a)

def rounding(in_sig, out_rounded, a, b, c):
     if in_sig[c - 1] == 1:
         out_rounded.next = in_sig[a:b].signed() + 1
     else:
         out_rounded.next = in_sig[a:b].signed()


@myhdl.block
def dct_1d(input_interface, output_interface, clock, reset, num_fractional_bits=14):

    fract_bits = num_fractional_bits
    nbits = input_interface.nbits
    output_fract = output_interface.out_precision
    increase_range = 1

    mult_max_range = 2**(nbits + fract_bits + 1 + increase_range)
    coeff_range = 2**fract_bits
    input_range = 2**(nbits + increase_range)

    a = fract_bits + output_fract + 1
    b = fract_bits
    c = fract_bits -1

    mult_reg = [Signal(intbv(0, min=-mult_max_range, max=mult_max_range))
                for _ in range(8)]
    adder_reg = [Signal(intbv(0, min=-mult_max_range, max=mult_max_range))
                 for _ in range(8)]
    coeffs = [Signal(intbv(0, min=-coeff_range, max=coeff_range))
              for _ in range(8)]
    mux_flush = [Signal(intbv(0, min=-mult_max_range, max=mult_max_range))
                 for _ in range(8)]

    inputs_counter = Signal(intbv(0, min=0, max=8))
    cycles_counter = Signal(intbv(0, min=0, max=12))
    first_row_passed = Signal(bool(0))

    data_in_s = Signal(intbv(0, min=-input_range, max=input_range))

    # coefficient rom
    coeff_rom = tuple_construct(dct_int_coeffs(fract_bits))

    @always_seq(clock.posedge, reset=reset)
    def input_to_signed():
        if input_interface.data_valid:
            data_in_s.next = input_interface.data_in

    @always_seq(clock.posedge, reset=reset)
    def coeff_assign():
        if input_interface.data_valid:
            for i in range(8):
                coeffs[i].next = coeff_rom[i * 8 + inputs_counter]

    @always_seq(clock.posedge, reset=reset)
    def mul_add():

        if input_interface.data_valid:
                mult_reg[0].next = data_in_s * coeffs[0]
                mult_reg[1].next = data_in_s * coeffs[1]
                mult_reg[2].next = data_in_s * coeffs[2]
                mult_reg[3].next = data_in_s * coeffs[3]
                mult_reg[4].next = data_in_s * coeffs[4]
                mult_reg[5].next = data_in_s * coeffs[5]
                mult_reg[6].next = data_in_s * coeffs[6]
                mult_reg[7].next = data_in_s * coeffs[7]

                adder_reg[0].next = mux_flush[0] + mult_reg[0]
                adder_reg[1].next = mux_flush[1] + mult_reg[1]
                adder_reg[2].next = mux_flush[2] + mult_reg[2]
                adder_reg[3].next = mux_flush[3] + mult_reg[3]
                adder_reg[4].next = mux_flush[4] + mult_reg[4]
                adder_reg[5].next = mux_flush[5] + mult_reg[5]
                adder_reg[6].next = mux_flush[6] + mult_reg[6]
                adder_reg[7].next = mux_flush[7] + mult_reg[7]

    @always_comb
    def mux_after_adder_reg():
        if cycles_counter == 10 or (cycles_counter == 7  and
                                    first_row_passed):
            for i in range(8):
                mux_flush[i].next = 0
        else:
            for i in range(8):
                mux_flush[i].next = adder_reg[i]

    @always_seq(clock.posedge, reset=reset)
    def counters():

        if input_interface.data_valid:
            if cycles_counter == 10 or (first_row_passed and
                                        cycles_counter == 7):
                cycles_counter.next = 0
                first_row_passed.next = True
            else:
                cycles_counter.next = cycles_counter + 1

            if inputs_counter == 7:
                inputs_counter.next = 0
            else:
                inputs_counter.next = inputs_counter +1


    @always_seq(clock.posedge, reset=reset)
    def outputs():
        if cycles_counter == 10 or (first_row_passed and
                                    cycles_counter == 7):
            if adder_reg[0][c] == 1:
                output_interface.out0.next = adder_reg[0][a:b].signed() + 1
            else:
                output_interface.out0.next = adder_reg[0][a:b].signed()
            if adder_reg[1][c] == 1:
                output_interface.out1.next = adder_reg[1][a:b].signed() + 1
            else:
                output_interface.out1.next = adder_reg[1][a:b].signed()
            if adder_reg[2][c] == 1:
                output_interface.out2.next = adder_reg[2][a:b].signed() + 1
            else:
                output_interface.out2.next = adder_reg[2][a:b].signed()
            if adder_reg[3][c] == 1:
                output_interface.out3.next = adder_reg[3][a:b].signed() + 1
            else:
                output_interface.out3.next = adder_reg[3][a:b].signed()
            if adder_reg[4][c] == 1:
                output_interface.out4.next = adder_reg[4][a:b].signed() + 1
            else:
                output_interface.out4.next = adder_reg[4][a:b].signed()
            if adder_reg[5][c] == 1:
                output_interface.out5.next = adder_reg[5][a:b].signed() + 1
            else:
                output_interface.out5.next = adder_reg[5][a:b].signed()
            if adder_reg[6][c] == 1:
                output_interface.out6.next = adder_reg[6][a:b].signed() + 1
            else:
                output_interface.out6.next = adder_reg[6][a:b].signed()
            if adder_reg[7][c] == 1:
                output_interface.out7.next = adder_reg[7][a:b].signed() + 1
            else:
                output_interface.out7.next = adder_reg[7][a:b].signed()
            output_interface.data_valid.next = True
        else:
            output_interface.data_valid.next = False

    return outputs, counters, mul_add, input_to_signed, coeff_assign, mux_after_adder_reg


def convert():

    inputs = input_interface()
    outputs = output_interface()

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)

    analyze.simulator = 'ghdl'
    assert dct_1d(inputs, outputs, clock, reset, num_fractional_bits=14).analyze_convert() == 0

if __name__ == '__main__':
    convert()

















