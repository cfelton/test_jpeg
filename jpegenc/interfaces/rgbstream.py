
import myhdl
from myhdl import Signal, intbv, ConcatSignal, SignalType
from rhea import Signals

from .datastream import DataStream
from .pixelstream import PixelStream


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
