
import myhdl
from myhdl import Signal, intbv, always, always_comb

from .object_with_blocks import ObjectWithBlocks


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
        data = self.data
        valid = self.valid
        ready = self.ready
        changed = Signal(bool(0))

        @always_comb
        def mon_interface_attrs():
            if valid or ready or data > 0:
                changed.next = True
            else:
                changed.next = False

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
