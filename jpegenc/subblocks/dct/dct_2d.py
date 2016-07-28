import numpy as np
from math import sqrt, pi, cos
import myhdl
from myhdl import Signal, intbv, always_comb, always_seq, block

from jpegenc.subblocks.common import (input_1d_1st_stage, input_interface,
                                      output_interface, outputs_2d, assign,
                                      input_1d_2nd_stage, assign_array)
from .dct_1d import dct_1d


class dct_2d_transformation(object):

    """2D-DCT Transformation Class

    It is used as a software reference for the 2D-DCT
    Transformation
    """

    def __init__(self, N):
        """Initialize the DCT coefficient matrix"""
        self.coeff_matrix = self.build_matrix(N)

    def build_matrix(self, N):
        const = sqrt(2.0 / 8)
        a0 = sqrt(1.0 / 2.0)
        ak = 1
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

    def dct_2d_transformation(self, block):
        """2D-DCT software reference"""
        coeff_matrix = np.asarray(self.coeff_matrix)
        block = np.asarray(block)
        block = block - 128
        # first 1d-dct with rows
        dct_result = np.dot(coeff_matrix, np.transpose(block))
        # second 1d-dct with columns
        dct_result = np.rint(dct_result)
        dct_result = np.dot(coeff_matrix, np.transpose(dct_result))
        dct_result = np.rint(dct_result).astype(int)
        dct_result = dct_result.tolist()
        return dct_result


@myhdl.block
def dct_2d(inputs, outputs, clock, reset, num_fractional_bits=14,
           stage_1_prec=10, out_prec=10, N=8):
    """2D-DCT Module

    This module performs the 2D-DCT Transformation.
    It takes serially the inputs of a NxN block
    and outputs parallely the transformed block in
    64 signals.

    Inputs:
        data_in, data_valid
    Outputs:
        NxN signals in the list out_sigs, data_valid
    """
    first_1d_output = output_interface(stage_1_prec, N)
    input_1d_stage_1 = input_1d_1st_stage()

    first_1d = dct_1d(input_1d_stage_1, first_1d_output, clock,
                      reset, num_fractional_bits, stage_1_prec, N)

    data_in_signed = Signal(intbv(0, min=-input_1d_stage_1.in_range,
                                  max=input_1d_stage_1.in_range))
    data_valid_reg = Signal(bool(0))
    data_valid_reg2 = Signal(bool(0))

    counter = Signal(intbv(0, min=0, max=N))
    outputs_data_valid = Signal(bool(0))

    # list of interfaces for the 2nd stage 1d-dct modules
    inputs_2nd_stage = []
    outputs_2nd_stage = []
    for i in range(N):
        inputs_2nd_stage += [input_1d_2nd_stage(first_1d_output.out_precision)]
        outputs_2nd_stage += [output_interface(out_prec, N)]


    stage_2_insts = []
    for i in range(N):
        stage_2_insts += [dct_1d(inputs_2nd_stage[i], outputs_2nd_stage[i], clock,
                                reset, num_fractional_bits, stage_1_prec, N)]

        stage_2_insts += [assign(inputs_2nd_stage[i].data_in, first_1d_output.out_sigs[i])]
        stage_2_insts += [assign(inputs_2nd_stage[i].data_valid, first_1d_output.data_valid)]

        for j in range(N):
            stage_2_insts += [assign(outputs.out_sigs[j * N + i], outputs_2nd_stage[i].out_sigs[j])]

    stage_2_insts += [assign(outputs_data_valid, outputs_2nd_stage[0].data_valid)]

    @always_seq(clock.posedge, reset=reset)
    def input_subtract():
        """Align to zero each input"""
        if inputs.data_valid:
            input_1d_stage_1.data_in.next = data_in_signed - 128
            input_1d_stage_1.data_valid.next = data_valid_reg

    @always_seq(clock.posedge, reset=reset)
    def reg_input():
        if inputs.data_valid:
            data_in_signed.next = inputs.data_in
            data_valid_reg.next = inputs.data_valid

    @always_comb
    def second_stage_output():
        outputs.data_valid.next = data_valid_reg2

    @always_seq(clock.posedge, reset=reset)
    def counter_update():
        """Counter update"""
        if outputs_data_valid:
            if counter == N - 1:
                counter.next = 0
            else:
                counter.next = counter + 1

    @always_comb
    def data_valid_2d():
        """Data valid signal assignment when the outputs are valid"""
        if outputs_data_valid and counter == 0:
            data_valid_reg2.next = True
        else:
            data_valid_reg2.next = False

    return (reg_input, stage_2_insts, input_subtract, second_stage_output,
            counter_update, data_valid_2d, first_1d)

