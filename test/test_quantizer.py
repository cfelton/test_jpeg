"""This module is the testbench for
    the Quantiser top module"""

from myhdl import block, instance
from myhdl import ResetSignal, Signal, StopSimulation
from myhdl.conversion import verify

from jpegenc.subblocks.quantizer.quantiser import quantizer_top
from jpegenc.subblocks.quantizer.quantiser import QuantIDataStream
from jpegenc.subblocks.quantizer.quantiser import QuantODataStream, QuantCtrl
from jpegenc.subblocks.quantizer.quantiser_core import QuantConfig
from jpegenc.subblocks.quantizer.quantiser_core import Component

from common import tbclock, resetonstart, reset_on_start
from common import divider_ref, start_of_block

from testcases import quant_rom, quant_in


def quant_top_block_process(
        clock, quant_ctrl, color, quanto_datastream,
        quanti_datastream, input_val, rom, max_addr):
    """Processing the block of pixels here"""

    # select which component to be processes
    quant_ctrl.color_component.next = color
    yield clock.posedge

    # select the table for quantisation
    if quant_ctrl.color_component < 2:
        table = 0
    else:
        table = 1

    # calculate the reference values for the input
    list_ouput_ref = []
    for i in range(max_addr):
        result = divider_ref(input_val[i], rom[i + (max_addr*table)])
        list_ouput_ref.append(int(result))

    # start processing of block
    yield start_of_block(clock, quant_ctrl.start)

    # send 64 inputs into the module
    # store 64 inputs into the buffer
    for i in range(max_addr):
        quanti_datastream.data_in.next = input_val[i]
        quanti_datastream.read_addr.next = i
        yield clock.posedge

    # output data from the buffer and print them
    for i in range(max_addr):
        quanto_datastream.read_addr.next = i
        if i >= 2:
            print (" output data is %d" % (quanto_datastream.data_out))
            assert list_ouput_ref.pop(0) == quanto_datastream.data_out
        yield clock.posedge

    # print left outputs
    print (" output data is %d" % (quanto_datastream.data_out))
    assert list_ouput_ref.pop(0) == quanto_datastream.data_out
    yield clock.posedge

    # print left outputs
    print (" output data is %d" % (quanto_datastream.data_out))
    assert list_ouput_ref.pop(0) == quanto_datastream.data_out


def test_quantiser():
    """The functionality of the module is tested here"""

    # declare clock and reset
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=True, async=True)

    # bus declaration for the module
    quanto_datastream = QuantODataStream(12, 6)
    quanti_datastream = QuantIDataStream(12, 6)
    quant_config = QuantConfig(8, 7)
    quant_ctrl = QuantCtrl()

    # declare constants
    max_addr_quant = 2**len(quant_config.qwaddr)
    max_addr = 2**len(quanti_datastream.read_addr)
    component = Component()

    @block
    def bench_quant():
        """instantiation of quantizer module and clock"""
        inst = quantizer_top(
            reset, clock, quanti_datastream,
            quant_ctrl, quant_config, quanto_datastream)

        inst_clock = tbclock(clock)

        @instance
        def tbstim():
            """we send test cases here"""

            # reset the block before processing
            yield reset_on_start(clock, reset)

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
            color = component.Y2

            # process Cb or Cr component
            yield quant_top_block_process(
                clock, quant_ctrl, color, quanto_datastream,
                quanti_datastream, quant_in, quant_rom, max_addr)

            print ("===============================================")

            # select Y1 or Y2 component
            color = component.Cr

            # process Cb or Cr component
            yield quant_top_block_process(
                clock, quant_ctrl, color, quanto_datastream,
                quanti_datastream, quant_in, quant_rom, max_addr)

            raise StopSimulation

        return tbstim, inst, inst_clock

    inst1 = bench_quant()
    inst1.config_sim(trace=False)
    inst1.run_sim()


def test_quant_conversion():
    """Test bench used for conversion purpose"""

    # clock, reset signals declared
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=True, async=True)

    # bus declarations for the module
    quanto_datastream = QuantODataStream(12, 6)
    quanti_datastream = QuantIDataStream(12, 6)
    quant_config = QuantConfig(8, 7)
    quant_ctrl = QuantCtrl()

    @block
    def bench_quant_top_core():
        """wrapper used for conversion purpose"""

        # instantiatiom of quantizer, clock and reset
        inst = quantizer_top(
            reset, clock, quanti_datastream,
            quant_ctrl, quant_config, quanto_datastream)

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
    assert bench_quant_top_core().verify_convert() == 0

test_quantiser()
