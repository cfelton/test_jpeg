
from __future__ import print_function, division

from math import ceil

import myhdl
from myhdl import Signal, intbv, always


class PixelStream(object):
    def __init__(self, resolution=(640, 480,), pformat=(8, 8, 8)):
        """ Pixel stream interface
        """
        # @todo: merge this with jpegenc.interfaces.pixelstream.py
        self.resolution = resolution
        self.pformat = pformat
        self.width = sum(pformat)
        pmax = (2**self.width)-1
        self.pixel = Signal(intbv(pmax)[self.width:])
        self.valid = Signal(bool(0))
        self.clock = Signal(bool(0))

    @myhdl.block
    def generate_stream(self):

        @always(self.clock.posedge)
        def mdl_stream():
            self.valid.next = True
            # self.pixel.next = randint(0, self.pixel.max-1)
            if self.pixel == self.pixel.max-1:
                self.pixel.next = 0
            else:
                self.pixel.next = self.pixel + 1

        return mdl_stream


class ImageBlock(object):
    def __init__(self, pxl, block_size=(9, 9)):
        """ Interface to a block of memory
        This interface is used to retrieve blocks of an image.
        """
        pw = pxl.width
        v, h = pxl.resolution
        m, n = block_size
        self.block_size = block_size

        self.pixel = Signal(intbv(0)[pw:])
        self.row = Signal(intbv(0, min=0, max=m))
        self.col = Signal(intbv(0, min=0, max=n))

        # number of blocks in a buffer, number of blocks in a row
        self.blocks_per_buffer = bpb = h//n
        self.block_num = Signal(intbv(0, min=0, max=bpb))


def _dump_info(resolution, block_size, pwidth):
    """ Print some information on the parameters
    Need to capture M row, the required memory would be the
    video horizontal resolution times M times the number of
    bytes required for a pixel times 2 (double buffered).

    Args:
        resolution: video resolution
        block_size: the sub-image size (matrix size)
        pwidth: pixel width (change to color_depth)
    """
    v, h = resolution
    m, n = block_size
    bytez = int(ceil(pwidth / 8))
    mem_bytes = 2 * m * h * bytez
    print("Memory requirements:")
    print("  {:d} bytes for double buffer".format(mem_bytes))

    return bytes, mem_bytes


@myhdl.block
def mdl_block_buffer(pxl, bmem):
    """ Generate the MxN (rows x columns) block buffers.

    This model illustrates how a video stream is buffered
    and MxM blocks created.  The video stream is fed one
    row (line) at a time.  The buffer needs to store M rows
    into memory

    Args:
        pxl: input pixel stream interface
        bmem: block memory interface
    """
    block_size = bmem.block_size
    pw = pxl.width         # pixel width
    v, h = pxl.resolution  # video stream resolution
    m, n = block_size      # block size

    # dump information
    bytez, mb = _dump_info(pxl.resolution, block_size, pw)

    # memory buffers, double buffered
    num_pixels = m * h
    line_buffer_a = [Signal(intbv(0)[pw:]) for _ in range(num_pixels)]
    line_buffer_b = [Signal(intbv(0)[pw:]) for _ in range(num_pixels)]

    anotb = Signal(bool(0))
    ccnt = Signal(intbv(0, min=0, max=m*h))

    # input double buffer, capture the stream
    @always(pxl.clock.posedge)
    def mdl_input_capture():
        if pxl.valid:
            if anotb:
                line_buffer_a[ccnt].next = pxl.pixel
            else:
                line_buffer_b[ccnt].next = pxl.pixel

            if ccnt == num_pixels - 1:
                ccnt.next = 0
                anotb.next = not anotb
            else:
                ccnt.next = ccnt + 1

    @always(pxl.clock.posedge)
    def mdl_output():
        # @todo: translate row,col to linear address
        bmem.pixel.next = 0x555AAA

    return mdl_input_capture, mdl_output
