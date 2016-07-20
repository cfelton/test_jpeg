"""
This module is MyHDL implementation
of Byte Stuffer used for JPEG Encoder
"""

from myhdl import always_seq, always_comb
from myhdl import Signal, concat, intbv, block


class BSInputDataStream(object):
    """
    Input interface for the Byte Stuffer

    data_in    : Input data to Byte Stuffer
    read       : read signal sent to input FIFO
    fifo_empty : asserts if input FIFO is empty
    """
    def __init__(self, width_data):
        self.data_in = Signal(intbv(0)[width_data:])
        self.read = Signal(bool(0))
        self.fifo_empty = Signal(bool(0))


class BScntrl(object):
    """
    Control Interface for Byte Stuffer

    sof   : start of frame
    start : send input frame when start asserts
    ready : ready to access next frame
    """
    def __init__(self):
        self.start = Signal(bool(0))
        self.ready = Signal(bool(0))
        self.sof = Signal(bool(0))


class BSOutputDataStream(object):
    """
    Output Interface for the Byte Stuffer

    byte       : output byte from the Byte Stuffer
    addr       : output address to the RAM
    data_valid : asserts when output data is valid
    """
    def __init__(self, width_data, width_addr_out):
        self.byte = Signal(intbv(0)[width_data:])
        self.addr = Signal(intbv(0)[width_addr_out:])
        self.data_valid = Signal(bool(0))


@block
def bytestuffer(
        clock, reset, bs_in_stream, bs_out_stream, bs_cntrl, num_enc_bytes):
    """Byte stuffer checks for 0xFF byte and adds a 0xFF00 Byte

    Constants:
    width_addr_out : maximum adress width of the output RAM
    width_out : width of the data in the ouput RAM

    Args :
    bs_in_stream : input interface to the byte stuffer
    bs_cntrl : control interface to the byte stuffer

    Returns:
    bs_out_stream : output interface to the byte stuffer
    num_enc_byte : number of bytes encoded to output RAM
    """

    assert isinstance(bs_in_stream, BSInputDataStream)
    assert isinstance(bs_out_stream, BSOutputDataStream)
    assert isinstance(bs_cntrl, BScntrl)

    # maximum address width of output RAM
    width_addr_out = len(bs_out_stream.addr)
    # maximum width of the output data
    width_out = len(bs_out_stream.byte)

    # temporary latch used to store byte
    latch_byte = Signal(intbv(0)[width_out:])
    read_in_temp = Signal(bool(0))
    # pointer to write address to output RAM
    write_addr = Signal(intbv(0)[width_addr_out:])
    # used to validate data after four clocks
    data_val = Signal(intbv(0)[4:])
    # used to read data
    read_enable = Signal(bool(0))
    read_enable_temp = Signal(bool(0))
    data_valid = Signal(bool(0))
    # wait signal used to handle sedning data
    wait_ndata = Signal(bool(0))
    # it gets a value two when it encounter 0xFF
    wr_cnt_stuff = Signal(intbv(0)[2:])
    # used to store 0xFF00 byte or processed bytes
    wdata_reg = Signal(intbv(0)[(2*width_out):])

    @always_comb
    def assign():
        """assign read signal to interface"""
        bs_in_stream.read.next = read_in_temp

    @always_seq(clock.posedge, reset=reset)
    def control_bs():
        """control sending data into the byte stuffer"""
        read_in_temp.next = False
        bs_cntrl.ready.next = False
        data_val.next = concat(data_val[3:0], read_in_temp)
        read_enable_temp.next = read_enable
        bs_out_stream.data_valid.next = False
        data_valid.next = False

        # enable reading inputs
        if bs_cntrl.start:
            read_enable.next = True

        # read fifo till it becomes empty
        # wait till last byte is read

        if read_enable_temp and not wait_ndata:
            # fifo is empty or when all the inputs processed
            if bs_in_stream.fifo_empty:
                read_enable.next = False
                read_enable_temp.next = False
                bs_cntrl.ready.next = True

            else:
                read_in_temp.next = True
                wait_ndata.next = True

        # show ahead fifo, capture data early
        if read_in_temp:
            # store the input data in latch
            latch_byte.next = bs_in_stream.data_in
            data_valid.next = True

        # send the next input from FIFO
        if data_val[1]:
            wait_ndata.next = False

        # data from FIFO is valid
        if data_valid:
            # stuffing required
            if latch_byte == 0xFF:
                wr_cnt_stuff.next = 0b10
                wdata_reg.next = 0xFF00
            # stuffing not required
            else:
                wr_cnt_stuff.next = 0b01
                wdata_reg.next = latch_byte

        # restore the value of wr_cnt_stuff and validate o/p signals
        if wr_cnt_stuff > 0:
            wr_cnt_stuff.next = wr_cnt_stuff - 1
            bs_out_stream.data_valid.next = True
            write_addr.next = write_addr + 1

        # delayed to make address post-increment
        bs_out_stream.addr.next = write_addr

        #stuffing
        if wr_cnt_stuff == 2:
            bs_out_stream.byte.next = wdata_reg[16:8]
        else:
            bs_out_stream.byte.next = wdata_reg[8:0]

        # start of frame signal
        if bs_cntrl.sof:
            write_addr.next = 0

    @always_seq(clock.posedge, reset=reset)
    def num_bytes():
        """calulate the number of output bytes written"""

        # the plus 2 bytes are for EOI marker
        num_enc_bytes.next = write_addr + 2

    return assign, control_bs, num_bytes
