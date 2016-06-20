"""The functionality of entire Run Length Encoder is checked here"""

from myhdl import StopSimulation
from myhdl import block
from myhdl import ResetSignal, Signal, instance
from myhdl.conversion import verify
from testcases import *

from jpegenc.subblocks.RLE.rletop import InDataStream, BufferDataBus
from jpegenc.subblocks.RLE.rletop import rletop
from jpegenc.subblocks.RLE.RLECore.rlecore import RLEConfig, Pixel

from common import tbclock, reset_on_start, resetonstart, Constants
from common import numofbits, start_of_block, BufferConstants


def write_block(clock, block, datastream, rleconfig, color):
    """Write the data into RLE Double Buffer"""

    # select one among Y1,Y2 or Cb or Cr to be processes
    rleconfig.color_component.next = color

    # wait till start signal asserts
    yield start_of_block(clock, datastream.start)

    # read data into rle module
    datastream.input_val.next = block[rleconfig.read_addr]
    yield clock.posedge

    while rleconfig.read_addr != 63:
        # more reads
        datastream.input_val.next = block[rleconfig.read_addr]
        yield clock.posedge

    datastream.input_val.next = block[rleconfig.read_addr]

    # wait till all the inputs are written into RLE Double Fifo
    yield clock.posedge
    yield clock.posedge
    yield clock.posedge
    yield clock.posedge
    yield clock.posedge


def read_block(select, bufferdatabus, clock):
    """Outputs the data from RLE Double Buffer"""

    # select which buffer should be in read mode
    bufferdatabus.buffer_sel.next = select
    yield clock.posedge

    # enable read mode
    bufferdatabus.read_enable.next = True
    yield clock.posedge
    yield clock.posedge

    # pop data out into the bus until fifo becomes empty
    while bufferdatabus.fifo_empty != 1:
        print ("runlength %d size %d amplitude %d" % (
            bufferdatabus.runlength,
            bufferdatabus.size, bufferdatabus.amplitude))
        yield clock.posedge

    print ("runlength %d size %d amplitude %d" % (
        bufferdatabus.runlength, bufferdatabus.size, bufferdatabus.amplitude))

    # disable readmode
    bufferdatabus.read_enable.next = False
    yield clock.posedge


def test_rle():
    """This block checks the functionality of the Run Length Encoder"""
    @block
    def bench_rle():

        clock = Signal(bool(0))
        reset = ResetSignal(0, active=1, async=True)

        # constants for input, runlength, size width
        constants = Constants(6, 12, 63, 4)
        pixel = Pixel()

        # interfaces to the rle module
        # input to the rle core and start signals sent from here
        indatastream = InDataStream(constants.width_data)

        # signals generated by the rle core
        bufferdatabus = BufferDataBus(
            constants.width_data, constants.size, constants.rlength)

        # selects the color component, manages address values
        rleconfig = RLEConfig(numofbits(constants.max_write_cnt))

        # rle double buffer constants
        width_dbuf = constants.width_data + constants.size + constants.rlength
        dfifo_const = BufferConstants(width_dbuf, constants.max_write_cnt + 1)

        # instantiation for clock and rletop module
        inst = rletop(
            dfifo_const, constants, reset, clock,
            indatastream, bufferdatabus, rleconfig)

        inst_clock = tbclock(clock)

        @instance
        def tbstim():

            # reset the stimulus before sending data in
            yield reset_on_start(clock, reset)

            # write Y1 component into 1st buffer
            bufferdatabus.buffer_sel.next = False
            yield clock.posedge
            yield write_block(
                clock, red_pixels_1,
                indatastream,
                rleconfig, pixel.Y1
                )
            yield clock.posedge
            print ("============================")

            # read Y1 component from 1st Buffer
            yield read_block(True, bufferdatabus, clock)

            # write Y2 component into 2nd Buffer
            yield write_block(
                clock, red_pixels_2,
                indatastream,
                rleconfig, pixel.Y2
                )
            yield clock.posedge

            print ("============================")

            # read Y2 component from 2nd Buffer
            yield read_block(False, bufferdatabus, clock)

            # write Cb Component into 1st Buffer
            yield write_block(
                clock, green_pixels_1,
                indatastream,
                rleconfig, pixel.Cb
                )
            yield clock.posedge
            print ("=============================")

            # read Cb component from 1st Buffer
            yield read_block(True, bufferdatabus, clock)

            # write Cb Component into 2nd Buffer
            yield write_block(
                clock, green_pixels_2,
                indatastream,
                rleconfig, pixel.Cb
                )
            yield clock.posedge
            print ("==============================")

            # read Cb component from 2nd Buffer
            yield read_block(False, bufferdatabus, clock)

            # write Cr Component into 1st Buffer
            yield write_block(
                clock, blue_pixels_1,
                indatastream,
                rleconfig, pixel.Cr
                )
            yield clock.posedge
            print ("==============================")

            # read Cr component from 1st Buffer
            yield read_block(True, bufferdatabus, clock)

            # write Cr Component into 2nd Buffer
            yield write_block(
                clock, blue_pixels_2,
                indatastream,
                rleconfig, pixel.Cr
                )
            yield clock.posedge
            print ("==============================")

            # read Cr component from 1st Buffer
            yield read_block(False, bufferdatabus, clock)

            print ("==============================")

            # end of stream when sof asserts
            yield clock.posedge
            rleconfig.sof.next = True
            yield clock.posedge

            raise StopSimulation

        return tbstim, inst_clock, inst

    instance_rle = bench_rle()
    instance_rle.config_sim(trace=False)
    instance_rle.run_sim()


def test_rle_conversion():
    """This block is used to test conversion"""

    @block
    def bench_rle_conversion():

        constants = Constants(6, 12, 63, 4)

        clock = Signal(bool(0))
        reset = ResetSignal(0, active=1, async=True)

        indatastream = InDataStream(constants.width_data)
        bufferdatabus = BufferDataBus(
            constants.width_data, constants.size, constants.rlength)

        rleconfig = RLEConfig(numofbits(constants.max_write_cnt))

        width_dbuf = constants.width_data + constants.size + constants.rlength
        dfifo_const = BufferConstants(width_dbuf, constants.max_write_cnt + 1)

        inst = rletop(
            dfifo_const, constants, reset,
            clock, indatastream, bufferdatabus, rleconfig)

        inst_clock = tbclock(clock)
        inst_reset = resetonstart(clock, reset)

        @instance
        def tbstim():
            yield clock.posedge
            print ("Conversion done!!")
            raise StopSimulation

        return tbstim, inst, inst_clock, inst_reset

    verify.simulator = 'iverilog'
    assert bench_rle_conversion().verify_convert() == 0
