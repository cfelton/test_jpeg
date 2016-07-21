"""MyHDL implementation of Huffman Encoder Module"""

from myhdl import always_seq, block, always_comb
from myhdl import Signal, modbv, intbv
from .dc_rom import dc_rom
from .ac_rom import ac_rom
from .ac_cr_rom import ac_cr_rom
from .dc_cr_rom import dc_cr_rom
from .doublebuffer import doublefifo
from rhea.system import FIFOBus


class HuffmanCntrl(object):
    """
    These are the control signals for Huffman block
    start           : start sending block
    ready           : request for next block
    color_component : select the component to be processed
    sof             : start of frame

    """
    def __init__(self):
        self.start = Signal(bool(0))
        self.ready = Signal(bool(0))
        self.color_component = Signal(intbv(0)[3:])
        self.sof = Signal(bool(0))


class ImgSize(object):
    """
    Indicates dimensions of the Image
    width  : width of the image
    height : height of the image

    """
    def __init__(self, width, height):
        self.width = width
        self.height = height


class HuffmanDataStream(object):
    """
    Input interface bus to the Huffman module
    runlength  : runlength of the data byte
    vli_size   : number of bits required to store vli
    vli        : amplitude of the data
    data_valid : input data is valid

    """
    def __init__(self, width_runlength, width_size,
                 width_amplitude, width_addr):
        self.runlength = Signal(intbv(0)[width_runlength:])
        self.vli_size = Signal(intbv(0)[width_size:])
        self.vli = Signal(intbv(0)[width_amplitude:])
        self.data_valid = Signal(bool(0))
        self.read_addr = Signal(intbv(0)[width_addr:])


class BufferDataBus(object):
    """
    Output Interface of the Huffman module
    read_req        : access to read the output data stored in FIFO
    fifo_empty      : output fifo is empty
    buffer_sel      : select a buffer from Double Fifo
    huf_packed_byte : Huffman Encoded Output

    """
    def __init__(self, width_packed_byte):
        self.read_req = Signal(bool(0))
        self.fifo_empty = Signal(bool(0))
        self.buffer_sel = Signal(bool(0))
        self.huf_packed_byte = Signal(intbv(0)[width_packed_byte:])


class VLControl(object):
    """Contains the four states in which the FSM Operates"""
    def __init__(self):
        self.idle = 0
        self.vlc = 1
        self.vli = 2
        self.pad = 3


@block
def huffman(clock, reset, huffmancntrl, bufferdatabus,
            huffmandatastream, img_size, rle_fifo_empty):
    """HDL Implementation of Huffman Module. This module takes
    Variable Length Encoded Inputs and serialise them to VLC
    using Huffman Rom Tables

    Args:
    huffmancntrl : control signals interface
    huffmandatastream : Input Interface
    img_size : Image data class
    rle_fifo_empty : asserts when Input buffer is empty

    Returns:
    bufferdatabus : Output FIFO Interface

    Constants:
    block_size : size of each block
    vlcontrol : contains the states used to run huff_fsm
    image_size.width : width of image
    image_size.heigth : height of image
    bits_block_count : width to store number of blocks in image
    width_word : maximum width of the word register

    """

    assert isinstance(huffmandatastream, HuffmanDataStream)
    assert isinstance(bufferdatabus, BufferDataBus)
    assert isinstance(img_size, ImgSize)
    assert isinstance(huffmancntrl, HuffmanCntrl)

    #constant defined from huffman tables.
    # 7 bits from previous loop and 16 from present one
    width_word = 16+7

    block_size = 2**len(huffmandatastream.read_addr)

    # calculated area of image
    area = (img_size.width*img_size.height)*(3)

    # number of blocks
    bits_block_cnt = area/64

    # contains all the states
    vlcontrol = VLControl()
    assert isinstance(vlcontrol, VLControl)

    # used to denote the processing state
    state = Signal(intbv(0)[2:])
    # asserts if processing first rle word
    first_rle_word = Signal(bool(0))
    # fsm writes data into word_reg
    word_reg = Signal(modbv(0)[width_word:])
    # keeps updated locations in word_reg to be written
    bit_ptr = Signal(intbv(0)[5:])
    # number of bits written in fifo
    num_fifo_wrs = Signal(intbv(0)[2:])

    # output FIFO Bus
    dfifo = FIFOBus(width=len(bufferdatabus.huf_packed_byte))
    assert isinstance(dfifo, FIFOBus)

    # asserts if its ready to handle fifo writes
    ready_hfw = Signal(bool(0))

    # take a note of number of fifo writes
    fifo_wrt_cnt = Signal(intbv(0)[2:])

    # asserts if processing last block
    last_block = Signal(bool(0))

    # area of the image
    img_area = Signal(intbv(0)[(img_size.width + img_size.height):])
    block_cnt = Signal(intbv(0)[bits_block_cnt:])

    # delay line signals
    d_val_d1 = Signal(bool(0))
    d_val_d2 = Signal(bool(0))
    d_val_d3 = Signal(bool(0))
    d_val_d4 = Signal(bool(0))

    vli_size_d = Signal(intbv(0)[len(huffmandatastream.vli_size):])
    vli_d = Signal(intbv(0)[len(huffmandatastream.vli):])
    vli_size_d1 = Signal(intbv(0)[len(huffmandatastream.vli_size):])
    vli_d1 = Signal(intbv(0)[len(huffmandatastream.vli):])

    # extended vli as per vlc size
    vli_ext = Signal(intbv(0)[16:])
    vli_ext_size = Signal(intbv(0)[5:])

    # used to determine if HFW block is running
    hfw_running = Signal(bool(0))

    vli_size_temp = Signal(intbv(0)[len(huffmandatastream.vli_size):])
    vli_temp = Signal(intbv(0)[len(huffmandatastream.vli):])
    read_enable_temp = Signal(bool(0))

    pad_byte = Signal(intbv(0)[len(bufferdatabus.huf_packed_byte):])
    pad_reg = Signal(bool(0))

    # these width came from constant AC and DC ROM's
    # @todo: Build Huffman tables using the Huffman Tree
    vlc_size = Signal(intbv(0)[5:])
    vlc = Signal(intbv(0)[16:])
    vlc_dc_size = Signal(intbv(0)[4:])
    vlc_dc = Signal(intbv(0)[9:])
    vlc_ac_size = Signal(intbv(0)[5:])
    vlc_ac = Signal(intbv(0)[16:])
    vlc_cr_dc_size = Signal(intbv(0)[4:])
    vlc_cr_dc = Signal(intbv(0)[11:])
    vlc_cr_ac_size = Signal(intbv(0)[5:])
    vlc_cr_ac = Signal(intbv(0)[16:])

    start_temp = Signal(bool(0))

    @always_seq(clock.posedge, reset=reset)
    def latch():
        """This latch stores input values"""
        if huffmandatastream.data_valid:
            vli_size_temp.next = huffmandatastream.vli_size
            vli_temp.next = huffmandatastream.vli

    inst_dc_rom = dc_rom(clock, huffmandatastream.vli_size,
                         vlc_dc_size, vlc_dc)

    inst_ac_rom = ac_rom(clock, huffmandatastream.runlength,
                         huffmandatastream.vli_size, vlc_ac_size, vlc_ac)

    inst_cr_dc_rom = dc_cr_rom(clock, huffmandatastream.vli_size,
                               vlc_cr_dc_size, vlc_cr_dc)

    inst_cr_ac_rom = ac_cr_rom(clock, huffmandatastream.runlength,
                               huffmandatastream.vli_size,
                               vlc_cr_ac_size, vlc_cr_ac)

    inst_dfifo = doublefifo(clock, reset, dfifo, bufferdatabus.buffer_sel,
                            depth=block_size)

    @always_comb
    def assign_out():
        """output signal assignments from FIFO Bus"""
        bufferdatabus.huf_packed_byte.next = dfifo.read_data
        dfifo.read.next = bufferdatabus.read_req
        bufferdatabus.fifo_empty.next = dfifo.empty

    @always_seq(clock.posedge, reset=reset)
    def mux_rom():
        """mux for ac/dc rom selection"""
        if first_rle_word:
            if huffmancntrl.color_component < 2:
                vlc_size.next = vlc_dc_size
                vlc.next = vlc_dc
            else:
                vlc_size.next = vlc_cr_dc_size
                vlc.next = vlc_cr_dc

        else:
            if huffmancntrl.color_component < 2:
                vlc_size.next = vlc_ac_size
                vlc.next = vlc_ac
            else:
                vlc_size.next = vlc_cr_ac_size
                vlc.next = vlc_cr_ac

    @always_comb
    def ext():
        """create vli ext variables"""
        vli_ext.next = vli_d1
        vli_ext_size.next = vli_size_d1

    @always_seq(clock.posedge, reset=reset)
    def blk_cntr():
        """block counter counts number of blocks"""
        img_area.next = (img_size.width)*(img_size.height)
        if huffmancntrl.sof:
            block_cnt.next = 0

        elif huffmancntrl.start:
            block_cnt.next = block_cnt + 1

        # dividing block area by 64 to get the number of 8x8 blocks
        # right shift 5 times to divide by 64
        if block_cnt == img_area[32:5]:
            last_block.next = True
        else:
            last_block.next = False

    @always_seq(clock.posedge, reset=reset)
    def delay_line():
        """It delayes signals"""

        vli_d1.next = vli_temp
        vli_size_d1.next = vli_size_temp
        vli_d.next = vli_d1
        vli_size_d.next = vli_size_d1
        d_val_d1.next = huffmandatastream.data_valid
        d_val_d2.next = d_val_d1
        d_val_d3.next = d_val_d2
        d_val_d4.next = d_val_d3

    @always_seq(clock.posedge, reset=reset)
    def fifo_writes():
        """writing data into the FIFO"""

        # handle fifo writes
        dfifo.write.next = False
        ready_hfw.next = False
        read_enable_temp.next = False
        start_temp.next = huffmancntrl.start

        if start_temp:
            read_enable_temp.next = True and not rle_fifo_empty

        if hfw_running and not ready_hfw:

            # no bytes to write
            if num_fifo_wrs == 0:
                ready_hfw.next = True
                if state == vlcontrol.vli:
                    read_enable_temp.next = True and not rle_fifo_empty

            # bytes write to fifo
            else:
                fifo_wrt_cnt.next = fifo_wrt_cnt + 1
                dfifo.write.next = True
                # last byte write
                if (fifo_wrt_cnt + 1) == num_fifo_wrs:
                    ready_hfw.next = True
                    if state == vlcontrol.vli:
                        read_enable_temp.next = True and not rle_fifo_empty
                    fifo_wrt_cnt.next = 0

        if fifo_wrt_cnt == 0:
            dfifo.write_data.next = word_reg[(width_word):(width_word-8)]

        elif fifo_wrt_cnt == 1:
            dfifo.write_data.next = word_reg[(width_word-8):(width_word-16)]

        else:
            dfifo.write_data.next = 0

        if pad_reg == 1:
            dfifo.write_data.next = pad_byte

    @always_comb
    def div_by8():
        """divide number of fifowrites by eight"""
        num_fifo_wrs.next = bit_ptr[5:3]

    @always_seq(clock.posedge, reset=reset)
    def huff_fsm():
        """Huffman Encoder Finite State Machine"""

        # processing present block
        huffmancntrl.ready.next = False

        # IDLE mode : enables processing of first rle word
        if state == vlcontrol.idle:
            if huffmancntrl.start:
                # first rle word to be processed
                first_rle_word.next = True
                # move to next state
                state.next = vlcontrol.vlc

        # VLC Mode : send vlc data into word_reg
        elif state == vlcontrol.vlc:
            # process rle words when data is valid
            if (d_val_d1 and first_rle_word) or (
                    huffmandatastream.data_valid and not first_rle_word):
                # add vlc data in the MSB positions of word_reg
                for i in range(width_word):
                    if i < int(vlc_size):
                        word_reg.next[(width_word-1-int(
                            bit_ptr)-i)] = vlc[int(vlc_size)-1-i]
                # increment bit pointer to the position
                # next after the vlc data is stored
                bit_ptr.next = bit_ptr + vlc_size
                # enable handling fifo writes
                hfw_running.next = True

            # handle fifo writes
            elif hfw_running and ((
                    num_fifo_wrs == 0)or ((fifo_wrt_cnt+1) == num_fifo_wrs)):
                # left shift word reg to skip bytes already written to FIFO
                word_reg.next = word_reg << ((num_fifo_wrs)*8)
                # adjust bit pointer as per the updated word_reg
                # modulo 8 operation on bit_ptr
                bit_ptr.next = bit_ptr - ((num_fifo_wrs)*8)
                # disable handling fifo writes
                hfw_running.next = False
                # disable first rle word
                first_rle_word.next = False
                # move to next state
                state.next = vlcontrol.vli

        # append vli code word to word_reg
        elif state == vlcontrol.vli:
            # handle fifo writes is not enabled
            if not hfw_running:
                # write vli code word to word_reg
                for i in range(width_word):
                    if i < int(vli_ext_size):
                        word_reg.next[width_word-1-int(
                            bit_ptr)-i] = vli_ext[int(vli_ext_size)-1-i]

                # update bit pointer after adding vli code-word
                bit_ptr.next = bit_ptr + vli_ext_size
                #print ("%d bit_ptr is vlli" %bit_ptr.next)
                # enable handling fifo writes
                hfw_running.next = True

            # handle fifo writes
            elif hfw_running and (
                    (num_fifo_wrs == 0) or ((
                    fifo_wrt_cnt+1) == num_fifo_wrs)):

                # shift word reg to skip bytes already written to FIFO
                word_reg.next = word_reg << (num_fifo_wrs*8)
                # adjust bit pointer to the updated value
                bit_ptr.next = bit_ptr - (num_fifo_wrs*8)
                # disable handling fifo writes
                hfw_running.next = False
                # end of block encountered
                if rle_fifo_empty:
                    # end of image
                    if ((bit_ptr - (
                         num_fifo_wrs * 8) != 0) and last_block):
                        # shift to next state
                        state.next = vlcontrol.pad
                    else:
                        # end of block send next block
                        huffmancntrl.ready.next = True
                        # move to first state
                        state.next = vlcontrol.idle
                # current block yet to be processed
                else:
                    # move to previous state
                    state.next = vlcontrol.vlc

        # padding with ones on end of image if required
        elif state == vlcontrol.pad:
            # handle fifo writes disabled
            if not hfw_running:
                # pad bytes when end of file reached
                for i in range(7):
                    if i < bit_ptr:
                        pad_byte.next[7-i] = word_reg[width_word-1-i]
                    else:
                        # pad ones
                        pad_byte.next[7-i] = 1

                pad_reg.next = 1
                bit_ptr.next = 8
                # enable handling fifo writes
                hfw_running.next = True

            # handle fifo writes
            elif (hfw_running and (
                  num_fifo_wrs == 0 or (fifo_wrt_cnt+1) == num_fifo_wrs)):

                # reset bit pointer
                bit_ptr.next = 0
                # disable fifo writes handling
                hfw_running.next = False
                # reset pad bytes
                pad_reg.next = 0
                huffmancntrl.ready.next = True
                state.next = vlcontrol.idle
        else:
            pass

        # start of frame
        if huffmancntrl.sof:
            bit_ptr.next = 0

    return (latch, inst_dc_rom, inst_ac_rom, inst_cr_dc_rom,
            inst_cr_ac_rom, inst_dfifo, mux_rom, ext, delay_line,
            blk_cntr, fifo_writes, div_by8, huff_fsm, assign_out)
