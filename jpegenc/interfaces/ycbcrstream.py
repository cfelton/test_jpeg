
import myhdl
from myhdl import Signal, intbv, ConcatSignal
from .pixelstream import PixelStream


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
