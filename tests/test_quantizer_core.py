"""
This module is the testbench for the divider used in quantizer core module
"""

from myhdl import block, instance, StopSimulation
from myhdl import intbv, ResetSignal, Signal
from myhdl.conversion import verify

from jpegenc.subblocks.quantizer import (QuantDataStream, quantizer_core,
                                         divider_ref,)

from jpegenc.subblocks.rle import Component

from jpegenc.testing import (clock_driver, reset_on_start,
                             pulse_reset,)

from jpegenc.testing import run_testbench
from jpegenc.testing import quant_inputs


def quant_block_process(
        clock, color_component, color, input_q, rom,
        input_interface, output_interface, max_cnt):
    """Processing the block of pixels here"""

    assert isinstance(input_interface, QuantDataStream)
    assert isinstance(output_interface, QuantDataStream)

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
    input_interface.data.next = True

    # send 64 input samples into the quantizer core
    for i in range(max_cnt):
        input_interface.data.next = input_q[i]
        input_interface.valid.next = True
        yield clock.posedge
        input_interface.valid.next = False
        # print the outputs
        if output_interface.valid:
            print("output is %d" % output_interface.data)
            assert list_ouput_ref.pop(0) == output_interface.data

    # de-assert data_valid signal
    input_interface.valid.next = False
    yield clock.posedge

    # print some more outputs
    for i in range(5):
        if output_interface.valid:
            print("output is %d" % output_interface.data)
            assert list_ouput_ref.pop(0) == output_interface.data
        yield clock.posedge


def test_quantizer_core():
    """The functionality of the module is tested here"""

    # clock and reset signals declared here
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=True, async=True)

    # width of the input data
    width_data = 12

    # width of input address
    width_addr = 6

    # bus signals declaration for the module
    quant_output_stream = QuantDataStream(width_data)
    assert isinstance(quant_output_stream, QuantDataStream)

    quant_input_stream = QuantDataStream(width_data)
    assert isinstance(quant_input_stream, QuantDataStream)

    color_component = Signal(intbv(0)[3:])

    max_addr = 2**width_addr

    # component declaration
    component = Component()
    assert isinstance(component, Component)

    @block
    def bench_quant_core():
        """instantiation of quantizer core module and clock signals"""

        inst = quantizer_core(
            clock, reset, quant_output_stream,
            quant_input_stream, color_component)

        inst_clock = clock_driver(clock)

        @instance
        def tbstim():
            """We send the inputs from here"""

            # reset the module before sending inputs
            yield pulse_reset(reset, clock)

            # select Cb or Cr component
            color = component.y2_space

            # process the component selected
            yield quant_block_process(
                clock, color_component, color,
                quant_inputs.quant_in, quant_inputs.quant_rom,
                quant_input_stream, quant_output_stream, max_addr
            )
            yield clock.posedge

            print("====================================")

            # select Y1 or Y2 component
            color = component.cb_space

            # process the component selected
            yield quant_block_process(
                clock, color_component, color,
                quant_inputs.quant_in, quant_inputs.quant_rom,
                quant_input_stream, quant_output_stream, max_addr
            )
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

    # bus signals declaration for the module
    quant_output_stream = QuantDataStream(width_data)
    assert isinstance(quant_output_stream, QuantDataStream)

    quant_input_stream = QuantDataStream(width_data)
    assert isinstance(quant_input_stream, QuantDataStream)

    color_component = Signal(intbv(0)[3:])

    @block
    def bench_quant_core():
        """wrapper used for conversion purpose"""

        # instantiatiom of divider, clock and reset
        inst = quantizer_core(clock, reset, quant_output_stream,
                              quant_input_stream, color_component)

        inst_clock = clock_driver(clock)
        inst_reset = reset_on_start(reset, clock)

        @instance
        def tbstim():
            """dummy tests to convert the module"""
            yield clock.posedge
            print("Conversion done!!")
            raise StopSimulation

        return tbstim, inst, inst_clock, inst_reset

    verify.simulator = 'iverilog'
    assert bench_quant_core().verify_convert() == 0
