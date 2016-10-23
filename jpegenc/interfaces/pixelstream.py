
import myhdl
from myhdl import Signal, intbv, ConcatSignal
from .datastream import DataStream


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

    @myhdl.block
    def process(self):
        raise NotImplementedError
