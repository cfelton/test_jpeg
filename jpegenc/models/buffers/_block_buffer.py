
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from math import ceil
from random import randint

from myhdl import *


class PixelStream(object):
    """ Pixel stream interface
    """
    def __init__(self, resolution=(640, 480,), pformat=(8, 8, 8)):
        self.resolution = resolution
        self.pformat = pformat
        self.width = sum(pformat)
        self.pixel = Signal(intbv(0)[self.width:])
        self.valid = Signal(bool(0))
        self.clock = Signal(bool(0))

    def generate_stream(self):

        @always(self.clock.posedge)
        def mdl_stream():
            self.valid.next = True
            #self.pixel.next = randint(0, self.pixel.max-1)
            if self.pixel == self.pixel.max-1:
                self.pixel.next = 0
            else:
                self.pixel.next = self.pixel + 1

        return mdl_stream


class ImageBlock(object):
    """ Interface to a block of memory
    This interface is used to retrieve blocks of an image
    """
    def __init__(self, pxl, block_size=(9, 9)):

        pw = pxl.width
        V, H = pxl.resolution
        M, N = block_size
        self.block_size = block_size

        self.pixel = Signal(intbv(0)[pw:])
        self.row = Signal(intbv(0, min=0, max=M))
        self.col = Signal(intbv(0, min=0, max=N))

        # number of blocks in a buffer, number of blocks in a row
        self.blocks_per_buffer = H//N
        self.block_num = Signal(intbv(0, min=0,
                                      max=self.blocks_per_buffer))


def _dump_info(resolution, block_size, pwidth):
    """ Print some information on the parameters
    Need to capture M row, the required memory would be the
    video horizontal resolution times M times the number of
    bytes required for a pixel times 2 (double buffered).

    :param block_size:
    :param pwidth:
    :return bytes:
    :return mem_bytes:
    """
    V, H = resolution
    M, N = block_size
    bytes = int(ceil(pwidth / 8))
    mem_bytes = 2 * M * H * bytes
    print("Memory requirements:")
    print("  {:d} bytes for double buffer".format(mem_bytes))

    return bytes, mem_bytes


def mdl_block_buffer(pxl, bmem):
    """ Generate the MxN (rows x columns) block buffers.

    This model illustrates how a video stream is buffered
    and MxM blocks created.  The video stream is fed one
    row (line) at a time.  The buffer needs to store M rows
    into memory


    :param pxl: input pixel stream interface
    :param bmem: block memory interface
    :return:
    """
    block_size = bmem.block_size
    pw = pxl.width         # pixel width
    V, H = pxl.resolution  # video stream resolution
    M, N = block_size      # block size

    # dump information
    bytes, mb = _dump_info(pxl.resolution, block_size, pw)

    # memory buffers, double buffered
    num_pixels = M*H
    line_buffer_a = [Signal(intbv(0)[pw:]) for _ in range(num_pixels)]
    line_buffer_b = [Signal(intbv(0)[pw:]) for _ in range(num_pixels)]

    anotb = Signal(bool(0))
    ccnt = Signal(intbv(0, min=0, max=M*H))

    # input double buffer, capture the stream
    @always(pxl.clock.posedge)
    def mdl_input_capture():
        if pxl.valid:
            if anotb:
                line_buffer_a[ccnt].next = pxl.pixel
            else:
                line_buffer_b[ccnt].next = pxl.pixel

            if ccnt == num_pixels-1:
                ccnt.next = 0
                anotb.next = not anotb
            else:
                ccnt.next = ccnt + 1

    @always(pxl.clock.posedge)
    def mdl_output():
        # @todo: translate row,col to linear address
        bmem.pixel.next = 0xAAA

    return mdl_input_capture, mdl_output