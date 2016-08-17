"""The above module is the hardware implementation
    of quantizer core module"""

from myhdl import always_seq, block, always_comb
from myhdl import Signal, concat, modbv, intbv
from .divider import divider
from .quant_rom import quant_rom


class QuantDataStream(object):
    """
    Input interface for core module

    data : input data to the quantizer core module
    valid : asserts when input data is valid

    """
    def __init__(self, width_data=12):
        self.data = Signal(intbv(0)[width_data:].signed())
        self.valid = Signal(bool(0))


@block
def quantizer_core(
        clock, reset, quant_output_stream,
        quant_input_stream, color_component):

    """This Module is the core of the Quantizer

    Arguments:
    quant_input_stream : Input stream to the core module
    color_component : used to select specific quantizer tables

    Returns:
    quant_output_stream : Output data stream from the Quantizer

    """

    assert isinstance(quant_output_stream, QuantDataStream)
    assert isinstance(quant_input_stream, QuantDataStream)

    # input and output data width
    width_data = len(quant_input_stream.data)

    # no of pipelined stages in divider
    pipeline_length = 3

    # select cb or cr component
    cbcr_thsld = 2

    # signal used to access ram for Y1 or Y2 component
    romaddr_s = Signal(modbv(0)[(6):])

    # signal used to access ram for Cb or Cr component
    cbcr_romaddr_s = Signal(modbv(0)[7:])

    # output data from quantizer ram
    romdatao_s = Signal(intbv(0)[8:])

    # temporary signals for divider purpose
    data_out_temp = Signal(intbv(0)[width_data:].signed())
    data_in_temp = Signal(intbv(0)[width_data:].signed())
    pipline_reg = Signal(intbv(0)[(pipeline_length+2):])

    # select table used for quantization
    table_select = Signal(bool(0))

    inst_rom = quant_rom(clock, cbcr_romaddr_s, romdatao_s)

    inst_divider = divider(clock, reset, data_in_temp,
                           romdatao_s, data_out_temp,)

    @always_comb
    def assign1():
        """assign signals to output bus"""
        quant_output_stream.data.next = data_out_temp
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
        if quant_input_stream.valid:
            romaddr_s.next = romaddr_s + 1

        pipline_reg.next = concat(
            pipline_reg[(pipeline_length+1):0], quant_input_stream.valid)

        data_in_temp.next = quant_input_stream.data

    @always_comb
    def assign2():
        """assign output valid signal to output bus"""
        quant_output_stream.valid.next = pipline_reg[(pipeline_length+1)]

    return assign1, assign2, addr_inc, tab_sel, inst_divider, inst_rom
