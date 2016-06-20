from myhdl import block, delay, instance
from jpegenc.subblocks.RLE.RLECore.rlecore import DataStream, rle
from jpegenc.subblocks.RLE.RLECore.rlecore import RLEConfig

@block
def tbclock(clock):
    @instance
    def clockgen():
        clock.next = False
        while True:
            yield delay(10)
            clock.next = not clock
    return clockgen

@block
def resetonstart(clock, reset):
    """reset block used for verification purpose"""
    @instance
    def reset_button():
        reset.next = True
        yield delay(40)
        yield clock.posedge
        reset.next = False
    return reset_button


def start_of_block(clock, start):
    start.next = True
    yield clock.posedge
    start.next = False
    yield clock.posedge


def reset_on_start(clock, reset):
    reset.next = True
    yield delay(40)
    yield clock.posedge
    reset.next = False

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
