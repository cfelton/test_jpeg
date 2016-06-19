from myhdl.conversion import *
from myhdl import *
from jpegenc.subblocks.RLE.RLECore.rlecore import DataStream, rle
from jpegenc.subblocks.RLE.RLECore.rlecore import RLESymbols, RLEConfig
from testcases import *
from commons import tbclock, reset_on_start, resetonstart
from commons import numofbits, Pixel, start_of_block

class Constants(object):
    def __init__(self, width_addr, width_data, max_write_cnt):
        self.width_addr = width_addr
        self.width_data = width_data
        self.size = numofbits(width_data)
        self.max_write_cnt = max_write_cnt



def block_process(constants, clock, block, datastream, rlesymbols, rleconfig, color):
    # select color component
    rleconfig.color_component.next = color
    yield start_of_block(clock, datastream.start)

    datastream.input_val.next = block[rleconfig.read_addr]
    yield clock.posedge

    while rleconfig.read_addr != constants.max_write_cnt:
        datastream.input_val.next = block[rleconfig.read_addr]
        yield clock.posedge
        if rlesymbols.dovalid:
            print("amplitude = %d runlength = %d size = %d" % (
                rlesymbols.amplitude, rlesymbols.runlength, rlesymbols.size))

    datastream.input_val.next = block[rleconfig.read_addr]
    
    yield clock.posedge

    if rlesymbols.dovalid:
        print("amplitude = %d runlength = %d size = %d" % (
            rlesymbols.amplitude, rlesymbols.runlength, rlesymbols.size))

    yield clock.posedge
    
    if rlesymbols.dovalid:
        print("amplitude = %d runlength = %d size = %d" % (
            rlesymbols.amplitude, rlesymbols.runlength, rlesymbols.size))
    
    yield clock.posedge
    
    if rlesymbols.dovalid:
        print("amplitude = %d runlength = %d size = %d" % (
            rlesymbols.amplitude, rlesymbols.runlength, rlesymbols.size))
    
    yield clock.posedge
    
    if rlesymbols.dovalid:
        print("amplitude = %d runlength = %d size = %d" % (
            rlesymbols.amplitude, rlesymbols.runlength, rlesymbols.size))

    yield clock.posedge
    if rlesymbols.dovalid:
        print("amplitude = %d runlength = %d size = %d" % (
                rlesymbols.amplitude, rlesymbols.runlength, rlesymbols.size))


@block
def test():

    clock = Signal(bool(0))
    reset = ResetSignal(0, active=1, async=True)

    constants = Constants(6, 12, 63)
    pixel = Pixel()
    datastream = DataStream(constants.width_data)
    rlesymbols = RLESymbols(constants.width_data, constants.size)
    rleconfig = RLEConfig(numofbits(constants.max_write_cnt))


    jpgv1 = rle(constants,
        reset, clock,
        datastream, rlesymbols, rleconfig
        )

    @instance
    def tbclock():
        clock.next = 0
        while True:
            yield delay(10)
            clock.next = not clock

    @instance
    def tbsim():
        """ reset signal """
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

    return tbsim, tbclock, jpgv1


def conversion_bench():

    instance = test()
    instance.config_sim(trace=True)
    instance.run_sim()
    # verify.simulator='iverilog'
    # assert testbench2().verify_convert() == 0

if __name__ == '__main__':
    conversion_bench()
