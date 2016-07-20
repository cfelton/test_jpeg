#!/usr/bin/env python
# coding=utf-8

import numpy as np

from itertools import chain
import myhdl
from myhdl import Signal, intbv, always_comb, always_seq, block, ResetSignal

from jpegenc.subblocks.color_converters import ColorSpace, rgb2ycbcr_v2
from jpegenc.subblocks.dct.dct_2d import dct_2d_transformation, dct_2d
from jpegenc.subblocks.zig_zag import zig_zag_scan, zig_zag
from jpegenc.subblocks.common import YCbCr_v2, input_interface, outputs_2d, RGB_v2, outputs_frontend_new


def frontend_transform(blockr, blockg, blockb, N=8):
    """software implementation of the frontend part"""
    ycbcr_blocks = [[[] for _ in range(N)] for _ in range(3)]
    dct_blocks, dct_blocks_linear, zig_zag_blocks = [[] for _ in range(3)]

    """Color space conversion"""
    for i in range(N):
        for j in range(N):
            red = blockr[i][j]
            green = blockg[i][j]
            blue = blockb[i][j]
            color_convert_obj = ColorSpace(red, green, blue)
            ycbcr = color_convert_obj.get_jfif_ycbcr()
            ycbcr = ycbcr.tolist()
            for k in range(3):
                ycbcr_blocks[k][i].append(ycbcr[k][0])

    for i in range(3):
        """dct-2d transformation"""
        dct_blocks.append(dct_2d_transformation(N).dct_2d_transformation(ycbcr_blocks[i]))
        """dct blocks to linear lists"""
        dct_blocks_linear.append(list(chain.from_iterable(dct_blocks[i])))
        """zig zag scan"""
        zig_zag_blocks.append(zig_zag_scan(N).zig_zag(dct_blocks_linear[i]))

    return zig_zag_blocks

@block
def frontend_top_level_v2(inputs, outputs, clock, reset, N=8):

    """
    Inputs:red, green , blue, data_valid
    Outputs: data_out
    """

    """Color Space Conversion"""
    rgb2ycbcr_out = YCbCr_v2()
    inputs_reg = RGB_v2()
    color_space_converter = rgb2ycbcr_v2(inputs_reg, rgb2ycbcr_out, clock, reset)

    """2D-DCT Transformation"""
    dct_2d_input = input_interface()

    dct_2d_output = outputs_2d()

    dct_2d_inst = dct_2d(dct_2d_input, dct_2d_output, clock, reset)

    """Zig-Zag Module"""
    zig_zag_out = outputs_2d()

    zig_zag_inst = zig_zag(dct_2d_output, zig_zag_out)

    """Intermediate signals"""
    input_counter = Signal(intbv(0, min=0, max=64))
    color_mode = Signal(intbv(0, min=0, max=3))
    output_counter = Signal(intbv(0, min=0, max=64))
    start_out = Signal(bool(0))

    @always_seq(clock.posedge, reset=reset)
    def input_reg():
        inputs_reg.red.next = inputs.red
        inputs_reg.green.next = inputs.green
        inputs_reg.blue.next = inputs.blue
        inputs_reg.data_valid.next = inputs.data_valid
        inputs_reg.color_mode.next = color_mode

    @always_comb
    def color_space_to_dct():
        """signal assignment from color_space_conversion module to dct_2d inputs"""
        if rgb2ycbcr_out.data_valid:
            dct_2d_input.data_in.next = rgb2ycbcr_out.data_out
            dct_2d_input.data_valid.next = rgb2ycbcr_out.data_valid

    @always_seq(clock.posedge, reset=reset)
    def first_control_signals_update():
        """Is used to update the control signal color_mode for the first mux of the rgb2ycbcr
        output to 2d dct"""
        if inputs.data_valid:
            if input_counter == 63:
                input_counter.next = 0
                if color_mode == 2:
                    color_mode.next = 0
                else:
                    color_mode.next = color_mode + 1
            else:
                input_counter.next = input_counter + 1

    @always_comb
    def set_start_out():
        if zig_zag_out.data_valid:
            start_out.next = True
            outputs.data_valid.next = zig_zag_out.data_valid
        else:
            outputs.data_valid.next = False


    @always_seq(clock.posedge, reset=reset)
    def zig_zag_to_output_mux():
        """signal assignment from zig zag to output"""
        if start_out:
            outputs.data_out.next = zig_zag_out.out_sigs[output_counter]

    @always_seq(clock.posedge, reset=reset)
    def output_counter_reset():
        if start_out:
            if output_counter == 63:
                output_counter.next = 0
            else:
                output_counter.next = output_counter + 1

    return (color_space_converter, zig_zag_inst, dct_2d_inst, color_space_to_dct,
            zig_zag_to_output_mux, first_control_signals_update, set_start_out,
            output_counter_reset, input_reg)

def convert():

    input_interface = RGB_v2()
    output_interface = outputs_frontend_new()
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=True, async=False)

    inst = frontend_top_level_v2(input_interface, output_interface, clock, reset)

    inst.convert(hdl='vhdl')
    inst.convert(hdl='verilog')

# convert()
