
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from math import ceil

from myhdl import *


def _dump_info(resolution, block_size, pwidth):
    """ Print some information on the parameters
    :param block_size:
    :param pwidth:
    :return:
    """
    M, N = block_size
    bytes = ceil(pwidth / 8)
    mem_bytes = 2 * M * N * bytes
    print("Memory requirements:")
    print("  {:d} bytes for double buffer".format(mem_bytes))

    return bytes, mem_bytes


def mdl_block_buffer(
        # ~~~[interfaces]~~~
        pxl,      # pixel video stream
        bmem,     # block memory interface

        # ~~~[parameters]~~~
        resolution=(640, 480),
        block_size=(9, 9),
        pwidth=(8, 8, 8)):
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
    bytes, mb = _dump_info(block_size, pw)

    # memory buffers, double buffered
    line_buffer_a = [Signal(intbv(0)[pw:]) for _ in range(M)]
    line_buffer_b = [Signal(intbv(0)[pw:])]