import numpy as np
from math import sqrt, pi, cos
import myhdl
from myhdl import Signal, ResetSignal, intbv, always_comb, always_seq, instance, block
from myhdl.conversion import analyze

from jpegenc.subblocks.common import (input_1d_1st_stage, input_interface,
                                      output_interface, outputs_2d,
                                      input_1d_2nd_stage)
from jpegenc.subblocks.dct_1d import dct_1d


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
def dct_2d(inputs, outputs, clock, reset, num_fractional_bits=14, stage_1_prec=10, out_prec=10, N=8):
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

    """the blocks below are used for the list of signal elaboration"""

    @block
    def assign(data_in, data_valid, data_in_temp, data_valid_temp):
        """used to assign the signals data_in and data_valid of the first 1d-dct module
        to the second stage 1d-dct modules"""
        @always_comb
        def assign():
            data_in.next = data_in_temp
            data_valid.next = data_valid_temp

        return assign

    @block
    def assign_2(outputs, outputs_2nd_stage, io):
        """used to assigns the output signals of the 2nd stage 1d-dct modules
        to the outputs signals of the top level 2d-dct"""
        @block
        def assign(y, x):
            @always_comb
            def assign():
                y.next = x
            return assign

        g = [None for _ in range(N)]
        for i in range(N):
                g[i] = assign(outputs.out_sigs[i*N + io], outputs_2nd_stage.out_sigs[i])
        return g

    @block
    def assign_3(y, x):
        """used to make a simple assignment of the data_valid signals of the 2nd stage
        1d-dct modules to a temp signal which used in the 2d-dct module"""
        @always_comb
        def assign():
            y.next = x

        return assign


    stage_2_insts = []
    for i in range(N):
        stage_2_insts += [dct_1d(inputs_2nd_stage[i], outputs_2nd_stage[i], clock,
                                reset, num_fractional_bits, stage_1_prec, N)]

        stage_2_insts += [assign(inputs_2nd_stage[i].data_in, inputs_2nd_stage[i].data_valid,
                                 first_1d_output.out_sigs[i], first_1d_output.data_valid)]

        stage_2_insts += [assign_2(outputs, outputs_2nd_stage[i], i)]

    stage_2_insts += [assign_3(outputs_data_valid, outputs_2nd_stage[0].data_valid)]


    @always_seq(clock.posedge, reset=reset)
    def input_subtract():
        """Align to zero each input"""
        if inputs.data_valid:
            data_in_signed.next = inputs.data_in
            input_1d_stage_1.data_in.next = data_in_signed - 128
            data_valid_reg.next = inputs.data_valid
            input_1d_stage_1.data_valid.next = data_valid_reg


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


    return (stage_2_insts, input_subtract, second_stage_output,
             counter_update, data_valid_2d, first_1d)

"""
def convert():
    out_prec = 10
    stage_1_prec = 10
    fract_bits = 14
    N = 8

    inputs = input_interface()
    outputs = outputs_2d(out_prec, N)

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)

    analyze.simulator = 'ghdl'
    assert dct_2d(inputs, outputs, clock, reset,
                  fract_bits, stage_1_prec, out_prec, N).analyze_convert() == 0

if __name__ == '__main__':
    convert()
"""
