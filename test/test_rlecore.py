from myhdl.conversion import *
from myhdl import *
from jpegenc.subblocks.RLE.RLECore.rlecore import DataStream, rle, Pixel
from jpegenc.subblocks.RLE.RLECore.rlecore import RLESymbols, RLEConfig
from testcases import *
from commons import tbclock, reset_on_start, resetonstart
from commons import numofbits, start_of_block, block_process

class Constants(object):
    def __init__(self, width_addr, width_data, max_write_cnt):
        self.width_addr = width_addr
        self.width_data = width_data
        self.size = numofbits(width_data)
        self.max_write_cnt = max_write_cnt


def test_rle_core():

    clock = Signal(bool(0))
    reset = ResetSignal(0, active=1, async=True)

    constants = Constants(6, 12, 63)
    pixel = Pixel()
    datastream = DataStream(constants.width_data)
    rlesymbols = RLESymbols(constants.width_data, constants.size)
    rleconfig = RLEConfig(numofbits(constants.max_write_cnt))

    @block
    def bench_rle_core():
        inst = rle(
            constants,
            reset, clock,
            datastream, rlesymbols, rleconfig
            )

        inst_clock = tbclock(clock)

        @instance
        def tbstim():

            yield reset_on_start(clock, reset)

            yield block_process(constants,
                clock, red_pixels_1,
                datastream,
                rlesymbols,
                rleconfig, pixel.Y1
                )

            print ("=====")

            yield block_process(constants,
                clock, red_pixels_2,
                datastream,
                rlesymbols,
                rleconfig, pixel.Y2
                )

            print ("=====")

            yield block_process(constants,
                clock, blue_pixels_1,
                datastream,
                rlesymbols,
                rleconfig, pixel.Cb
                )

            print ("=====")
            
            yield block_process(constants,
                clock, blue_pixels_2,
                datastream,
                rlesymbols,
                rleconfig, pixel.Cb
                )

            print ("=====")
        
            yield block_process(constants,
                clock, green_pixels_1,
                datastream,
                rlesymbols,
                rleconfig, pixel.Cr
                )

            print ("=====")


            yield block_process(constants,
                clock, green_pixels_2,
                datastream,
                rlesymbols,
                rleconfig, pixel.Cr
                )

            print ("=====")


            rleconfig.sof.next = True
            yield clock.posedge

            raise StopSimulation

        return tbstim, inst_clock, inst

    instance_rle = bench_rle_core()
    instance_rle.config_sim(trace=False)
    instance_rle.run_sim()

def test_rle_conversion():

    clock = Signal(bool(0))
    reset = ResetSignal(0, active=1, async=True)

    constants = Constants(6, 12, 63)
    pixel = Pixel()
    datastream = DataStream(constants.width_data)
    rlesymbols = RLESymbols(constants.width_data, constants.size)
    rleconfig = RLEConfig(numofbits(constants.max_write_cnt))

    @block
    def bench_rle_core():
        inst = rle(
            constants,
            reset, clock,
            datastream, rlesymbols, rleconfig
            )

        inst_clock = tbclock(clock)
        inst_reset = resetonstart(clock, reset)

        @instance
        def tbstim():

            yield clock.posedge
            print ("Conversion done!!")
            raise StopSimulation

        return tbstim, inst, inst_clock, inst_reset

    verify.simulator = 'iverilog'
    assert bench_rle_core().verify_convert() == 0
