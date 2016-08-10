#!/usr/bin/env python
# coding=utf-8

import numpy as np
from math import sqrt, pi, cos
import myhdl
from myhdl import Signal, intbv, always_comb, always_seq
from jpegenc.subblocks.common import assign_array

class dct_1d_transformation(object):

    """1D-DCT Transformation Class

    It is used to derive the integer coefficient matrix
    and as a software reference for the 1D-DCT Transformation.
    """

    def __init__(self, N):
        """Initialize the DCT coefficient matrix"""
        self.coeff_matrix = self.build_matrix(N)

    def build_matrix(self, N):
        """Create the coefficient NxN matrix"""
        const = sqrt(2.0 / 8)
        a0 = sqrt(1.0 / 2.0)
        ak  = 1
        coeff_matrix = []
        for i in range(N):
            row = []
            for j in range(N):
                if i == 0:
                    coeff = const * a0 * cos(((2 * j + 1) * pi * i) / (2 * N))
                else:
                    coeff = const * ak * cos(((2 * j + 1) * pi * i) / (2 * N))
                row.append(coeff)
            coeff_matrix.append(row)
        return coeff_matrix

    def dct_1d_transformation(self, vector):
        """1D-DCT software reference"""
        vector_t = np.transpose(vector)
        dct_result = np.dot(self.coeff_matrix, vector_t)
        dct_result = np.rint(dct_result)
        dct_result = dct_result.astype(int)
        dct_result = dct_result.tolist()
        return dct_result

    def dct_int_coeffs(self, precision_factor):
        """Transform coeff matrix to integer coefficients"""
        coeff_matrix = np.asarray(self.coeff_matrix)
        coeff_matrix = coeff_matrix * (2**precision_factor)
        coeff_matrix = np.rint(coeff_matrix)
        coeff_matrix = coeff_matrix.astype(int)
        coeff_matrix = coeff_matrix.tolist()
        return coeff_matrix


def tuple_construct(matrix):
    """Construct a tuple from list to use it as a rom"""
    a = []
    for i in matrix:
        for j in i:
            a.append(j)
    return tuple(a)


@myhdl.block
def dct_1d(input_interface, output_interface, clock, reset,
           num_fractional_bits=14, out_precision=10, N=8):
    """1D-DCT Module

    This module performs the 1D-DCT Transformation.
    It takes serially  N inputs and outputs parallely
    the vector of N signals. The parameter num_fractional_bits
    defines how many bits will be used for the fixed point representation
    of the dct coefficient. The out_precision parameter defines how many bits
    will be used for the fixed point representation of the outputs signals.
    This module is the building block for the 2d-dct module.
    The input interface is the input_1d_1st_stage and the output interface is the
    output_interface.

    Inputs:
        data_in, data_valid, clock, reset

    Outputs:
        List of N signals: out_sigs, data_valid

    Parameters:
        num_fractional_bits, out_precision, N

    """
    fract_bits = num_fractional_bits
    nbits = input_interface.nbits
    output_fract = out_precision
    increase_range = 1

    mult_max_range = 2**(nbits + fract_bits + 1 + increase_range)
    coeff_range = 2**fract_bits

    a = fract_bits + output_fract + 1
    b = fract_bits
    c = fract_bits - 1

    mult_reg = [Signal(intbv(0, min=-mult_max_range, max=mult_max_range))
                for _ in range(N)]
    adder_reg = [Signal(intbv(0, min=-mult_max_range, max=mult_max_range))
                 for _ in range(N)]
    coeffs = [Signal(intbv(0, min=-coeff_range, max=coeff_range))
              for _ in range(N)]
    mux_flush = [Signal(intbv(0, min=-mult_max_range, max=mult_max_range))
                 for _ in range(N)]

    inputs_counter = Signal(intbv(0, min=0, max=N))
    cycles_counter = Signal(intbv(0, min=0, max=N+4))
    first_row_passed = Signal(bool(0))

    data_in_reg = Signal(intbv(0, min=-2**nbits,
                               max=2**nbits))
    # coefficient rom
    dct_1d_obj = dct_1d_transformation(N)
    coeff_matrix = dct_1d_obj.dct_int_coeffs(fract_bits)
    coeff_rom = tuple_construct(coeff_matrix)

    output_sigs = [Signal(intbv(0, min=-2**output_fract, max=2**output_fract))
                   for _ in range(N)]

    @always_seq(clock.posedge, reset=reset)
    def input_reg():
        """input register"""
        if input_interface.data_valid:
            data_in_reg.next = input_interface.data_in

    @always_seq(clock.posedge, reset=reset)
    def coeff_assign():
        """coefficient assignment from rom"""
        if input_interface.data_valid:
            for i in range(N):
                coeffs[i].next = coeff_rom[i * N + int(inputs_counter)]

    @always_seq(clock.posedge, reset=reset)
    def mul_add():
        """multiplication and addition"""
        if input_interface.data_valid:
            for i in range(N):
                mult_reg[i].next = data_in_reg * coeffs[i]
                adder_reg[i].next = mux_flush[i] + mult_reg[i]

    @always_comb
    def mux_after_adder_reg():
        """after 8 inputs flush one of the inputs of the adder"""
        if cycles_counter == (N + 2) or (cycles_counter == (N - 1)
                                         and first_row_passed):
            for i in range(N):
                mux_flush[i].next = 0
        else:
            for i in range(N):
                mux_flush[i].next = adder_reg[i]

    @always_seq(clock.posedge, reset=reset)
    def counters():
        """inputs and cycles counter"""
        if input_interface.data_valid:
            if cycles_counter == (N + 2) or (cycles_counter == (N - 1)
                                             and first_row_passed):
                cycles_counter.next = 0
                first_row_passed.next = True
            else:
                cycles_counter.next = cycles_counter + 1

            if inputs_counter == N - 1:
                inputs_counter.next = 0
            else:
                inputs_counter.next = inputs_counter + 1

    @always_seq(clock.posedge, reset=reset)
    def outputs():
        """rounding"""
        for i in range(N):
                output_sigs[i].next = adder_reg[i][a:b].signed() + adder_reg[i][c]

        if cycles_counter == N + 2 or (first_row_passed and
                                       cycles_counter == N - 1):
                output_interface.data_valid.next = True
        else:
            output_interface.data_valid.next = False

    # avoid verilog indexing error
    outputs_assignment = assign_array(output_interface.out_sigs,output_sigs)

    return (input_reg, outputs, counters, mul_add, coeff_assign,
            mux_after_adder_reg, outputs_assignment)
