"""This module is the testbench for
    the Quantiser top module"""

from myhdl import block, instance
from myhdl import ResetSignal, Signal, StopSimulation
from myhdl.conversion import verify

from jpegenc.subblocks.quantizer import (QuantIDataStream, QuantConfig,
                                         divider_ref, QuantODataStream,
                                         QuantCtrl, quantizer_top,)

from jpegenc.subblocks.rle import Component

from jpegenc.testing import (clock_driver, reset_on_start,
                             pulse_reset, toggle_signal,)

from jpegenc.testing import run_testbench

from quant_test_inputs import quant_rom, quant_in


def quant_top_block_process(
        clock, control_unit, color, output_interface,
        input_interface, input_val, rom, max_addr):
    """Processing the block of pixels here"""

    # select which component to be processes
    control_unit.color_component.next = color
    yield clock.posedge

    # select the table for quantisation
    if control_unit.color_component < 2:
        table = 0
    else:
        table = 1

    # calculate the reference values for the input
    list_ouput_ref = []
    for i in range(max_addr):
        result = divider_ref(input_val[i], rom[i + (max_addr*table)])
        list_ouput_ref.append(int(result))

    # start processing of block
    yield toggle_signal(control_unit.start, clock)

    # send 64 inputs into the module
    # store 64 inputs into the buffer
    for i in range(max_addr):
        input_interface.data_in.next = input_val[i]
        input_interface.read_addr.next = i
        yield clock.posedge

    # output data from the buffer and print them
    for i in range(max_addr):
        output_interface.read_addr.next = i
        if i >= 2:
            print (" output data is %d" % (output_interface.data_out))
            assert list_ouput_ref.pop(0) == output_interface.data_out
        yield clock.posedge

    # print left outputs
    print (" output data is %d" % (output_interface.data_out))
    assert list_ouput_ref.pop(0) == output_interface.data_out
    yield clock.posedge

    # print left outputs
    print (" output data is %d" % (output_interface.data_out))
    assert list_ouput_ref.pop(0) == output_interface.data_out


def test_quantiser():
    """The functionality of the module is tested here"""

    # declare clock and reset
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=True, async=True)

    # width of the input data
    width_data = 12

    # width of the address used for Dual Port RAM
    width_qaddr = 7

    # width of data stored in DualPortRAM
    width_qdata = 8

    # width of input address
    width_addr = 6

    # bus declaration for the module
    quanto_datastream = QuantODataStream(width_data, width_addr)
    assert isinstance(quanto_datastream, QuantODataStream)

    quanti_datastream = QuantIDataStream(width_data, width_addr)
    assert isinstance(quanti_datastream, QuantIDataStream)

    quant_config = QuantConfig(width_qdata, width_qaddr)
    assert isinstance(quant_config, QuantConfig)

    quant_ctrl = QuantCtrl()
    assert isinstance(quant_ctrl, QuantCtrl)

    # declare constants
    max_addr_quant = 2**width_qaddr
    max_addr = 2**width_addr

    component = Component()
    assert isinstance(component, Component)

    @block
    def bench_quant():
        """instantiation of quantizer module and clock"""
        inst = quantizer_top(
            clock, reset, quanti_datastream,
            quant_ctrl, quant_config, quanto_datastream)

        inst_clock = clock_driver(clock)

        @instance
        def tbstim():
            """we send test cases here"""

            # reset the block before processing
            yield pulse_reset(reset, clock)

            # enable writing in the quantizer ram
            quant_config.qwren.next = True
            yield clock.posedge

            # filling the quantizer ram with quantizer rom
            for i in range(max_addr_quant):
                quant_config.qdata.next = quant_rom[i]
                quant_config.qwaddr.next = i
                yield clock.posedge

            # disable writing in the quantizer ram
            quant_config.qwren.next = False
            yield clock.posedge

            # select Cb or Cr component
            color = component.y2_space

            # process Cb or Cr component
            yield quant_top_block_process(
                clock, quant_ctrl, color, quanto_datastream,
                quanti_datastream, quant_in, quant_rom, max_addr)

            print ("===============================================")

            # select Y1 or Y2 component
            color = component.cr_space

            # process Cb or Cr component
            yield quant_top_block_process(
                clock, quant_ctrl, color, quanto_datastream,
                quanti_datastream, quant_in, quant_rom, max_addr)

            raise StopSimulation

        return tbstim, inst, inst_clock

    run_testbench(bench_quant)


def test_quant_conversion():
    """Test bench used for conversion purpose"""

    # clock, reset signals declared
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=True, async=True)

    # width of the input data
    width_data = 12

    # width of the address used for Dual Port RAM
    width_qaddr = 7

    # width of data stored in DualPortRAM
    width_qdata = 8

    # width of input address
    width_addr = 6

    # bus declaration for the module
    quanto_datastream = QuantODataStream(width_data, width_addr)
    assert isinstance(quanto_datastream, QuantODataStream)

    quanti_datastream = QuantIDataStream(width_data, width_addr)
    assert isinstance(quanti_datastream, QuantIDataStream)

    quant_config = QuantConfig(width_qdata, width_qaddr)
    assert isinstance(quant_config, QuantConfig)

    quant_ctrl = QuantCtrl()
    assert isinstance(quant_ctrl, QuantCtrl)

    @block
    def bench_quant_top_core():
        """wrapper used for conversion purpose"""

        # instantiatiom of quantizer, clock and reset
        inst = quantizer_top(
            clock, reset, quanti_datastream,
            quant_ctrl, quant_config, quanto_datastream)

        inst_clock = clock_driver(clock)
        inst_reset = reset_on_start(reset, clock)

        @instance
        def tbstim():
            """dummy tests to convert the module"""
            yield clock.posedge
            print ("Conversion done!!")
            raise StopSimulation

        return tbstim, inst, inst_clock, inst_reset

    verify.simulator = 'iverilog'
    assert bench_quant_top_core().verify_convert() == 0

test_quantiser()
test_quant_conversion()
