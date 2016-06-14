#!/usr/bin/env python
# coding=utf-8

import numpy as np
from math import sqrt, pi, cos, sin
import myhdl
from myhdl import Signal, ResetSignal, intbv, always_comb, always_seq, instance
from myhdl.conversion import analyze

from interfaces import input_interface, output_interface,outputs_2d, input_1d_2nd_stage
from dct_1d import dct_1d

def random_matrix_8_8():

    random_matrix = np.random.rand(8, 8)
    random_matrix = np.rint(255*random_matrix)
    random_matrix = random_matrix.astype(int)

    return random_matrix


def two_d_dct_numpy(block):

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
    block = np.asarray(block)

    print block

    # first 1d-dct with rows
    dct_result = np.dot(coeff_matrix, np.transpose(block))
    # second 1d-dct with columns
    print np.rint(dct_result)
    dct_result = np.rint(dct_result)
    dct_result = np.dot(coeff_matrix, np.transpose(dct_result))
    dct_result = np.rint(dct_result).astype(int)
    dct_result[0][0] -= 1024
    print dct_result

# block = random_matrix_8_8()

block = [[0xa6, 0xa1, 0x9b, 0x9a, 0x9b, 0x9c, 0x97, 0x92],
         [0x9f, 0xa3, 0x9d, 0x8e, 0x89, 0x8f, 0x95, 0x94],
         [0xa5, 0x97, 0x96, 0xa1, 0x9e, 0x90, 0x90, 0x9e],
         [0xa7, 0x9b, 0x91, 0x91, 0x92, 0x91, 0x91, 0x94],
         [0xca, 0xda, 0xc8, 0x98, 0x85, 0x98, 0xa2, 0x96],
         [0xf0, 0xf7, 0xfb, 0xe8, 0xbd, 0x96, 0x90, 0x9d],
         [0xe9, 0xe0, 0xf1, 0xff, 0xef, 0xad, 0x8a, 0x90],
         [0xe7, 0xf2, 0xf1, 0xeb, 0xf7, 0xfb, 0xd0, 0x97]]

two_d_dct_numpy(block)

@myhdl.block
def dct_2d(inputs, outputs, clock, reset, num_fractional_bits=14):

    first_1d_output = output_interface()

    first_1d = dct_1d(inputs, first_1d_output, clock,
                      reset, num_fractional_bits)

    inputs_2nd_stage_0 = input_1d_2nd_stage(first_1d_output.out_precision)
    inputs_2nd_stage_1 = input_1d_2nd_stage(first_1d_output.out_precision)
    inputs_2nd_stage_2 = input_1d_2nd_stage(first_1d_output.out_precision)
    inputs_2nd_stage_3 = input_1d_2nd_stage(first_1d_output.out_precision)
    inputs_2nd_stage_4 = input_1d_2nd_stage(first_1d_output.out_precision)
    inputs_2nd_stage_5 = input_1d_2nd_stage(first_1d_output.out_precision)
    inputs_2nd_stage_6 = input_1d_2nd_stage(first_1d_output.out_precision)
    inputs_2nd_stage_7 = input_1d_2nd_stage(first_1d_output.out_precision)

    out_prec = 10

    outputs_2nd_stage_0 = output_interface(out_prec)
    outputs_2nd_stage_1 = output_interface(out_prec)
    outputs_2nd_stage_2 = output_interface(out_prec)
    outputs_2nd_stage_3 = output_interface(out_prec)
    outputs_2nd_stage_4 = output_interface(out_prec)
    outputs_2nd_stage_5 = output_interface(out_prec)
    outputs_2nd_stage_6 = output_interface(out_prec)
    outputs_2nd_stage_7 = output_interface(out_prec)


    stage_2_inst_0 = dct_1d(inputs_2nd_stage_0, outputs_2nd_stage_0, clock, reset,
                            num_fractional_bits)
    stage_2_inst_1 = dct_1d(inputs_2nd_stage_1, outputs_2nd_stage_1, clock, reset,
                            num_fractional_bits)
    stage_2_inst_2 = dct_1d(inputs_2nd_stage_2, outputs_2nd_stage_2, clock, reset,
                                num_fractional_bits)
    stage_2_inst_3 = dct_1d(inputs_2nd_stage_3, outputs_2nd_stage_3, clock, reset,
                                num_fractional_bits)
    stage_2_inst_4 = dct_1d(inputs_2nd_stage_4, outputs_2nd_stage_4, clock, reset,
                                num_fractional_bits)
    stage_2_inst_5 = dct_1d(inputs_2nd_stage_5, outputs_2nd_stage_5, clock, reset,
                                num_fractional_bits)
    stage_2_inst_6 = dct_1d(inputs_2nd_stage_6, outputs_2nd_stage_6, clock, reset,
                                num_fractional_bits)
    stage_2_inst_7 = dct_1d(inputs_2nd_stage_7, outputs_2nd_stage_7, clock, reset,
                                num_fractional_bits)

    @always_seq(clock.posedge, reset=reset)
    def first_stage_to_second():
        inputs_2nd_stage_0.data_in.next = first_1d_output.out0
        inputs_2nd_stage_0.data_valid.next = first_1d_output.data_valid
        inputs_2nd_stage_1.data_in.next = first_1d_output.out1
        inputs_2nd_stage_1.data_valid.next = first_1d_output.data_valid
        inputs_2nd_stage_2.data_in.next = first_1d_output.out2
        inputs_2nd_stage_2.data_valid.next = first_1d_output.data_valid
        inputs_2nd_stage_3.data_in.next = first_1d_output.out3
        inputs_2nd_stage_3.data_valid.next = first_1d_output.data_valid
        inputs_2nd_stage_4.data_in.next = first_1d_output.out4
        inputs_2nd_stage_4.data_valid.next = first_1d_output.data_valid
        inputs_2nd_stage_5.data_in.next = first_1d_output.out5
        inputs_2nd_stage_5.data_valid.next = first_1d_output.data_valid
        inputs_2nd_stage_6.data_in.next = first_1d_output.out6
        inputs_2nd_stage_6.data_valid.next = first_1d_output.data_valid
        inputs_2nd_stage_7.data_in.next = first_1d_output.out7
        inputs_2nd_stage_7.data_valid.next = first_1d_output.data_valid

    @always_seq(clock.posedge, reset=reset)
    def second_stage_output():
        # subtract y00 with 1024 but check the precisions!!!
        outputs.y00.next = outputs_2nd_stage_0.out0
        outputs.y01.next = outputs_2nd_stage_0.out1
        outputs.y02.next = outputs_2nd_stage_0.out2
        outputs.y03.next = outputs_2nd_stage_0.out3
        outputs.y04.next = outputs_2nd_stage_0.out4
        outputs.y05.next = outputs_2nd_stage_0.out5
        outputs.y06.next = outputs_2nd_stage_0.out6
        outputs.y07.next = outputs_2nd_stage_0.out7
        outputs.y10.next = outputs_2nd_stage_1.out0
        outputs.y11.next = outputs_2nd_stage_1.out1
        outputs.y12.next = outputs_2nd_stage_1.out2
        outputs.y13.next = outputs_2nd_stage_1.out3
        outputs.y14.next = outputs_2nd_stage_1.out4
        outputs.y15.next = outputs_2nd_stage_1.out5
        outputs.y16.next = outputs_2nd_stage_1.out6
        outputs.y17.next = outputs_2nd_stage_1.out7
        outputs.y20.next = outputs_2nd_stage_2.out0
        outputs.y21.next = outputs_2nd_stage_2.out1
        outputs.y22.next = outputs_2nd_stage_2.out2
        outputs.y23.next = outputs_2nd_stage_2.out3
        outputs.y24.next = outputs_2nd_stage_2.out4
        outputs.y25.next = outputs_2nd_stage_2.out5
        outputs.y26.next = outputs_2nd_stage_2.out6
        outputs.y27.next = outputs_2nd_stage_2.out7
        outputs.y30.next = outputs_2nd_stage_3.out0
        outputs.y31.next = outputs_2nd_stage_3.out1
        outputs.y32.next = outputs_2nd_stage_3.out2
        outputs.y33.next = outputs_2nd_stage_3.out3
        outputs.y34.next = outputs_2nd_stage_3.out4
        outputs.y35.next = outputs_2nd_stage_3.out5
        outputs.y36.next = outputs_2nd_stage_3.out6
        outputs.y37.next = outputs_2nd_stage_3.out7
        outputs.y40.next = outputs_2nd_stage_4.out0
        outputs.y41.next = outputs_2nd_stage_4.out1
        outputs.y42.next = outputs_2nd_stage_4.out2
        outputs.y43.next = outputs_2nd_stage_4.out3
        outputs.y44.next = outputs_2nd_stage_4.out4
        outputs.y45.next = outputs_2nd_stage_4.out5
        outputs.y46.next = outputs_2nd_stage_4.out6
        outputs.y47.next = outputs_2nd_stage_4.out7
        outputs.y50.next = outputs_2nd_stage_5.out0
        outputs.y51.next = outputs_2nd_stage_5.out1
        outputs.y52.next = outputs_2nd_stage_5.out2
        outputs.y53.next = outputs_2nd_stage_5.out3
        outputs.y54.next = outputs_2nd_stage_5.out4
        outputs.y55.next = outputs_2nd_stage_5.out5
        outputs.y56.next = outputs_2nd_stage_5.out6
        outputs.y57.next = outputs_2nd_stage_5.out7
        outputs.y60.next = outputs_2nd_stage_6.out0
        outputs.y61.next = outputs_2nd_stage_6.out1
        outputs.y62.next = outputs_2nd_stage_6.out2
        outputs.y63.next = outputs_2nd_stage_6.out3
        outputs.y64.next = outputs_2nd_stage_6.out4
        outputs.y65.next = outputs_2nd_stage_6.out5
        outputs.y66.next = outputs_2nd_stage_6.out6
        outputs.y67.next = outputs_2nd_stage_6.out7
        outputs.y70.next = outputs_2nd_stage_7.out0
        outputs.y71.next = outputs_2nd_stage_7.out1
        outputs.y72.next = outputs_2nd_stage_7.out2
        outputs.y73.next = outputs_2nd_stage_7.out3
        outputs.y74.next = outputs_2nd_stage_7.out4
        outputs.y75.next = outputs_2nd_stage_7.out5
        outputs.y76.next = outputs_2nd_stage_7.out6
        outputs.y77.next = outputs_2nd_stage_7.out7
        outputs.data_valid = outputs_2nd_stage_0.data_valid

    return second_stage_output, first_stage_to_second, first_1d, stage_2_inst_0,\
           stage_2_inst_1, stage_2_inst_2, stage_2_inst_3, stage_2_inst_4,\
           stage_2_inst_5, stage_2_inst_6, stage_2_inst_7

def convert():

    out_prec = 10

    inputs = input_interface()
    outputs = outputs_2d(out_prec)

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)

    inst = dct_2d(inputs, outputs, clock, reset, num_fractional_bits=14)
    inst.convert(hdl='vhdl')
    #analyze.simulator = 'ghdl'
    #assert dct_1d(inputs, outputs, clock, reset, num_fractional_bits=14).analyze_convert() == 0

if __name__ == '__main__':
    convert()



