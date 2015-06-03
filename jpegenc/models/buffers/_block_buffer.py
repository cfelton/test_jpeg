
from __future__ import absolute_import
from __future__ import print_function

from myhdl import *

def _dump_info():
    pass


def mdl_block_buffer(pxl, block_size=(9, 9), pwidth=(8,8,8)):
    """ Generate the MxN (rows x columns) block buffers.

    This model illustrates how a video stream is buffered
    and MxM blocks created.  The video stream is fed one
    row (line) at a time.  The buffer needs to store M rows
    into memory


    :param pxl: input pixel
    :param block_size: block size
    :param pwidth: pixel width
    :return:
    """
    pw = sum(pwidth)  # pixel width
    M, N = block_size

    # dump information
    _dump_info(block_size, pwidth)

    # memory buffers
    line_buffer_a = [Signal(intbv(0)[pw:])]
    line_buffer_b = []