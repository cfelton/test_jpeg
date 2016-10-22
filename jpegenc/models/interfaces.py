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

import myhdl
from myhdl import Signal, ConcatSignal, intbv, always_comb
try:
    from rhea import Signals, assign
except ImportError:
    from .useful_things import Signals, assign


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