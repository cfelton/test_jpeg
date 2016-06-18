from myhdl.conversion import *
from myhdl import *
from jpegenc.subblocks.RLE.RLECore.rlecore import DataStream, rle
from jpegenc.subblocks.RLE.RLECore.rlecore import RLESymbols, RLEConfig
from testcases import *

red = 1
green = 2
blue = 3

WIDTH_RAM_ADDRESS = 6
WIDTH_RAM_DATA = 12


def start_of_block(clock, start):
    start.next = True
    yield clock.posedge
    start.next = False
    yield clock.posedge


def reset_on_start(clock, reset):
    reset.next = True
    yield delay(20)
    yield clock.posedge
    reset.next = False


def block_process(clock, block, datastream, rlesymbols, rleconfig, color):
    # select color component
    rleconfig.color_component.next = color
    yield start_of_block(clock, datastream.start)

    datastream.input_val.next = block[rleconfig.read_addr]
    yield clock.posedge
    while rleconfig.read_addr != 63:
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

    datastream = DataStream()
    rlesymbols = RLESymbols()
    rleconfig = RLEConfig()


    jpgv1 = rle(
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

        yield block_process(
            clock, red_pixels_1,
            datastream,
            rlesymbols,
            rleconfig,  red
            )

        print ("=====")

        yield block_process(
            clock, red_pixels_2,
            datastream,
            rlesymbols,
            rleconfig,  red
            )

        print ("=====")

        yield block_process(
            clock, blue_pixels_1,
            datastream,
            rlesymbols,
            rleconfig,  red
            )

        print ("=====")
        yield block_process(
            clock, blue_pixels_2,
            datastream,
            rlesymbols,
            rleconfig,  red
            )

        print ("=====")
        yield block_process(
            clock, green_pixels_1,
            datastream,
            rlesymbols,
            rleconfig,  red
            )

        print ("=====")


        yield block_process(
            clock, green_pixels_2,
            datastream,
            rlesymbols,
            rleconfig,  red
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
