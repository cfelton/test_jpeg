"""
Example (exploration) of interface types useful for a JPEG eoncder
system.
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


class PixelStream(object):
    def __init__(self, data_width=24):
        """A pixel-stream """
        self.data = Signal(intbv(0)[data_width:0])
        self.data_valid = Signal(bool(0))


class RGBStream(PixelStream):
    def __init__(self, color_space=(8, 8, 8)):
        assert len(color_space) == 3
        data_width = sum(color_space)

        super(PixelStream, self).__init__(data_width=data_width)

        rbits, gbits, bbits = color_space
        self.red = Signal(intbv(0)[rbits:0])
        self.green = Signal(intbv(0)[gbits:0])
        self.blue = Signal(intbv(0)[rbits:0])

        # alias to the above signals
        self.data = ConcatSignal(self.red, self.green, self.blue)


class YCbCrStream(PixelStream):
    def __init__(self, color_space=(8, 8, 8)):
        assert len(color_space) == 3
        data_width = sum(color_space)

        super(YCbCrStream, self).__init__(data_width=data_width)

        ybits, cbbits, crbits = color_space
        self.y = Signal(intbv(0)[ybits:])
        self.cb = Signal(intbv(0)[cbbits:])
        self.cr = Signal(intbv(0)[crbits:])

        # alias to the above color signals
        self.data = ConcatSignal(self.y, self.cb, self.cr)


class DataStream(object):
    def __init__(self):
        pass


class DataBlock(object):
    def __init__(self, size=8, min=0, max=8):
        """

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
        nrows, ncols = size
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
