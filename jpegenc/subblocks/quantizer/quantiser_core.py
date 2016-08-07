"""The above module is the hardware implementation
    of quantizer core module"""

from myhdl import always_seq, block, always_comb
from myhdl import Signal, concat, modbv, intbv
from .ramz import ramz
from .divider import divider


class QuantInputStream(object):
    """
    Input interface for core module

    data_in : input data to the quantizer core module
    data_valid : asserts when input data is valid

    """
    def __init__(self, width):
        self.data_in = Signal(intbv(0)[width:].signed())
        self.data_valid = Signal(bool(0))


class QuantOutputStream(object):
    """
    Output interface from the core module

    data_out : output data from the core module
    dovalid : asserts when output data is valid

    """
    def __init__(self, width):
        self.data_out = Signal(intbv(0)[width:].signed())
        self.dovalid = Signal(bool(0))


class QuantConfig(object):
    """
    Interface between core module and quantizer ram

    qdata : input quantization table to be stored in ram
    qwaddr : select adress to read/write in quantizer ram
    qwren : used to write enable or diable

    """
    def __init__(self, q_width, q_addr):
        self.qdata = Signal(intbv(0)[q_width:])
        self.qwaddr = Signal(modbv(0)[q_addr:])
        self.qwren = Signal(bool(0))


@block
def quantizer(
        clock, reset, quant_output_stream, quant_input_stream,
        quant_config, color_component):

    """HDL modelling of quantizer core module"""

    assert isinstance(quant_output_stream, QuantOutputStream)
    assert isinstance(quant_input_stream, QuantInputStream)
    assert isinstance(quant_config, QuantConfig)

    # address and data width declared here
    width_io = len(quant_input_stream.data_in)
    width_qdata = len(quant_config.qdata)
    width_qaddr = len(quant_config.qwaddr)

    # no of pipelined stages in divider
    pipeline_length = 3

    # select cb or cr component
    cbcr_thsld = 2

    # signal used to access ram for Y1 or Y2 component
    romaddr_s = Signal(modbv(0)[(width_qaddr-1):])

    # signal used to access ram for Cb or Cr component
    cbcr_romaddr_s = Signal(modbv(0)[width_qaddr:])

    # output data from quantizer ram
    romdatao_s = Signal(intbv(0)[width_qdata:])

    # temporary signals for divider purpose
    data_out_temp = Signal(intbv(0)[width_io:].signed())
    data_in_temp = Signal(intbv(0)[width_io:].signed())
    pipline_reg = Signal(intbv(0)[(pipeline_length+2):])

    # select table used for quantization
    table_select = Signal(bool(0))

    # instantiation of ramz and divider module
    inst_ramz = ramz(
        quant_config.qdata, quant_config.qwaddr,
        cbcr_romaddr_s, quant_config.qwren, clock, romdatao_s)

    inst_divider = divider(
        clock, reset, data_in_temp, romdatao_s, data_out_temp)

    @always_comb
    def assign1():
        """assign signals to output bus"""
        quant_output_stream.data_out.next = data_out_temp
        cbcr_romaddr_s.next = concat(table_select, romaddr_s)

    @always_seq(clock.posedge, reset=reset)
    def tab_sel():
        """select table from ram for quantization"""
        if color_component < cbcr_thsld:
            table_select.next = False
        else:
            table_select.next = True

    @always_seq(clock.posedge, reset=reset)
    def addr_inc():
        """process the inputs with quantization matrix"""
        if quant_input_stream.data_valid:
            romaddr_s.next = romaddr_s + 1

        pipline_reg.next = concat(
            pipline_reg[(pipeline_length+1):0], quant_input_stream.data_valid)

        data_in_temp.next = quant_input_stream.data_in

    @always_comb
    def assign2():
        """assign output valid signal to output bus"""
        quant_output_stream.dovalid.next = pipline_reg[(pipeline_length+1)]

    return assign1, assign2, addr_inc, tab_sel, inst_divider, inst_ramz
