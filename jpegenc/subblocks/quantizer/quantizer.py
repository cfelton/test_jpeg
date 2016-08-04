"""The above module is the hardware implementation
    of quantizer top module"""

from myhdl import always_seq, block, always_comb
from myhdl import Signal, concat, modbv, intbv
from .ramz import ramz
from .quantizer_core import quantizer_core, QuantDataStream


class QuantIODataStream(object):
    """
    Input datastream into the Quantizer top module

    data_in : send input data into the module
    read_addr : read the data from the input buffer

    """
    def __init__(self, width_data=12, width_addr=6):
        self.data = Signal(intbv(0)[width_data:].signed())
        self.addr = Signal(modbv(0)[width_addr:])
        self.buffer_sel = Signal(bool(0))


class QuantCtrl(object):
    """
    Control Signals used for quantizer top module

    start : signal used to start the processing of block
    ready : asserts when block is ready to take next input
    color_components : select Y1 or Y2 or Cb or Cr component

    """
    def __init__(self):
        self.start = Signal(bool(0))
        self.ready = Signal(bool(0))
        self.color_component = Signal(intbv(0)[3:])


@block
def quantizer(clock, reset, quanti_datastream,
              quant_ctrl, quanto_datastream):
    """The Quantizer module divides the input
    data and data in the ROM

    Arguments:
    quanti_datastream : Input datastream to the module
    quant_ctrl : control signals to the module

    Returns:
    quanto_datastream : Output datastream from the module

    """

    assert isinstance(quant_ctrl, QuantCtrl)
    assert isinstance(quanto_datastream, QuantIODataStream)
    assert isinstance(quanti_datastream, QuantIODataStream)

    # input and output data width
    width_data = len(quanti_datastream.data)
    # address width input and output RAM
    width_addr = len(quanti_datastream.addr)

    # total number of blocks the module process
    max_block_addr = (2**width_addr) - 1

    # input data to the buffer
    buffer_data = Signal(intbv(0)[width_data:].signed())
    # output data from the buffer
    buffer_q = Signal(intbv(0)[width_data:].signed())
    # buffer write enable signal
    buffer_we = Signal(bool(0))
    # buffer write address
    buffer_waddr = Signal(modbv(0)[width_addr+1:])
    # buffer read addressS
    buffer_raddr = Signal(modbv(0)[width_addr+1:])

    # declare input and output signals for core module
    quant_input_stream_temp = QuantDataStream(width_data)
    assert isinstance(quant_input_stream_temp, QuantDataStream)

    quant_output_stream_temp = QuantDataStream(width_data)
    assert isinstance(quant_output_stream_temp, QuantDataStream)

    # counters used for reading and writing purpose
    write_cnt = Signal(modbv(0)[width_addr:])
    read_cnt = Signal(modbv(0)[width_addr:])
    read_enable_temp = Signal(modbv(0)[width_addr:])
    read_enable = Signal(bool(0))

    @always_comb
    def assign():
        """assign signals to bus interface"""
        quanti_datastream.addr.next = read_cnt
        quanto_datastream.data.next = buffer_q
        quant_input_stream_temp.data.next = quanti_datastream.data
        quant_input_stream_temp.valid.next = read_enable_temp[0]

    # instantiantion of quantizer core
    inst_quant = quantizer_core(
        clock, reset, quant_output_stream_temp,
        quant_input_stream_temp, quant_ctrl.color_component)

    # instantiation of quantizer ram
    inst_buffer = ramz(
        buffer_data, buffer_waddr, buffer_raddr, buffer_we, clock, buffer_q)

    @always_comb
    def assign1():
        """assign quantizer core signals to buffer interface"""
        buffer_data.next = quant_output_stream_temp.data
        buffer_waddr.next = concat(not quanto_datastream.buffer_sel, write_cnt)
        buffer_we.next = quant_output_stream_temp.valid
        buffer_raddr.next = concat(quanto_datastream.buffer_sel, quanto_datastream.addr)

    @always_seq(clock.posedge, reset=reset)
    def rdcnt():
        """pump inputs into the quantizer top module"""
        read_enable_temp.next = concat(
            read_enable_temp[(width_addr-2):0], read_enable)

        # enable read signals when start asserts
        if quant_ctrl.start:
            read_cnt.next = 0
            read_enable.next = True

        # start the read counters when read signals are enabled
        if read_enable:
            if read_cnt == max_block_addr:
                read_cnt.next = 0
                read_enable.next = False
            else:
                read_cnt.next = read_cnt + 1

    @always_seq(clock.posedge, reset=reset)
    def wrcnt():
        """write outputs to output buffer"""
        quant_ctrl.ready.next = False

        # reset write counters when start asserts
        if quant_ctrl.start:
            write_cnt.next = 0

        # start write counters
        if quant_output_stream_temp.valid:
            if write_cnt == max_block_addr:
                write_cnt.next = 0
            else:
                write_cnt.next = write_cnt + 1

            # assert ready signal few cycles before
            if write_cnt == (max_block_addr-3):
                quant_ctrl.ready.next = True

    @always_seq(clock.posedge, reset=reset)
    def buf_sel():
        if quant_ctrl.start:
            quanti_datastream.buffer_sel.next = not quanti_datastream.buffer_sel

    return assign, inst_quant, inst_buffer, assign1, rdcnt, wrcnt, buf_sel
