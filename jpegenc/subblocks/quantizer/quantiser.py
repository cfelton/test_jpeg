"""The above module is the hardware implementation
    of quantizer top module"""

from myhdl import always_seq, block, always_comb
from myhdl import Signal, concat, modbv, intbv

from .ramz import ramz
from .quantiser_core import (quantizer, QuantOutputStream,
                             QuantInputStream, QuantConfig)


class QuantIDataStream(object):
    """
    Input datastream into the Quantizer top module

    data_in : send input data into the module
    read_addr : read the data from the input buffer

    """
    def __init__(self, width, addr):
        self.data_in = Signal(intbv(0)[width:].signed())
        self.read_addr = Signal(modbv(0)[addr:])


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


class QuantODataStream(object):
    """
    Output data stream from quantizer module

    data_out : output data sent from the output buffer
    read_addr : read data from the output buffer

    """
    def __init__(self, width, addr):
        self.data_out = Signal(intbv(0)[width:].signed())
        self.read_addr = Signal(modbv(0)[addr:])


@block
def quantizer_top(
        clock, reset, quanti_datastream,
        quant_ctrl, quant_config, quanto_datastream):
    """HDL modeling of top module"""

    assert isinstance(quant_ctrl, QuantCtrl)
    assert isinstance(quanto_datastream, QuantODataStream)
    assert isinstance(quanti_datastream, QuantIDataStream)
    assert isinstance(quant_config, QuantConfig)

    # address length and data length declared here
    width_len = len(quanti_datastream.data_in)
    width_addr = len(quanti_datastream.read_addr)
    max_block_addr = (2**width_addr) - 1

    # declare signals used for output buffer
    buffer_data = Signal(intbv(0)[width_len:].signed())
    buffer_q = Signal(intbv(0)[width_len:].signed())
    buffer_we = Signal(bool(0))
    buffer_waddr = Signal(modbv(0)[width_addr:])
    buffer_raddr = Signal(modbv(0)[width_addr:])

    # declare input and output signals for core module
    quant_input_stream_temp = QuantInputStream(width_len)
    assert isinstance(quant_input_stream_temp, QuantInputStream)

    quant_output_stream_temp = QuantOutputStream(width_len)
    assert isinstance(quant_output_stream_temp, QuantOutputStream)

    # counters used for reading and writing purpose
    write_cnt = Signal(modbv(0)[width_addr:])
    read_cnt = Signal(modbv(0)[width_addr:])
    read_enable_temp = Signal(modbv(0)[width_addr:])
    read_enable = Signal(bool(0))

    @always_comb
    def assign():
        """assign signals to bus interface"""
        quanti_datastream.read_addr.next = read_cnt
        quanto_datastream.data_out.next = buffer_q
        quant_input_stream_temp.data_in.next = quanti_datastream.data_in
        quant_input_stream_temp.data_valid.next = read_enable_temp[0]

    # instantiantion of quantizer core
    inst_quant = quantizer(
        clock, reset, quant_output_stream_temp,
        quant_input_stream_temp, quant_config,
        quant_ctrl.color_component)

    # instantiation of quantizer ram
    inst_buffer = ramz(
        buffer_data, buffer_waddr, buffer_raddr, buffer_we, clock, buffer_q)

    @always_comb
    def assign1():
        """assign quantizer core signals to buffer interface"""
        buffer_data.next = quant_output_stream_temp.data_out
        buffer_waddr.next = write_cnt
        buffer_we.next = quant_output_stream_temp.dovalid
        buffer_raddr.next = quanto_datastream.read_addr

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
        if quant_output_stream_temp.dovalid:
            if write_cnt == max_block_addr:
                write_cnt.next = 0
            else:
                write_cnt.next = write_cnt + 1

            # assert ready signal few cycles before
            if write_cnt == (max_block_addr-3):
                quant_ctrl.ready.next = True

    return assign, inst_quant, inst_buffer, assign1, rdcnt, wrcnt
