from myhdl import always_seq, always_comb, block
from myhdl import intbv, Signal, concat
from jpegenc.subblocks.RLE.RLECore.rlecore import DataStream, rle
from jpegenc.subblocks.RLE.RLECore.rlecore import RLESymbols, RLEConfig
from jpegenc.subblocks.RLE.RleDoubleFifo.rledoublebuffer import rledoublefifo
from jpegenc.subblocks.RLE.RleDoubleFifo.rledoublebuffer import DoubleFifoBus


class InDataStream(DataStream):
    """
    InputData Interface Class
    ready: module asserts ready if its ready for next block

    start: start signal triggers the module to start
            processing data

    input_val: input to the rle module
    """
    def __init__(self, width):
        super(InDataStream, self).__init__(width)
        self.ready = Signal(bool(0))


class BufferDataBus(RLESymbols):
    """
    Output Interface Class
    Amplitude: amplitude of the number

    size: size required to store amplitude

    runlength: number of zeros

    dovalid: asserts if ouput is valid
    buffer_sel: It selects the buffer in double buffer
    read_enable: enables
    fifo_empty: asserts if any of the two fifos are empty

    """
    def __init__(self, width, size, rlength):
        super(BufferDataBus, self).__init__(width, size, rlength)
        self.buffer_sel = Signal(bool(0))
        self.read_enable = Signal(bool(0))
        self.fifo_empty = Signal(bool(0))


@block
def rletop(
        dfifo_const, constants, reset, clock,
        indatastream, bufferdatabus, rleconfig):
    """The top module connects rle core and rle double buffer"""

    assert isinstance(indatastream, InDataStream)
    assert isinstance(bufferdatabus, BufferDataBus)
    assert isinstance(rleconfig, RLEConfig)

    # Signals used to temporarily process data
    rlesymbols_temp = RLESymbols(
        constants.width_data, constants.size, constants.rlength)

    datastream_temp = DataStream(constants.width_data)

    # maximum number of zeroes that can be count
    limit = int((2**constants.rlength) - 1)

    # width of data to be stored in rle double fifo
    width_dbuf = constants.width_data + constants.size + constants.rlength

    # instantiation of double buffer bus
    dfifo = DoubleFifoBus(width_dbuf)

    # maximum number of pixels that can be processes for one time
    wr_cnt = Signal(intbv(0)[(constants.max_write_cnt + 1):])

    @always_comb
    def assign0():
        dfifo.buffer_sel.next = bufferdatabus.buffer_sel
        dfifo.read_req.next = bufferdatabus.read_enable
        bufferdatabus.fifo_empty.next = dfifo.fifo_empty
        datastream_temp.start.next = indatastream.start

    @always_comb
    def assign1():
        """runlength, size and amplitude read from double buffer"""
        bufferdatabus.runlength.next = dfifo.data_out[(
            constants.width_data+constants.size+constants.rlength):(
            constants.width_data+constants.size)]

        bufferdatabus.size.next = dfifo.data_out[(
            constants.width_data+constants.size):constants.width_data]

        bufferdatabus.amplitude.next = dfifo.data_out[constants.width_data:0].signed()

    # send the inputdata into rle core
    rle_core = rle(
        constants, reset, clock, datastream_temp, rlesymbols_temp, rleconfig)

    @always_comb
    def assign2():
        datastream_temp.input_val.next = indatastream.input_val

    # write the processed data to rle double fifo
    rle_doublefifo = rledoublefifo(dfifo_const, reset, clock, dfifo)

    @always_comb
    def assign3():
        dfifo.data_in.next = concat(
            rlesymbols_temp.runlength, rlesymbols_temp.size,
            rlesymbols_temp.amplitude)

        dfifo.write_enable.next = rlesymbols_temp.dovalid

    @always_seq(clock.posedge, reset=reset)
    def seq1():
        indatastream.ready.next = False
        if indatastream.start:
            wr_cnt.next = 0

        # select the data to be written
        if rlesymbols_temp.dovalid:
            if (rlesymbols_temp.runlength == limit) and (
                    rlesymbols_temp.size == 0):

                wr_cnt.next = wr_cnt + limit + 1

            else:
                wr_cnt.next = wr_cnt + 1 + rlesymbols_temp.runlength

        if dfifo.data_in == 0 and wr_cnt != 0:
            indatastream.ready.next = 1
        else:
            if (wr_cnt + rlesymbols_temp.runlength) == constants.max_write_cnt:
                indatastream.ready.next = True

    @always_comb
    def assign4():
        # output data valid signal
        bufferdatabus.dovalid.next = bufferdatabus.read_enable

    return (assign0, assign1, rle_core, assign2,
            rle_doublefifo, assign3, seq1, assign4)
