from myhdl import always_seq, block
from myhdl import intbv, ResetSignal, Signal
from myhdl import *
from myhdl.conversion import analyze
from jpegenc.subblocks.RLE.RLECore.rlecore import DataStream, rle
from jpegenc.subblocks.RLE.RLECore.rlecore import RLESymbols, RLEConfig
from jpegenc.subblocks.RLE.RleDoubleFifo.rledoublebuffer import *
WIDTH_RAM_ADDRESS = 6
WIDTH_RAM_DATA = 12
SIZE = 4


class  InDataStream(DataStream):
    """
    InDataStream Interface :
    ready: module asserts ready if its ready for next block
    start: start signal triggers the module to start
           processing data
    input_val: input to the rle module
    """
    def __init__(self):
        super(InDataStream, self).__init__()
        self.ready = Signal(bool(0))


class BufferDataBus(RLESymbols):
    """ 
    Connections related to rle double buffer:

    amplitude: amplitude of the number
    size: size required to store amplitude
    runlength: number of zeros
    dovalid: asserts if ouput is valid 
    buffer_sel: It selects the buffer in double buffer
    read_enable: enables
    fifo_empty: asserts if any of the two fifos are empty
    """
    def __init__(self):
        super(BufferDataBus, self).__init__()
        self.buffer_sel = Signal(bool(0))
        self.read_enable = Signal(bool(0))
        self.fifo_empty = Signal(bool(0))


@block
def rletop(reset, clock, indatastream, bufferdatabus, rleconfig):

    # signals used for RLE Core

    rlesymbols_temp = RLESymbols()
    datastream_temp = DataStream()
    dfifo = DoubleFifoBus()
    wr_cnt = Signal(intbv(0)[7:])


    @always_comb
    def assign0():
        dfifo.buffer_sel.next = bufferdatabus.buffer_sel
        dfifo.read_req.next = bufferdatabus.read_enable
        bufferdatabus.fifo_empty.next = dfifo.fifo_empty
        datastream_temp.start.next = indatastream.start



    @always_comb
    def assign1():
        """ output assignments """
        bufferdatabus.runlength.next = dfifo.data_out[20:16]
        bufferdatabus.size.next = dfifo.data_out[16:12]
        bufferdatabus.amplitude.next = dfifo.data_out[12:0]
        
        # quantiser.buffer_sel.next = buffer_sel_temp_q

    # rle core instantiation
    rle_core = rle(reset, clock, datastream_temp, rlesymbols_temp, rleconfig)

    @always_comb
    def assign2():
        datastream_temp.input_val.next = indatastream.input_val

    #instantiation of rle double buffer
    rle_doublefifo = rledoublefifo(reset, clock, dfifo)

    @always_comb
    def assign3():
        dfifo.data_in.next = concat (
            rlesymbols_temp.runlength, rlesymbols_temp.size, rlesymbols_temp.amplitude)
    
        # print ("data is %d %d %d" % (rlesymbols_temp.runlength, rlesymbols_temp.size, rlesymbols_temp.amplitude))
        dfifo.write_enable.next = rlesymbols_temp.dovalid
        # print ("%d wrte is" %rlesymbols_temp.dovalid)

    @always_seq(clock.posedge, reset=reset)
    def seq1():
        indatastream.ready.next = 0
        if indatastream.start == 1:
            wr_cnt.next = 0


        if rlesymbols_temp.dovalid == 1:
            if (rlesymbols_temp.runlength == 15) and (rlesymbols_temp.size == 0):
                wr_cnt.next = wr_cnt + 16

            else:
                wr_cnt.next = wr_cnt + 1 + rlesymbols_temp.runlength

        if dfifo.data_in == 0 and wr_cnt != 0:
            indatastream.ready.next = 1
        else:
            if (wr_cnt + rlesymbols_temp.runlength == 63):
                indatastream.ready.next = 1


    @always_comb
    def assign4():
        bufferdatabus.dovalid.next = bufferdatabus.read_enable

    return assign0, assign1, rle_core, assign2, rle_doublefifo, assign3, seq1, assign4


# def convert():

 #   clock = Signal(bool(0))
 #   reset = ResetSignal(0, active=1, async=True)


  #  indatastream = InDataStream()
   # bufferdatabus = BufferDataBus()
  #  rleconfig = RLEConfig()

   # inst = rletop(reset, clock, indatastream, bufferdatabus, rleconfig)
   # inst.convert = 'verilog'

   # analyze.simulator = 'iverilog'
   # assert rletop(reset, clock, indatastream, bufferdatabus, rleconfig).analyze_convert() == 0

#if __name__ == '__main__':
 #   convert()
