from myhdl import *
from myhdl.conversion import *
from jpegenc.subblocks.RLE.rletop import *
from testcases import *
from jpegenc.subblocks.RLE.RLECore.rlecore import DataStream, rle
from jpegenc.subblocks.RLE.RLECore.rlecore import RLEConfig, Pixel
from jpegenc.subblocks.RLE.RleDoubleFifo.rledoublebuffer import *
from commons import tbclock, reset_on_start, resetonstart, Constants, BufferConstants
from commons import numofbits, start_of_block, block_process, write_block, read_block


def test_rle():

    @block
    def bench_rle():

        constants = Constants(6, 12, 63, 4)
        clock = Signal(bool(0))
        reset = ResetSignal(0, active=1, async=True)

        pixel = Pixel()

        indatastream = InDataStream(constants.width_data)
        bufferdatabus = BufferDataBus(constants.width_data, constants.size, constants.rlength)
        rleconfig = RLEConfig(numofbits(constants.max_write_cnt))
    
        width_dbuf = constants.width_data + constants.size + constants.rlength
        dfifo_const = BufferConstants(width_dbuf, constants.max_write_cnt + 1)

        inst = rletop(dfifo_const, constants, reset, clock, indatastream, bufferdatabus, rleconfig)
        inst_clock = tbclock(clock)

        @instance
        def tbstim():

            yield reset_on_start(clock, reset)

            bufferdatabus.buffer_sel.next = False
            yield clock.posedge
            yield write_block(
                clock, red_pixels_1,
                indatastream,
                bufferdatabus,
                rleconfig, pixel.Y1
                )
            yield clock.posedge
            print ("=====")

            yield read_block(True, bufferdatabus, clock)

            yield write_block(
                clock, red_pixels_2,
                indatastream,
                bufferdatabus,
                rleconfig, pixel.Y2
                )
            yield clock.posedge

            print ("=====")

            yield read_block(False, bufferdatabus, clock)

            yield write_block(
                clock, green_pixels_1,
                indatastream,
                bufferdatabus,
                rleconfig, pixel.Cb
                )
            yield clock.posedge
            print ("=======")


            yield read_block(True, bufferdatabus, clock)

            yield write_block(
                clock, green_pixels_2,
                indatastream,
                bufferdatabus,
                rleconfig, pixel.Cb
                )
            yield clock.posedge
            print ("=======")


            yield read_block(False, bufferdatabus, clock)

            yield write_block(
                clock, blue_pixels_1,
                indatastream,
                bufferdatabus,
                rleconfig, pixel.Cr
                )
            yield clock.posedge
            print ("=======")


            yield read_block(True, bufferdatabus, clock)

            yield write_block(
                clock,  blue_pixels_2,
                indatastream,
                bufferdatabus,
                rleconfig, pixel.Cr
                )
            yield clock.posedge
            print ("=======")

            yield read_block(False, bufferdatabus, clock)

            print ("===============")

            yield clock.posedge
            rleconfig.sof.next = True
            yield clock.posedge

            raise StopSimulation        

        return  tbstim, inst_clock, inst

    instance_rle = bench_rle()
    instance_rle.config_sim(trace = False)
    instance_rle.run_sim()

def test_rle_conversion():

    @block
    def bench_rle_conversion():

        constants = Constants(6, 12, 63, 4)
        clock = Signal(bool(0))
        reset = ResetSignal(0, active=1, async=True)

        pixel = Pixel()

        indatastream = InDataStream(constants.width_data)
        bufferdatabus = BufferDataBus(constants.width_data, constants.size, constants.rlength)
        rleconfig = RLEConfig(numofbits(constants.max_write_cnt))
    
        width_dbuf = constants.width_data + constants.size + constants.rlength
        dfifo_const = BufferConstants(width_dbuf, constants.max_write_cnt + 1)

        inst = rletop(dfifo_const, constants, reset, clock, indatastream, bufferdatabus, rleconfig)
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
