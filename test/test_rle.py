"""The functionality of entire
    RLE Module is checked here"""

from myhdl import StopSimulation
from myhdl import block
from myhdl import ResetSignal, Signal, instance
from myhdl.conversion import verify

from jpegenc.subblocks.rle import rlencoder, DataStream
from jpegenc.subblocks.rle import RLEConfig, Component, BufferDataBus

from jpegenc.testing import (clock_driver, reset_on_start,
                             pulse_reset, toggle_signal,)

from jpegenc.testing import run_testbench

from .rle_test_inputs import (red_pixels_1, green_pixels_1, blue_pixels_1,
                             red_pixels_2, green_pixels_2, blue_pixels_2,)


def write_block(
        clock, block_in, input_interface, control_unit, color):
    """Write the data into RLE Double Buffer"""

    max_cnt = 2**(len(input_interface.read_addr)) - 1
    # select one among y1,y2 or cb or cr to be processes
    control_unit.color_component.next = color

    # wait till start signal asserts
    yield toggle_signal(control_unit.start, clock)

    # read data into rle module
    input_interface.data_in.next = block_in[input_interface.read_addr]
    yield clock.posedge

    while input_interface.read_addr != max_cnt:
        # more reads
        input_interface.data_in.next = block_in[input_interface.read_addr]
        yield clock.posedge

    input_interface.data_in.next = block_in[input_interface.read_addr]
    # wait till all the inputs are written into RLE Double Fifo
    for _ in range(4):
        yield clock.posedge


def read_block(select, output_interface, clock):
    """Outputs the data from RLE Double Buffer"""

    # select which buffer should be in read mode
    output_interface.buffer_sel.next = select
    yield clock.posedge

    # enable read mode
    output_interface.read_enable.next = True
    yield clock.posedge

    # pop data out into the bus until fifo becomes empty
    while not output_interface.fifo_empty:
        print ("runlength %d size %d amplitude %d" % (
            output_interface.runlength,
            output_interface.size, output_interface.amplitude))
        yield clock.posedge

    # disable readmode
    output_interface.read_enable.next = False


def test_rle():
    """This test checks the functionality of the Run Length Encoder"""
    @block
    def bench_rle():
        """bench to test the functionality of RLE"""

        # clock and reset signals
        clock = Signal(bool(0))
        reset = ResetSignal(0, active=1, async=True)

        # color component class
        component = Component()
        assert isinstance(component, Component)

        # width of the input data
        width_data = 12

        # width of the address register
        width_addr = 6

        # width of the register to store size
        width_size = width_data.bit_length()

        # width to store the runlength
        width_runlength = 4

        # input data stream into the register
        datastream = DataStream(width_data, width_addr)
        assert isinstance(datastream, DataStream)

        # connection between rlecore output bus and Double FIFO
        bufferdatabus = BufferDataBus(width_data, width_size, width_runlength)
        assert isinstance(bufferdatabus, BufferDataBus)

        # selects the color component, manages start and ready values
        rleconfig = RLEConfig()
        assert isinstance(rleconfig, RLEConfig)

        # instantiation for clock and rletop module
        inst = rlencoder(clock, reset, datastream, bufferdatabus, rleconfig)

        inst_clock = clock_driver(clock)

        @instance
        def tbstim():
            """RLE input tests given here"""

            # reset the stimulus before sending data in
            yield pulse_reset(reset, clock)

            # write y1 component into 1st buffer
            bufferdatabus.buffer_sel.next = False
            yield clock.posedge

            yield write_block(
                clock, red_pixels_1,
                datastream,
                rleconfig, component.y1_space
                )
            yield clock.posedge
            print ("============================")

            # read y1 component from 1st Buffer
            yield read_block(True, bufferdatabus, clock)

            # write y2 component into 2nd Buffer
            yield write_block(
                clock, red_pixels_2,
                datastream,
                rleconfig, component.y2_space
                )
            yield clock.posedge

            print ("============================")

            # read y2 component from 2nd Buffer
            yield read_block(False, bufferdatabus, clock)

            # write cb Component into 1st Buffer
            yield write_block(
                clock, green_pixels_1,
                datastream,
                rleconfig, component.cb_space
                )
            yield clock.posedge
            print ("=============================")

            # read cb component from 1st Buffer
            yield read_block(True, bufferdatabus, clock)

            # write cb Component into 2nd Buffer
            yield write_block(
                clock, green_pixels_2,
                datastream,
                rleconfig, component.cb_space
                )
            yield clock.posedge
            print ("==============================")

            # read cb component from 2nd Buffer
            yield read_block(False, bufferdatabus, clock)

            # write cr Component into 1st Buffer
            yield write_block(
                clock, blue_pixels_1,
                datastream,
                rleconfig, component.cr_space
                )
            yield clock.posedge
            print ("==============================")

            # read cr component from 1st Buffer
            yield read_block(True, bufferdatabus, clock)

            # write cr Component into 2nd Buffer
            yield write_block(
                clock, blue_pixels_2,
                datastream,
                rleconfig, component.cr_space
                )
            yield clock.posedge
            print ("==============================")

            # read cr component from 1st Buffer
            yield read_block(False, bufferdatabus, clock)

            print ("==============================")

            # end of stream when sof asserts
            yield clock.posedge
            rleconfig.sof.next = True
            yield clock.posedge

            raise StopSimulation

        return tbstim, inst_clock, inst

    run_testbench(bench_rle)


def test_rle_conversion():
    """This block is used to test conversion"""

    @block
    def bench_rle_conversion():
        """This bench is meant for conversion purpose"""

        # clock and reset signals
        clock = Signal(bool(0))
        reset = ResetSignal(0, active=1, async=True)

        # width of input data
        width_data = 12

        # width of address bus
        width_addr = 6

        # width to store the size
        width_size = width_data.bit_length()
        width_runlength = 4

        # input data bus for rle module
        datastream = DataStream(width_data, width_addr)
        assert isinstance(datastream, DataStream)

        # connections between output symbols
        bufferdatabus = BufferDataBus(width_data, width_size, width_runlength)
        assert isinstance(bufferdatabus, BufferDataBus)

        # selects the color component, manages address values
        rleconfig = RLEConfig()
        assert isinstance(rleconfig, RLEConfig)

        inst = rlencoder(clock, reset, datastream, bufferdatabus, rleconfig)

        inst_clock = clock_driver(clock)
        inst_reset = reset_on_start(reset, clock)

        @instance
        def tbstim():
            """testbench for conversion purpose"""
            yield clock.posedge
            print("Conversion done!!")
            raise StopSimulation

        return tbstim, inst, inst_clock, inst_reset

    verify.simulator = 'iverilog'
    assert bench_rle_conversion().verify_convert() == 0


if __name__ == "__main__":
    test_rle()
