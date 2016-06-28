
import numpy as np
from math import sqrt, pi, cos
import myhdl
from myhdl import Signal, ResetSignal, intbv, always_comb, always_seq, instance
from myhdl.conversion import analyze

from interfaces import (input_1d_1st_stage, input_interface, output_interface,
                        outputs_2d, input_1d_2nd_stage)
from dct_1d import dct_1d


class dct_2d_transformation(object):

    def __init__(self):
        const = sqrt(2.0/8)
        a = const * cos(pi/4)
        b = const * cos(pi/16)
        c = const * cos(pi/8)
        d = const * cos(3*pi/16)
        e = const * cos(5*pi/16)
        f = const * cos(3*pi/8)
        g = const * cos(7*pi/16)

        self.coeff_matrix = [[a, a, a, a, a, a, a, a],
                             [b, d, e, g, -g, -e, -d, -b],
                             [c, f, -f, -c, -c, -f, f, c],
                             [d, -g, -b, -e, e, b, g, -d],
                             [a, -a, -a, a, a, -a, -a, a],
                             [e, -b, g, d, -d, -g, b, -e],
                             [f, -c, c, -f, -f, c, -c, f],
                             [g, -e, d, -b, b, -d, e, -g]]


    def dct_2d_transformation(self, block):

        coeff_matrix = np.asarray(self.coeff_matrix)
        block = np.asarray(block)
        block = block - 128
        # first 1d-dct with rows
        dct_result = np.dot(coeff_matrix, np.transpose(block))
        # second 1d-dct with columns
        dct_result = np.rint(dct_result)
        dct_result = np.dot(coeff_matrix, np.transpose(dct_result))
        dct_result = np.rint(dct_result).astype(int)
        return dct_result


@myhdl.block
def dct_2d(inputs, outputs, clock, reset, num_fractional_bits=14, out_prec=10):

    first_1d_output = output_interface()
    input_1d_stage_1 = input_1d_1st_stage()

    first_1d = dct_1d(input_1d_stage_1, first_1d_output, clock,
                      reset, num_fractional_bits)

    inputs_2nd_stage_0 = input_1d_2nd_stage(first_1d_output.out_precision)
    inputs_2nd_stage_1 = input_1d_2nd_stage(first_1d_output.out_precision)
    inputs_2nd_stage_2 = input_1d_2nd_stage(first_1d_output.out_precision)
    inputs_2nd_stage_3 = input_1d_2nd_stage(first_1d_output.out_precision)
    inputs_2nd_stage_4 = input_1d_2nd_stage(first_1d_output.out_precision)
    inputs_2nd_stage_5 = input_1d_2nd_stage(first_1d_output.out_precision)
    inputs_2nd_stage_6 = input_1d_2nd_stage(first_1d_output.out_precision)
    inputs_2nd_stage_7 = input_1d_2nd_stage(first_1d_output.out_precision)

    outputs_2nd_stage_0 = output_interface(out_prec)
    outputs_2nd_stage_1 = output_interface(out_prec)
    outputs_2nd_stage_2 = output_interface(out_prec)
    outputs_2nd_stage_3 = output_interface(out_prec)
    outputs_2nd_stage_4 = output_interface(out_prec)
    outputs_2nd_stage_5 = output_interface(out_prec)
    outputs_2nd_stage_6 = output_interface(out_prec)
    outputs_2nd_stage_7 = output_interface(out_prec)

    stage_2_inst_0 = dct_1d(inputs_2nd_stage_0, outputs_2nd_stage_0, clock,
                            reset, num_fractional_bits)
    stage_2_inst_1 = dct_1d(inputs_2nd_stage_1, outputs_2nd_stage_1, clock,
                            reset, num_fractional_bits)
    stage_2_inst_2 = dct_1d(inputs_2nd_stage_2, outputs_2nd_stage_2, clock,
                            reset, num_fractional_bits)
    stage_2_inst_3 = dct_1d(inputs_2nd_stage_3, outputs_2nd_stage_3, clock,
                            reset, num_fractional_bits)
    stage_2_inst_4 = dct_1d(inputs_2nd_stage_4, outputs_2nd_stage_4, clock,
                            reset, num_fractional_bits)
    stage_2_inst_5 = dct_1d(inputs_2nd_stage_5, outputs_2nd_stage_5, clock,
                            reset, num_fractional_bits)
    stage_2_inst_6 = dct_1d(inputs_2nd_stage_6, outputs_2nd_stage_6, clock,
                            reset, num_fractional_bits)
    stage_2_inst_7 = dct_1d(inputs_2nd_stage_7, outputs_2nd_stage_7, clock,
                            reset, num_fractional_bits)

    data_in_signed = Signal(intbv(0, min=-input_1d_stage_1.in_range,
                                  max=input_1d_stage_1.in_range))
    data_valid_reg = Signal(bool(0))
    data_valid_reg2 = Signal(bool(0))

    counter = Signal(intbv(0, min=0, max=8))

    @always_seq(clock.posedge, reset=reset)
    def input_subtract():
        if inputs.data_valid:
            data_in_signed.next = inputs.data_in
            input_1d_stage_1.data_in.next = data_in_signed - 128
            data_valid_reg.next = inputs.data_valid
            input_1d_stage_1.data_valid.next = data_valid_reg

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
        outputs.y00.next = outputs_2nd_stage_0.out0
        outputs.y01.next = outputs_2nd_stage_1.out0
        outputs.y02.next = outputs_2nd_stage_2.out0
        outputs.y03.next = outputs_2nd_stage_3.out0
        outputs.y04.next = outputs_2nd_stage_4.out0
        outputs.y05.next = outputs_2nd_stage_5.out0
        outputs.y06.next = outputs_2nd_stage_6.out0
        outputs.y07.next = outputs_2nd_stage_7.out0
        outputs.y10.next = outputs_2nd_stage_0.out1
        outputs.y11.next = outputs_2nd_stage_1.out1
        outputs.y12.next = outputs_2nd_stage_2.out1
        outputs.y13.next = outputs_2nd_stage_3.out1
        outputs.y14.next = outputs_2nd_stage_4.out1
        outputs.y15.next = outputs_2nd_stage_5.out1
        outputs.y16.next = outputs_2nd_stage_6.out1
        outputs.y17.next = outputs_2nd_stage_7.out1
        outputs.y20.next = outputs_2nd_stage_0.out2
        outputs.y21.next = outputs_2nd_stage_1.out2
        outputs.y22.next = outputs_2nd_stage_2.out2
        outputs.y23.next = outputs_2nd_stage_3.out2
        outputs.y24.next = outputs_2nd_stage_4.out2
        outputs.y25.next = outputs_2nd_stage_5.out2
        outputs.y26.next = outputs_2nd_stage_6.out2
        outputs.y27.next = outputs_2nd_stage_7.out2
        outputs.y30.next = outputs_2nd_stage_0.out3
        outputs.y31.next = outputs_2nd_stage_1.out3
        outputs.y32.next = outputs_2nd_stage_2.out3
        outputs.y33.next = outputs_2nd_stage_3.out3
        outputs.y34.next = outputs_2nd_stage_4.out3
        outputs.y35.next = outputs_2nd_stage_5.out3
        outputs.y36.next = outputs_2nd_stage_6.out3
        outputs.y37.next = outputs_2nd_stage_7.out3
        outputs.y40.next = outputs_2nd_stage_0.out4
        outputs.y41.next = outputs_2nd_stage_1.out4
        outputs.y42.next = outputs_2nd_stage_2.out4
        outputs.y43.next = outputs_2nd_stage_3.out4
        outputs.y44.next = outputs_2nd_stage_4.out4
        outputs.y45.next = outputs_2nd_stage_5.out4
        outputs.y46.next = outputs_2nd_stage_6.out4
        outputs.y47.next = outputs_2nd_stage_7.out4
        outputs.y50.next = outputs_2nd_stage_0.out5
        outputs.y51.next = outputs_2nd_stage_1.out5
        outputs.y52.next = outputs_2nd_stage_2.out5
        outputs.y53.next = outputs_2nd_stage_3.out5
        outputs.y54.next = outputs_2nd_stage_4.out5
        outputs.y55.next = outputs_2nd_stage_5.out5
        outputs.y56.next = outputs_2nd_stage_6.out5
        outputs.y57.next = outputs_2nd_stage_7.out5
        outputs.y60.next = outputs_2nd_stage_0.out6
        outputs.y61.next = outputs_2nd_stage_1.out6
        outputs.y62.next = outputs_2nd_stage_2.out6
        outputs.y63.next = outputs_2nd_stage_3.out6
        outputs.y64.next = outputs_2nd_stage_4.out6
        outputs.y65.next = outputs_2nd_stage_5.out6
        outputs.y66.next = outputs_2nd_stage_6.out6
        outputs.y67.next = outputs_2nd_stage_7.out6
        outputs.y70.next = outputs_2nd_stage_0.out7
        outputs.y71.next = outputs_2nd_stage_1.out7
        outputs.y72.next = outputs_2nd_stage_2.out7
        outputs.y73.next = outputs_2nd_stage_3.out7
        outputs.y74.next = outputs_2nd_stage_4.out7
        outputs.y75.next = outputs_2nd_stage_5.out7
        outputs.y76.next = outputs_2nd_stage_6.out7
        outputs.y77.next = outputs_2nd_stage_7.out7
        outputs.data_valid.next = data_valid_reg2

    @always_seq(clock.posedge, reset=reset)
    def counter_update():
        if outputs_2nd_stage_0.data_valid:
            if counter == 7:
                counter.next = 0
            else:
                counter.next = counter + 1

    @always_comb
    def data_valid_2d():
        if outputs_2nd_stage_0.data_valid and counter == 0:
            data_valid_reg2.next = True
        else:
            data_valid_reg2.next = False
            """reset counter for the next outputs"""

    return (input_subtract, second_stage_output, first_stage_to_second,
            stage_2_inst_0, stage_2_inst_1, stage_2_inst_2, stage_2_inst_3,
            stage_2_inst_4, stage_2_inst_5, stage_2_inst_6, stage_2_inst_7,
            data_valid_2d, counter_update, first_1d)


def convert():

    out_prec = 10
    fract_bits = 14
    inputs = input_interface()
    outputs = outputs_2d(out_prec)

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)

    analyze.simulator = 'ghdl'
    assert dct_2d(inputs, outputs, clock, reset,
                  fract_bits, out_prec).analyze_convert() == 0

if __name__ == '__main__':
    convert()
