#!/usr/bin/env python
# coding=utf-8

import numpy as np

from itertools import chain
import myhdl
from myhdl import Signal, intbv, always_comb, always_seq, block, ResetSignal

from jpegenc.subblocks.color_converters import ColorSpace, rgb2ycbcr
from jpegenc.subblocks.dct.dct_2d import dct_2d_transformation, dct_2d
from jpegenc.subblocks.zig_zag import zig_zag_scan, zig_zag
from jpegenc.subblocks.common import YCbCr, input_interface, outputs_2d, RGB, outputs_frontend


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
def frontend_top_level(inputs, outputs, clock, reset, N=8):

    """
    Inputs:red, green , blue, data_valid
    Outputs: 3 lists of 64 signals
    """

    """Color Space Conversion"""
    rgb2ycbcr_out = YCbCr()
    color_space_converter = rgb2ycbcr(inputs, rgb2ycbcr_out, clock, reset)

    """2D-DCT Transformation of Y, Cb, Cr"""
    y_2d_dct_input = input_interface()
    cb_2d_dct_input = input_interface()
    cr_2d_dct_input = input_interface()

    y_2d_dct_output = outputs_2d()
    cb_2d_dct_output = outputs_2d()
    cr_2d_dct_output = outputs_2d()

    y_2d_dct = dct_2d(y_2d_dct_input, y_2d_dct_output, clock, reset)
    cb_2d_dct = dct_2d(cb_2d_dct_input, cb_2d_dct_output, clock, reset)
    cr_2d_dct = dct_2d(cr_2d_dct_input, cr_2d_dct_output, clock, reset)

    """Zig-Zag Module"""
    y_zig_zag_out = outputs_2d()
    cb_zig_zag_out = outputs_2d()
    cr_zig_zag_out = outputs_2d()

    y_zig_zag = zig_zag(y_2d_dct_output, y_zig_zag_out)
    cb_zig_zag = zig_zag(cb_2d_dct_output, cb_zig_zag_out)
    cr_zig_zag = zig_zag(cr_2d_dct_output, cr_zig_zag_out)

    @always_comb
    def color_space_to_dct():
        """signal assignment from color_space_conversion module to dct_2d inputs"""
        if rgb2ycbcr_out.data_valid:
            y_2d_dct_input.data_in.next = rgb2ycbcr_out.y
            y_2d_dct_input.data_valid.next = rgb2ycbcr_out.data_valid
            cb_2d_dct_input.data_in.next = rgb2ycbcr_out.cb
            cb_2d_dct_input.data_valid.next = rgb2ycbcr_out.data_valid
            cr_2d_dct_input.data_in.next = rgb2ycbcr_out.cr
            cr_2d_dct_input.data_valid.next = rgb2ycbcr_out.data_valid

    @always_comb
    def zig_zag_to_output():
        """signal assignment from zig zag to output"""
        if y_zig_zag_out.data_valid:
            for i in range(N**2):
                outputs.y_dct_out[i].next = y_zig_zag_out.out_sigs[i]
                outputs.cb_dct_out[i].next = cb_zig_zag_out.out_sigs[i]
                outputs.cr_dct_out[i].next = cr_zig_zag_out.out_sigs[i]
            outputs.data_valid.next = y_zig_zag_out.data_valid

    return (color_space_converter, y_2d_dct, cb_2d_dct, cr_2d_dct, y_zig_zag, cb_zig_zag,
            cr_zig_zag, color_space_to_dct, zig_zag_to_output)

def convert():

    input_interface = RGB()
    output_interface = outputs_frontend()
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=True, async=False)

    inst = frontend_top_level(input_interface, output_interface, clock, reset)

    inst.convert(hdl='vhdl')
    inst.convert(hdl='verilog')


