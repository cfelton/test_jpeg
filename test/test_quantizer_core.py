"""This module is the testbench for the
    divider used in Quantiser core module"""

from myhdl import block, instance, StopSimulation
from myhdl import intbv, ResetSignal, Signal
from myhdl.conversion import verify

from jpegenc.subblocks.quantizer import (QuantInputStream, QuantConfig,
                                         QuantOutputStream, quantizer,
                                         divider_ref,)

from jpegenc.subblocks.rle import Component

from jpegenc.testing import (clock_driver, reset_on_start,
                             pulse_reset,)

from jpegenc.testing import run_testbench

from quant_test_inputs import quant_rom, quant_in


def quant_block_process(
        clock, color_component, color, input_q, rom,
        input_interface, output_interface, max_cnt):
    """Processing the block of pixels here"""

    assert isinstance(input_interface, QuantInputStream)
    assert isinstance(output_interface, QuantOutputStream)

    # select Y1 or Y2 or Cb or Cr
    color_component.next = color
    yield clock.posedge

    # select the table for quantization
    if color_component < 2:
        table = 0
    else:
        table = 1

    # calculate the reference values for the input
    list_ouput_ref = []
    for i in range(max_cnt):
        result = divider_ref(input_q[i], rom[i + (max_cnt*table)])
        list_ouput_ref.append(int(result))

    # assert input valid signal
    input_interface.data_valid.next = True

    # send 64 input samples into the quantizer core
    for i in range(max_cnt):
        input_interface.data_in.next = input_q[i]
        yield clock.posedge
        # print the outputs
        if output_interface.dovalid:
            print ("output is %d" % output_interface.data_out)
            assert list_ouput_ref.pop(0) == output_interface.data_out

    # de-assert data_valid signal
    input_interface.data_valid.next = False
    yield clock.posedge

    # print some more outputs
    for i in range(5):
        if output_interface.dovalid:
            print ("output is %d" % output_interface.data_out)
            assert list_ouput_ref.pop(0) == output_interface.data_out
        yield clock.posedge


def test_quantiser_core():
    """The functionality of the module is tested here"""

    # clock and reset signals declared here
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

    # bus signals declaration for the module
    quant_output_stream = QuantOutputStream(width_data)
    assert isinstance(quant_output_stream, QuantOutputStream)

    quant_input_stream = QuantInputStream(width_data)
    assert isinstance(quant_input_stream, QuantInputStream)

    quant_config = QuantConfig(width_qdata, width_qaddr)
    assert isinstance(quant_config, QuantConfig)

    color_component = Signal(intbv(0)[3:])

    # maximum quantization address
    max_quant_addr = 2**width_qaddr

    max_addr = 2**width_addr

    # component declaration
    component = Component()
    assert isinstance(component, Component)

    @block
    def bench_quant_core():
        """instantiation of quantizer core module and clock signals"""

        inst = quantizer(
            clock, reset, quant_output_stream,
            quant_input_stream, quant_config, color_component)

        inst_clock = clock_driver(clock)

        @instance
        def tbstim():
            """We send the inputs from here"""

            # reset the module before sending inputs
            yield pulse_reset(reset, clock)

            # write enable the quantizer ram
            quant_config.qwren.next = True
            yield clock.posedge

            # fill the quantizer ram with quantization values
            for i in range(max_quant_addr):
                quant_config.qdata.next = quant_rom[i]
                quant_config.qwaddr.next = i
                yield clock.posedge

            # write disable the quantizer ram
            quant_config.qwren.next = False
            yield clock.posedge

            # select Cb or Cr component
            color = component.y2_space

            # process the component selected
            yield quant_block_process(
                clock, color_component, color, quant_in, quant_rom,
                quant_input_stream, quant_output_stream, max_addr)
            yield clock.posedge

            print ("====================================")

            # select Y1 or Y2 component
            color = component.cb_space

            # process the component selected
            yield quant_block_process(
                clock, color_component, color, quant_in, quant_rom,
                quant_input_stream, quant_output_stream, max_addr)
            yield clock.posedge

            raise StopSimulation

        return tbstim, inst, inst_clock

    run_testbench(bench_quant_core)


def test_block_conversion():
    """Test bench used for conversion purpose"""

    clock = Signal(bool(0))
    reset = ResetSignal(0, active=True, async=True)

    # width of the input data
    width_data = 12

    # width of the address used for Dual Port RAM
    width_qaddr = 7

    # width of data stored in DualPortRAM
    width_qdata = 8

    # bus signals declaration for the module
    quant_output_stream = QuantOutputStream(width_data)
    assert isinstance(quant_output_stream, QuantOutputStream)

    quant_input_stream = QuantInputStream(width_data)
    assert isinstance(quant_input_stream, QuantInputStream)

    quant_config = QuantConfig(width_qdata, width_qaddr)
    assert isinstance(quant_config, QuantConfig)

    color_component = Signal(intbv(0)[3:])

    @block
    def bench_quant_core():
        """wrapper used for conversion purpose"""

        # instantiatiom of divider, clock and reset
        inst = quantizer(
            clock, reset, quant_output_stream,
            quant_input_stream, quant_config, color_component)

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
    assert bench_quant_core().verify_convert() == 0
test_quantiser_core()
test_block_conversion()
