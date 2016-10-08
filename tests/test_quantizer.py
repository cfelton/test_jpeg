"""
This module is the testbench for the Quantizer top module
"""

from myhdl import block, instance
from myhdl import ResetSignal, Signal, StopSimulation
from myhdl.conversion import verify

from jpegenc.subblocks.quantizer import (QuantIODataStream, divider_ref,
                                         QuantCtrl, quantizer,)

from jpegenc.subblocks.rle import Component

from jpegenc.testing import (clock_driver, reset_on_start,
                             pulse_reset, toggle_signal,)

from jpegenc.testing import run_testbench
from jpegenc.testing import quant_inputs


def quant_top_block_process(
        clock, control_unit, color, output_interface,
        input_interface, input_val, rom, max_addr, buffer_sel):
    """Processing the block of pixels here"""

    assert isinstance(input_interface, QuantIODataStream)
    assert isinstance(output_interface, QuantIODataStream)
    assert isinstance(control_unit, QuantCtrl)

    # select which component to be processes
    control_unit.color_component.next = color
    yield clock.posedge

    # select the table for quantization
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
        input_interface.data.next = input_val[i]
        input_interface.addr.next = buffer_sel*64 + i
        yield clock.posedge

    # output data from the buffer and print them
    for i in range(max_addr):
        output_interface.addr.next = i
        if i >= 2:
            print(" output data is %d" % (output_interface.data,))
            # assert list_ouput_ref.pop(0) == output_interface.data
        yield clock.posedge

    # print left outputs
    print(" output data is %d" % (output_interface.data,))
    # assert list_ouput_ref.pop(0) == output_interface.data
    yield clock.posedge

    # print left outputs
    print(" output data is %d" % (output_interface.data,))
    # assert list_ouput_ref.pop(0) == output_interface.data


def test_quantizer():
    """The functionality of the module is tested here"""

    # declare clock and reset
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=True, async=True)

    # width of the input data
    width_data = 12

    # width of input address
    width_addr = 6

    # bus declaration for the module
    quanto_datastream = QuantIODataStream(width_data, width_addr)
    assert isinstance(quanto_datastream, QuantIODataStream)

    quanti_datastream = QuantIODataStream(width_data, width_addr)
    assert isinstance(quanti_datastream, QuantIODataStream)

    quant_ctrl = QuantCtrl()
    assert isinstance(quant_ctrl, QuantCtrl)

    # declare constants
    max_addr = 2**width_addr

    component = Component()
    assert isinstance(component, Component)

    @block
    def bench_quant():
        """instantiation of quantizer module and clock"""
        inst = quantizer(clock, reset, quanti_datastream,
                         quant_ctrl, quanto_datastream)

        inst_clock = clock_driver(clock)

        @instance
        def tbstim():
            """we send test cases here"""

            # reset the block before processing
            yield pulse_reset(reset, clock)

            # select Cb or Cr component
            color = component.y2_space

            # process Cb or Cr component
            yield quant_top_block_process(
                clock, quant_ctrl, color, quanto_datastream, quanti_datastream,
                quant_inputs.quant_in, quant_inputs.quant_rom, max_addr, 1
            )

            print("===============================================")

            # select Y1 or Y2 component
            color = component.cr_space

            # process Cb or Cr component
            yield quant_top_block_process(
                clock, quant_ctrl, color, quanto_datastream, quanti_datastream,
                quant_inputs.quant_in, quant_inputs.quant_rom, max_addr, 1
            )

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
    width_addr = 6

    # bus declaration for the module
    quanto_datastream = QuantIODataStream(width_data, width_addr)
    assert isinstance(quanto_datastream, QuantIODataStream)

    quanti_datastream = QuantIODataStream(width_data, width_addr)
    assert isinstance(quanti_datastream, QuantIODataStream)

    quant_ctrl = QuantCtrl()
    assert isinstance(quant_ctrl, QuantCtrl)

    @block
    def bench_quant_top_core():
        """wrapper used for conversion purpose"""

        # instantiatiom of quantizer, clock and reset
        inst = quantizer(clock, reset, quanti_datastream,
                         quant_ctrl, quanto_datastream)

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
    assert bench_quant_top_core().verify_convert() == 0

if __name__ == "__main__":
    test_quantizer()
    test_quant_conversion()
