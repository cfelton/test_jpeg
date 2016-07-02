"""This module is the testbench for the
    divider used in Quantiser core module"""

from myhdl import block, instance, StopSimulation
from myhdl import intbv, ResetSignal, Signal
from myhdl.conversion import verify

from jpegenc.subblocks.quantizer.quantiser_core import quantizer, Component
from jpegenc.subblocks.quantizer.quantiser_core import QuantInputStream
from jpegenc.subblocks.quantizer.quantiser_core import QuantOutputStream
from jpegenc.subblocks.quantizer.quantiser_core import QuantConfig

from common import tbclock, resetonstart
from common import divider_ref, reset_on_start

from testcases import quant_rom, quant_in


def quant_block_process(
    clock, color_component, color, input_q,
    rom, quant_input_stream, quant_output_stream, max_addr):
    """Processing the block of pixels here"""

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
    for i in range(max_addr):
        result = divider_ref(input_q[i], rom[i + (max_addr*table)])
        list_ouput_ref.append(int(result))

    # assert input valid signal
    quant_input_stream.data_valid.next = True

    # send 64 input samples into the quantizer core
    for i in range(max_addr):
        quant_input_stream.data_in.next = input_q[i]
        yield clock.posedge
        # print the outputs
        if quant_output_stream.dovalid:
            print ("output is %d" % quant_output_stream.data_out)
            assert list_ouput_ref.pop(0) == quant_output_stream.data_out

    # de-assert data_valid signal
    quant_input_stream.data_valid.next = False
    yield clock.posedge

    # print some more outputs
    if quant_output_stream.dovalid:
        print ("output is %d" % quant_output_stream.data_out)
        assert list_ouput_ref.pop(0) == quant_output_stream.data_out
    yield clock.posedge

    # print some more outputs
    if quant_output_stream.dovalid:
        print ("output is %d" % quant_output_stream.data_out)
        assert list_ouput_ref.pop(0) == quant_output_stream.data_out
    yield clock.posedge

    # print some more outputs
    if quant_output_stream.dovalid:
        print ("output is %d" % quant_output_stream.data_out)
        assert list_ouput_ref.pop(0) == quant_output_stream.data_out
    yield clock.posedge

    # print some more outputs
    if quant_output_stream.dovalid:
        print ("output is %d" % quant_output_stream.data_out)
        assert list_ouput_ref.pop(0) == quant_output_stream.data_out
    yield clock.posedge

    # print some more outputs
    if quant_output_stream.dovalid:
        print ("output is %d" % quant_output_stream.data_out)
        assert list_ouput_ref.pop(0) == quant_output_stream.data_out

def test_quantiser_core():
    """The functionality of the module is tested here"""

    # clock and reset signals declared here
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=True, async=True)

    # bus signals declaration for the module
    quant_output_stream = QuantOutputStream(12)
    quant_input_stream = QuantInputStream(12)
    quant_config = QuantConfig(8, 7)

    # maximum quantization address
    max_quant_addr = 2**len(quant_config.qwaddr)
    color_component = Signal(intbv(0)[3:])

    max_addr = 64
    # component declaration
    component = Component()

    @block
    def bench_quant_core():
        """instantiation of quantizer core module and clock signals"""

        inst = quantizer(
            reset, clock, quant_output_stream,
            quant_input_stream, quant_config, color_component)

        inst_clock = tbclock(clock)

        @instance
        def tbstim():
            """We send the inputs from here"""

            # reset the module before sending inputs
            yield reset_on_start(clock, reset)

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
            color = component.Y2

            # process the component selected
            yield quant_block_process(
                clock, color_component, color, quant_in, quant_rom,
                quant_input_stream, quant_output_stream, max_addr)
            yield clock.posedge

            print ("====================================")

            # select Y1 or Y2 component
            color = component.Cb

            # process the component selected
            yield quant_block_process(
                clock, color_component, color, quant_in, quant_rom,
                quant_input_stream, quant_output_stream, max_addr)
            yield clock.posedge

            raise StopSimulation

        return tbstim, inst, inst_clock

    inst1 = bench_quant_core()
    inst1.config_sim(trace=False)
    inst1.run_sim()

def test_block_conversion():
    """Test bench used for conversion purpose"""

    clock = Signal(bool(0))
    reset = ResetSignal(0, active=True, async=True)
    quant_output_stream = QuantOutputStream(12)
    quant_input_stream = QuantInputStream(12)
    quant_config = QuantConfig(8, 7)
    color_component = Signal(intbv(0)[3:])


    @block
    def bench_quant_core():
        """wrapper used for conversion purpose"""

        # instantiatiom of divider, clock and reset
        inst = quantizer(
            reset, clock, quant_output_stream,
            quant_input_stream, quant_config, color_component)

        inst_clock = tbclock(clock)
        inst_reset = resetonstart(clock, reset)

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
