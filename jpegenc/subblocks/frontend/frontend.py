#!/usr/bin/env python
# coding=utf-8

import numpy as np

from itertools import chain
import myhdl
from myhdl import Signal, intbv, always_comb, always_seq, block

from jpegenc.subblocks.color_converters import ColorSpace
from jpegenc.subblocks.dct.dct_2d import dct_2d_transformation
from jpegenc.subblocks.zig_zag import zig_zag_scan


def frontend_transform(blockr, blockg, blockb, N):
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

