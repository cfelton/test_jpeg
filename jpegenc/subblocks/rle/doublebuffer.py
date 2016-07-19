"""The above module is a double buffer
    to store runlength encoded data"""

from myhdl import always_comb, always_seq, block
from myhdl import intbv, Signal

from rhea.cores.fifo import fifo_sync
from rhea.system import FIFOBus
from rhea import Global


@block
def doublefifo(clock, reset, dfifo_bus, buffer_sel, depth=16):
    """
    I/O ports:

    dfifo_bus : A FIFOBus connection interace
    buffer_sel : select a buffer

    Constants :

    depth : depth of the fifo used
    width_data : width of the data to be stored in FIFO

    """

    # width of the input data
    width_data = len(dfifo_bus.write_data)

    # input to both the FIFO's
    fifo_data_in = Signal(intbv(0)[width_data:])

    # FIFOBus instantiation from rhea
    glbl = Global(clock, reset)
    fbus1 = FIFOBus(width=width_data)
    fbus2 = FIFOBus(width=width_data)

    assert isinstance(glbl, Global)
    assert isinstance(fbus1, FIFOBus)
    assert isinstance(fbus2, FIFOBus)

    # instantiate two sync FIFO's
    fifo_sync1 = fifo_sync(glbl, fbus1, depth)
    fifo_sync2 = fifo_sync(glbl, fbus2, depth)

    @always_comb
    def assign():
        """write data into FIFO's"""

        fbus1.write_data.next = fifo_data_in
        fbus2.write_data.next = fifo_data_in

    @always_seq(clock.posedge, reset=reset)
    def mux2_logic():
        """select buffer to pump data"""

        if not buffer_sel:
            fbus1.write.next = dfifo_bus.write

        else:
            fbus2.write.next = dfifo_bus.write

        fifo_data_in.next = dfifo_bus.write_data

    @always_comb
    def logic():
        """read or write into buffer"""

        fbus1.read.next = dfifo_bus.read if (
            buffer_sel) else False

        fbus2.read.next = dfifo_bus.read if (
            not buffer_sel) else False

        dfifo_bus.read_data.next = fbus1.read_data if (
            buffer_sel) else fbus2.read_data

        dfifo_bus.empty.next = fbus1.empty if (
            buffer_sel) else fbus2.empty

    return (
        fifo_sync1, fifo_sync2, assign, mux2_logic, logic)
