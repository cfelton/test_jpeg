"""
Example (exploration) of interface types useful for a JPEG encoder
system.  The JPEG encoder (jpegenc) has a collection of processing
blocks with a data-streaming interface to each.  The data-streaming
interface is a read-valid flow control interface [1].

The base interface has a ``data``, ``ready``, and ``valid``
attributes, this interface is sufficient to completely define
the data flow between processing blocks (for our first system
definition):

"""

from random import randint

import myhdl
from myhdl import (Signal, ResetSignal, ConcatSignal, intbv,
                   always_seq, always_comb, )
from myhdl import instance, delay, StopSimulation
from myhdl.conversion import verify

try:
    from rhea import Signals, assign
except ImportError:
    from .useful_things import Signals, assign


class DataStream(object):
    def __init__(self, data_width=24):
        """Data stream with ready-valid flow control."""
        self.data = Signal(intbv(0)[data_width:0])
        self.valid = Signal(bool(0))
        self.ready = Signal(bool(0))

    def assign(self, stream):
        assert isinstance(stream, DataStream)
        self.data.next = stream.data
        self.valid.next = stream.valid


class PixelStream(DataStream):
    def __init__(self, data_width=24):
        """Pixel stream."""
        self.start_of_frame = Signal(bool(0))
        self.end_of_frame = Signal(bool(0))
        super(PixelStream, self).__init__(data_width+2)
        self.data = ConcatSignal(self.start_of_frame, self.end_of_frame,
                                 self.data)

    def assign(self, stream):
        assert isinstance(stream, PixelStream)
        self.data.next = stream.data
        self.valid.next = stream.valid
        self.start_of_frame.next = stream.start_of_frame
        self.end_of_frame.next = stream.end_of_frame

    # def map_to_data(self):
    #     raise NotImplementedError()


class RGBStream(PixelStream):
    def __init__(self, color_depth=(8, 8, 8), num_pixels=1):
        """A red-green-blue pixel stream.
        Args:
            color_depth (tuple): the number of bits for each color component.
            num_pixels (int): define the number of pixels in this interface,
                this is used to define a parallel interface.
        """
        assert len(color_depth) == 3
        data_width = sum(color_depth)
        super(PixelStream, self).__init__(data_width=data_width)

        self.color_depth = color_depth
        rbits, gbits, bbits = color_depth

        # a single pixel (color component) is the most
        if num_pixels == 1:
            self.red = Signal(intbv(0)[rbits:0])
            self.green = Signal(intbv(0)[gbits:0])
            self.blue = Signal(intbv(0)[rbits:0])
            # alias to the above signals
            self.data = ConcatSignal(self.start_of_frame, self.end_of_frame,
                                     self.red, self.green, self.blue)
        else:
            self.red = Signals(intbv(0)[rbits:0], num_pixels)
            self.green = Signals(intbv(0)[gbits:0], num_pixels)
            self.blue = Signals(intbv(0)[rbits:0], num_pixels)
            # @todo data alias for multiple pixels
            raise NotImplementedError

    def assign(self, stream):
        assert isinstance(stream, RGBStream)
        self.valid.next = stream.valid
        self.start_of_frame.next = stream.start_of_frame
        self.end_of_frame.next = stream.end_of_frame
        self.red.next = stream.red
        self.green.next = stream.green
        self.blue.next = stream.blue
        
    def assign_from_data(self, data):
        """Given a data vector, update the attributes"""
        assert len(data) == len(self.data)
        rbits, gbits, bbits = self.color_depth
        self.blue.next = data[bbits:0]
        self.green.next = data[gbits+bbits:bbits]
        self.red.next = data[rbits+gbits+bbits:gbits]
        self.end_of_frame.next = data[rbits]
        self.start_of_frame.next = data[rbits+1]

    # @myhdl.block
    # def map_to_data(self):
    #     """Map red, green, and blue to data
    #     The base interface to all the subblocks is `DataStream` but in most
    #     of the subblocks it is more convenient to deal with the color
    #     components.  When using the color components the data needs to be
    #     assigned.
    #
    #     myhdl convertible
    #     """
    #     raise NotImplementedError
    #
    #     # insts = []
    #     # for nn in range(self.num_pixels):
    #     #     for jj in range(3):
    #     #         insts = assign()


class YCbCrStream(PixelStream):
    def __init__(self, color_depth=(8, 8, 8)):
        """A y-cb-cr pixel stream.

        Args:
            color_depth (tuple): the number of bits for each color component
        """
        assert len(color_depth) == 3
        data_width = sum(color_depth)

        super(YCbCrStream, self).__init__(data_width=data_width)

        ybits, cbbits, crbits = color_depth
        self.y = Signal(intbv(0)[ybits:])
        self.cb = Signal(intbv(0)[cbbits:])
        self.cr = Signal(intbv(0)[crbits:])

        # alias to the above color signals
        self.data = ConcatSignal(self.y, self.cb, self.cr)


class DataBlock(object):
    def __init__(self, size=8, min=0, max=8):
        """A block of data (parallel data) that is transferred together.

        Arguments:
            size: the number of items to have in the block
            min: the data min value
            max: the data max value
        """
        self.size = size
        dtype = intbv(0, min=min, max=max)
        self.data = Signals(dtype, size)
        self.valid = Signal(bool(0))
        self.ready = Signal(bool(0))


class ImageBlock(object):
    def __init__(self, size=(8, 8), min=0, max=8):
        """

        Arguments:
            size (tuple):
            min (int): the min value of the data contained in the
                matrix
            max (int)L the max value of the data contained in the
                matrix

        """
        assert isinstance(size, tuple)
        assert len(size) == 2
        self.size = size
        ncols, nrows = size
        self.nitems = nrows * ncols
        dtype = intbv(0, min=min, max=max)
        self.nbits = len(dtype)
        self.dtype = dtype

        self.mat = [Signals(dtype, ncols) for _ in range(nrows)]

        self.data = self.get_bit_vector()
        self.valid = Signal(bool(0))
        self.ready = Signal(bool(0))

    def __getitem__(self, idx):
        item = None
        if isinstance(idx, tuple):
            item = self.mat[idx[0]][idx[1]]

        return item

    def __setitem__(self):
        raise NotImplementedError

    def get_bit_vector(self):
        nrows, ncols = self.size
        nbits = nrows * ncols * self.nbits
        sig = Signal(intbv(0)[nbits:0])
        return sig

    @myhdl.block
    def stack(self, flat):
        """ """
        nitems = sum(self.size)
        nbits = self.nbits
        assert len(flat) == nitems*nbits
        # create a flat list of signals (references)

    @myhdl.block
    def flatten(self, flat):
        """ """
        nbits = self.nbits
        shadowbits = [col(nbits, 0) for row in self.mat for col in row]
        flats = ConcatSignal(*shadowbits)

        @always_comb
        def beh_assign():
            flat.next = flats

        return beh_assign