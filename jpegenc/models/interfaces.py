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
from myhdl import (Signal, SignalType, ResetSignal, ConcatSignal, intbv,
                   always_seq, always, always_comb, )
from myhdl import instance, delay, StopSimulation
from myhdl.conversion import verify

try:
    from rhea import Signals, assign
except ImportError:
    from .useful_things import Signals, assign

from . import ObjectWithBlocks

# @todo: refactor each of the interfaces to their own module
#     There is a fair amount of documentation with the interfaces.
#     Having the interfaces in their own file (python.module) makes
#     it easier to navigate


class DataStream(ObjectWithBlocks):
    def __init__(self, data_width=24):
        """Data stream with ready-valid flow control.

        The "next" property can only be used in simulation, it is
        not convertible!
        """
        self.data_width = data_width
        self.data = Signal(intbv(0)[data_width:0])
        self.valid = Signal(bool(0))
        self.ready = Signal(bool(0))
        super(DataStream, self).__init__(name='datastream')

    @property
    def next(self):
        return None

    @next.setter
    def next(self, ds):
        self._assign_next(ds)

    def _assign_next(self, stream):
        """Simulation assign only (see next)
        """
        assert isinstance(stream, DataStream)
        self.data.next = stream.data
        self.valid.next = stream.valid

    def copy(self):
        ds = DataStream(data_width=self.data_width)
        return ds

    @staticmethod
    def always_deco(clock=None):
        if clock is None:
            deco = always_comb
        else:
            deco = always(clock.posedge)

        return deco

    @myhdl.block
    def monitor(self):
        """
        In the current myhdl tracing there are some limitations
        that prevent most of the signals not to be traced in
        the interfaces.  This block will trace the signals in
        the interface.
        """
        # @todo: there is an odd issue with this and myhdl 1.0dev
        mdata = Signal(intbv(0)[len(self.data):0])
        mvalid = Signal(bool(0))
        mready = Signal(bool(0))

        @always_comb
        def mon_interface_attrs():
            mdata.next = self.data
            mvalid.next = self.valid
            mready.next = self.ready

        return mon_interface_attrs

    @myhdl.block
    def assign(self, ds, clock=None):
        """Assign another datastream to this datastream
        This assign block needs to be used in convertible in place
        of the `next` attribute.

        Args:
            ds (DataStream): the datastream to assign from
            clock (Signal): system clock, optional

        This needs to be implemented for each interface that uses
        DataStream as a base class.  In subclasses the `data` field
        is read-only (shadow), the lower bits are the data bits and
        upper bits of the data field are additional control and meta
        data.

        myhdl convertible
        """
        assert isinstance(ds, DataStream)

        @self.always_deco(clock)
        def beh_assign():
            self.data.next = ds.data
            self.ready.next = ds.ready
            self.valid.next = ds.valid

        return beh_assign


class PixelStream(DataStream):
    def __init__(self, data_width=24):
        """Pixel stream."""
        self.start_of_frame = Signal(bool(0))
        self.end_of_frame = Signal(bool(0))
        self.pixel = Signal(intbv(0)[data_width:0])
        super(PixelStream, self).__init__(data_width+2)

        # override the data to be a shadow (read-only)
        self.data = ConcatSignal(self.start_of_frame,
                                 self.end_of_frame,
                                 self.pixel)

    def _assign_next(self, stream):
        assert isinstance(stream, PixelStream)
        self.pixel.next = stream.pixel
        self.valid.next = stream.valid
        self.start_of_frame.next = stream.start_of_frame
        self.end_of_frame.next = stream.end_of_frame

    def copy(self):
        raise NotImplementedError


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
        super(RGBStream, self).__init__(data_width=data_width+2)

        self.color_depth = color_depth
        rbits, gbits, bbits = color_depth

        # a single pixel (color component) is the most
        self.num_pixels = num_pixels
        if num_pixels == 1:
            self.red = Signal(intbv(0)[rbits:0])
            self.green = Signal(intbv(0)[gbits:0])
            self.blue = Signal(intbv(0)[rbits:0])
            # alias to the above signals, overrides data, data is
            # a shadow (read-only) of the RGB attributes
            self.data = ConcatSignal(self.start_of_frame, self.end_of_frame,
                                     self.red, self.green, self.blue)
        else:
            self.red = Signals(intbv(0)[rbits:0], num_pixels)
            self.green = Signals(intbv(0)[gbits:0], num_pixels)
            self.blue = Signals(intbv(0)[rbits:0], num_pixels)
            # @todo data alias for multiple pixels
            raise NotImplementedError

    def copy(self):
        rgb = RGBStream(color_depth=self.color_depth,
                        num_pixels=self.num_pixels)
        return rgb

    def _assign_next(self, stream):
        if isinstance(stream, RGBStream):
            self.valid.next = stream.valid
            self.start_of_frame.next = stream.start_of_frame
            self.end_of_frame.next = stream.end_of_frame
            self.red.next = stream.red
            self.green.next = stream.green
            self.blue.next = stream.blue
        elif isinstance(stream, (DataStream, SignalType,)):
            data = stream.data if isinstance(stream, DataStream) else stream
            assert len(data) == len(self.data)
            rbits, gbits, bbits = self.color_depth
            self.blue.next = data[bbits:0]
            self.green.next = data[gbits + bbits:bbits]
            self.red.next = data[rbits + gbits + bbits:gbits]
            self.end_of_frame.next = data[rbits]
            self.start_of_frame.next = data[rbits + 1]
        else:
            raise TypeError("Invalid stream type {}".format(type(stream)))

    @myhdl.block
    def assign(self, stream, clock=None):
        # @todo this should be identical to _assign_next
        #    but the assignments need to be wrapped in a myhdl always decorator

        # @todo: maybe make these external modules and name the instances
        #    if RGBStream:
        #        inst = rgb_assign_rgbstream(stream, clock)
        #    elif DataStream, SignalType
        #        inst = rgb_assign_data(data, color_depth, clock)
        #    inst.name = self.name
        if isinstance(stream, RGBStream):
            @self.always_deco(clock)
            def beh_assign():
                pass
        elif isinstance(stream (DataStream, SignalType)):
            data = stream.data if isinstance(stream, DataStream) else stream
            assert len(data) == len(self.data)
            rbits, gbits, bbits = self.color_depth

            @self.always_deco(clock)
            def beh_assign():
                pass
        else:
            raise TypeError("Invalid stream type {}".format(type(stream)))

        raise NotImplementedError

        return beh_assign


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

    def copy(self):
        raise NotImplementedError

    def _assign_next(self, stream):
        raise NotImplementedError

    def assign(self, ds, clock=None):
        raise NotImplementedError


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