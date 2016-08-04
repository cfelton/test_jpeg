"""This module is the MyHDL implementation of
    run length encoder top module"""

from myhdl import always_seq, always_comb, block
from myhdl import Signal, concat, modbv
from jpegenc.subblocks.rle.rlecore import DataStream, rle
from jpegenc.subblocks.rle.rlecore import RLESymbols, RLEConfig
from jpegenc.subblocks.rle.doublebuffer import doublefifo
from rhea.system import FIFOBus


class BufferDataBus(RLESymbols):
    """
    Connections related to output data buffer

    Amplitude   : amplitude of the number
    size        : size required to store amplitude
    runlength   : number of zeros
    dovalid     : asserts if ouput data is valid
    buffer_sel  : select the buffer in double buffer
    read_enable : read data from the output fifo
    fifo_empty  : asserts if any of the two fifos are empty

    """
    def __init__(self, width_data, width_size, width_runlength):
        super(BufferDataBus, self).__init__(
            width_data, width_size, width_runlength)

        self.buffer_sel = Signal(bool(0))
        self.read_enable = Signal(bool(0))
        self.fifo_empty = Signal(bool(0))


@block
def rlencoder(clock, reset, datastream, bufferdatabus, rleconfig):
    """
    The top module connects rle core and rle double buffer

    I/O Ports:

    datastream      : input datastream bus
    buffer data bus : output data bus
    rleconfig       : configuration bus

    Constants:

    width_data      : input data width
    width_addr      : address width
    width_size      : width of register to store amplitude size
    max_addr_cnt    : maximum address of the block being processed
    width_runlength : width of runlength value that can be stored
    limit           : value of maximum runlength value
    width_depth     : width of the FIFO Bus

    """

    assert isinstance(datastream, DataStream)
    assert isinstance(bufferdatabus, BufferDataBus)
    assert isinstance(rleconfig, RLEConfig)

    # width of input data
    width_data = len(datastream.data_in)

    # width of the address register
    width_addr = len(datastream.read_addr)

    # width of register to store amplitude size
    width_size = len(bufferdatabus.size)

    # width to store the runlength value
    width_runlength = len(bufferdatabus.runlength)

    # maximum address of block
    max_addr_cnt = int((2**(width_addr)) - 1)

    # depth of the FIFO
    width_depth = max_addr_cnt + 1

    # Signals used to temporarily process data
    rlesymbols_temp = RLESymbols(
        width_data, width_size, width_runlength)
    assert isinstance(rlesymbols_temp, RLESymbols)

    # maximum number of zeroes that can be count
    limit = int((2**width_runlength) - 1)

    # width of data to be stored in rle double fifo
    width_dbuf_data = width_data + width_size + width_runlength

    # instantiation of double buffer bus
    dfifo = FIFOBus(width_dbuf_data)
    assert isinstance(dfifo, FIFOBus)

    buffer_sel = Signal(bool(0))

    # maximum number of pixels that can be processes for one time
    wr_cnt = Signal(modbv(0)[width_addr:])

    @always_comb
    def assign0():
        """assign data to the output bus"""

        buffer_sel.next = bufferdatabus.buffer_sel
        dfifo.read.next = bufferdatabus.read_enable
        bufferdatabus.fifo_empty.next = dfifo.empty

    @always_comb
    def assign1():
        """runlength, size and amplitude read from double buffer"""

        bufferdatabus.runlength.next = dfifo.read_data[(
            width_data+width_size+width_runlength):(
            width_data+width_size)]

        bufferdatabus.size.next = dfifo.read_data[(
            width_data+width_size):width_data]

        bufferdatabus.amplitude.next = dfifo.read_data[width_data:0].signed()

    # send the inputdata into rle core
    rle_core = rle(clock, reset, datastream, rlesymbols_temp, rleconfig)

    # write the processed data to rle double fifo
    rle_doublefifo = doublefifo(
        clock, reset, dfifo, buffer_sel, depth=width_depth)

    @always_comb
    def assign3():
        """write data into the FIFO Bus"""

        dfifo.write_data.next = concat(
            rlesymbols_temp.runlength, rlesymbols_temp.size,
            rlesymbols_temp.amplitude)

        dfifo.write.next = rlesymbols_temp.dovalid

    @always_seq(clock.posedge, reset=reset)
    def seq1():
        """process the block using rlecore"""

        rleconfig.ready.next = False
        if rleconfig.start:
            wr_cnt.next = 0

        # select the data to be written
        if rlesymbols_temp.dovalid:
            if (rlesymbols_temp.runlength == limit) and (
                    rlesymbols_temp.size == 0):

                wr_cnt.next = wr_cnt + limit + 1

            else:
                wr_cnt.next = wr_cnt + 1 + rlesymbols_temp.runlength

            if dfifo.write_data == 0 and wr_cnt != 0:
                rleconfig.ready.next = True
            else:
                if (wr_cnt + rlesymbols_temp.runlength) == max_addr_cnt:
                    rleconfig.ready.next = True

    @always_seq(clock.posedge, reset=reset)
    def assign3_buf():
        if rleconfig.start:
            datastream.buffer_sel.next = not datastream.buffer_sel

    @always_comb
    def assign4():
        """output data valid signal generation"""
        bufferdatabus.dovalid.next = bufferdatabus.read_enable

    return (assign0, assign1, rle_core, rle_doublefifo,
            assign3, seq1, assign3_buf, assign4)


def bench_rle_conversion():
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=1, async=True)

        # width of input data
    width_data = 12

        # width of address bus
    width_addr = 6

        # width to store the size
    width_size = width_data.bit_length()
    width_runlength = 4

        # input data bus for rle module
    datastream = DataStream(width_data, width_addr)
    assert isinstance(datastream, DataStream)

        # connections between output symbols
    bufferdatabus = BufferDataBus(width_data, width_size, width_runlength)
    assert isinstance(bufferdatabus, BufferDataBus)

        # selects the color component, manages address values
    rleconfig = RLEConfig()
    assert isinstance(rleconfig, RLEConfig)

    inst = rlencoder(clock, reset, datastream, bufferdatabus, rleconfig)

    inst.convert('verilog')

if __name__ == "__main__":
    bench_rle_conversion()