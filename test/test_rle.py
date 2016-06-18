from myhdl import *
from myhdl.conversion import *
from jpegenc.subblocks.RLE.rletop import *
from testcases import *
from jpegenc.subblocks.RLE.RLECore.rlecore import DataStream, rle
from jpegenc.subblocks.RLE.RLECore.rlecore import RLEConfig
from jpegenc.subblocks.RLE.RleDoubleFifo.rledoublebuffer import *
# from test_rlecore import *

red = 1
green = 2
blue = 3

WIDTH_RAM_ADDRESS = 6
WIDTH_RAM_DATA = 12


def reset_on_start(clock, reset):
    reset.next = True
    yield delay(20)
    yield clock.posedge
    reset.next = False

def start_of_block(clock, start):
    start.next = True
    yield clock.posedge
    start.next = False
    yield clock.posedge

def write_block(clock, block, datastream, rlesymbols, rleconfig, color):
    # select color component
    rleconfig.color_component.next = color
    yield start_of_block(clock, datastream.start)

    datastream.input_val.next = block[rleconfig.read_addr]
    yield clock.posedge
    while rleconfig.read_addr != 63:
        datastream.input_val.next = block[rleconfig.read_addr]
        yield clock.posedge

    datastream.input_val.next = block[rleconfig.read_addr]
    yield clock.posedge
    yield clock.posedge
    yield clock.posedge
    yield clock.posedge
    yield clock.posedge


def read_block(select, bufferdatabus, clock):
    bufferdatabus.buffer_sel.next = select
    yield clock.posedge
    bufferdatabus.read_enable.next = True
    yield clock.posedge
    yield clock.posedge
    while bufferdatabus.fifo_empty != 1:
        print ("runlength %d size %d amplitude %d" % (
            bufferdatabus.runlength, bufferdatabus.size, bufferdatabus.amplitude))
        yield clock.posedge

    print ("runlength %d size %d amplitude %d" % (
        bufferdatabus.runlength, bufferdatabus.size, bufferdatabus.amplitude))

    bufferdatabus.read_enable.next = False
    yield clock.posedge

@block
def test():

    clock = Signal(bool(0))
    reset = ResetSignal(0, active=1, async=True)

    indatastream = InDataStream()
    bufferdatabus = BufferDataBus()
    rleconfig = RLEConfig()

    jpgv1 = rletop(reset, clock, indatastream, bufferdatabus, rleconfig)
   

    @instance
    def tbclock():
        clock.next=0
        while True:
            yield delay(10)
            clock.next = not clock


    @instance
    def tbsim():
        """ reset signal """
        yield reset_on_start(clock, reset)

        bufferdatabus.buffer_sel.next = False
        yield clock.posedge
        yield write_block(
            clock, red_pixels_1,
            indatastream,
            bufferdatabus,
            rleconfig,  red
            )
        yield clock.posedge
        print ("=====")

        yield read_block(True, bufferdatabus, clock)

        yield write_block(
            clock, red_pixels_2,
            indatastream,
            bufferdatabus,
            rleconfig,  red
            )
        yield clock.posedge

        print ("=====")

        yield read_block(False, bufferdatabus, clock)

        yield write_block(
            clock, green_pixels_1,
            indatastream,
            bufferdatabus,
            rleconfig, green
            )
        yield clock.posedge
        print ("=======")


        yield read_block(True, bufferdatabus, clock)

        yield write_block(
            clock, green_pixels_2,
            indatastream,
            bufferdatabus,
            rleconfig, green
            )
        yield clock.posedge
        print ("=======")


        yield read_block(False, bufferdatabus, clock)

        yield write_block(
            clock, blue_pixels_1,
            indatastream,
            bufferdatabus,
            rleconfig, blue
            )
        yield clock.posedge
        print ("=======")


        yield read_block(True, bufferdatabus, clock)

        yield write_block(
            clock,  blue_pixels_2,
            indatastream,
            bufferdatabus,
            rleconfig, blue
            )
        yield clock.posedge
        print ("=======")

        yield read_block(False, bufferdatabus, clock)

        print ("===============")

        yield clock.posedge
        rleconfig.sof.next = True
        yield clock.posedge

        raise StopSimulation        
    return  tbsim, tbclock, jpgv1



def conversion_bench():

    instance = test()
    instance.config_sim(trace = True)
    instance.run_sim()
    #verify.simulator='iverilog'
    #assert testbench2().verify_convert() == 0

if __name__ == '__main__':
    conversion_bench() 
