"""MyHDL implementation of Backend Module"""

from myhdl import (Signal, intbv, always_comb,
                   always_seq, block, concat)

from .dualram import dram
from jpegenc.subblocks.quantizer import quantizer, QuantIODataStream, QuantCtrl
from jpegenc.subblocks.rle import rlencoder, DataStream
from jpegenc.subblocks.rle import BufferDataBus, RLEConfig
from jpegenc.subblocks.huffman import huffman, ImgSize, HuffmanDataStream
from jpegenc.subblocks.huffman import HuffmanCntrl, HuffBufferDataBus
from jpegenc.subblocks.bytestuffer import BSInputDataStream, BScntrl
from jpegenc.subblocks.bytestuffer import bytestuffer, BSOutputDataStream


@block
def backend(clock, reset, start, data_in, write_addr,
            write_enable, data_out, ready, addr, num_enc_bytes):

    """
    Constants:

    width_data : width of the input data
    width_addr : width of the address accessed by a module
    width_runlength : width of the runlength value
    width_size : width of the size value
    width_out_byte : width of output byte
    width_num_bytes : max encoded bytes width

    """
    width_data = len(data_in)
    width_addr = len(write_addr)
    width_num_bytes = len(num_enc_bytes)
    width_runlength = 4
    width_byte = 8
    width_size = width_data.bit_length()

    # used by quantizer to read data from input DRAM
    read_addr = Signal(intbv(0)[width_addr:])
    # output from the input DRAM
    data_in_quantiser = Signal(intbv(0)[width_data:])

    # quantizer data and control streams
    quanti_datastream = QuantIODataStream(width_data, width_addr-1)
    quanto_datastream = QuantIODataStream(width_data, width_addr-1)
    quant_ctrl = QuantCtrl()

    # rle data and control streams
    rle_input_datastream = DataStream(width_data, width_addr-1)
    rle_outputs = BufferDataBus(width_data, width_size, width_runlength)
    rle_config = RLEConfig()

    huffmandatastream = HuffmanDataStream(width_runlength, width_size,
                                          width_data, width_addr-1)
    bufferdatabus = HuffBufferDataBus(width_byte)
    huffmancntrl = HuffmanCntrl()
    img_size = ImgSize(8, 8)
    rle_fifo_empty = Signal(bool(0))

    bs_in_stream = BSInputDataStream(width_byte)
    bs_out_stream = BSOutputDataStream(width_byte, width_num_bytes)
    bs_cntrl = BScntrl()

    ready_rle = Signal(bool(0))
    ready_huffman = Signal(bool(0))

    # control signals
    wait = Signal(intbv(0)[3:])
    enable_huff_read = Signal(bool(0))
    counter = Signal(intbv(0)[3:])
    value = Signal(intbv(3)[4:])
    ready_quant = Signal(bool(0))
    ready_bytestuffer = Signal(bool(0))

    # instantiation of DRAM
    inst_dbuf = dram(clock, data_in, write_addr, read_addr,
                     write_enable, data_in_quantiser)

    @always_seq(clock.posedge, reset=reset)
    def control_ready_valid():
        """control flow that operated between blocks"""

        # initially when the first block enters
        if wait == 0:
            if start:
                quant_ctrl.start.next = True
                quant_ctrl.color_component.next = 1
            else:
                quant_ctrl.start.next = False
                if quant_ctrl.ready:
                    ready.next = True
                    wait.next = 1

        # when both rle and quantizer are ready
        elif wait == 1:
            ready.next = False
            if start:
                rle_config.start.next = True
                quant_ctrl.start.next = True
                quant_ctrl.color_component.next = 2
                rle_config.color_component.next = 1
            else:
                rle_config.start.next = False
                quant_ctrl.start.next = False
                if quant_ctrl.ready:
                    ready_quant.next = True
                if rle_config.ready:
                    ready_rle.next = True

                if ready_quant and ready_rle:
                    ready.next = True
                    ready_rle.next = False
                    ready_quant.next = False
                    wait.next = 2

        # when quantizer, rle and huffman are ready
        elif wait == 2:
            ready.next = False
            if start:
                rle_config.start.next = True
                quant_ctrl.start.next = True
                huffmancntrl.start.next = True
                huffmancntrl.color_component.next = 1
                rle_config.color_component.next = 2
                quant_ctrl.color_component.next = 3
            else:
                rle_config.start.next = False
                quant_ctrl.start.next = False
                huffmancntrl.start.next = False
                if quant_ctrl.ready:
                    ready_quant.next = True
                if rle_config.ready:
                    ready_rle.next = True
                if huffmancntrl.ready:
                    ready_huffman.next = True

                if ready_quant and ready_rle and ready_huffman:
                    ready.next = True
                    ready_rle.next = False
                    ready_quant.next = False
                    ready_huffman.next = False
                    wait.next = 3

        # when all the four blocks are ready
        elif wait == 3:
            ready.next = False
            if start:
                rle_config.start.next = True
                quant_ctrl.start.next = True
                huffmancntrl.start.next = True
                bs_cntrl.start.next = True

                if huffmancntrl.color_component == 3:
                    huffmancntrl.color_component.next = 1
                if quant_ctrl.color_component == 3:
                    quant_ctrl.color_component.next = 1
                if rle_config.color_component == 3:
                    rle_config.color_component.next = 1
                else:
                    huffmancntrl.color_component.next = (
                        huffmancntrl.color_component + 1)

                    rle_config.color_component.next = (
                        rle_config.color_component + 1)

                    quant_ctrl.color_component.next = (
                        quant_ctrl.color_component + 1)

            else:
                rle_config.start.next = False
                quant_ctrl.start.next = False
                huffmancntrl.start.next = False
                bs_cntrl.start.next = False

                if quant_ctrl.ready:
                    ready_quant.next = True
                if rle_config.ready:
                    ready_rle.next = True
                if huffmancntrl.ready:
                    ready_huffman.next = True
                if bs_cntrl.ready:
                    ready_bytestuffer.next = True

                if (ready_quant and ready_rle) and (
                        ready_huffman and ready_bytestuffer):

                    ready.next = True
                    ready_rle.next = False
                    ready_quant.next = False
                    ready_huffman.next = False
                    ready_bytestuffer.next = False
                    wait.next = 3

    @always_comb
    def assign_quant_in():
        """quantizer and DRAM connections"""
        quanti_datastream.data.next = data_in_quantiser
        read_addr.next = concat(quanti_datastream.buffer_sel,
                                quanti_datastream.addr.next)

    # instantiation of quantizer module
    inst_quant = quantizer(clock, reset, quanti_datastream,
                           quant_ctrl, quanto_datastream)

    @always_comb
    def assign_rle_in():
        """connections between quantizer and RLE module"""
        rle_input_datastream.data_in.next = quanto_datastream.data
        quanto_datastream.addr.next = concat(rle_input_datastream.buffer_sel,
                                             rle_input_datastream.read_addr)

        quanto_datastream.buffer_sel.next = rle_input_datastream.buffer_sel

    # instantiation of RLE module
    inst_rle = rlencoder(clock, reset, rle_input_datastream,
                         rle_outputs, rle_config)


    @always_seq(clock.posedge, reset=reset)
    def counter_huff():
        """counter that increments till three"""
        if enable_huff_read:
            counter.next = counter + 1

        if huffmancntrl.start:
            enable_huff_read.next = True
            value.next = 4
            rle_outputs.read_enable.next = True

        else:
            rle_outputs.read_enable.next = False

        if counter >= value:
            rle_outputs.read_enable.next = not rle_outputs.read_enable
            counter.next = 0
            value.next = 2
            if huffmancntrl.ready:
                rle_outputs.read_enable.next = False
                enable_huff_read.next = False

        if huffmancntrl.ready:
            rle_outputs.read_enable.next = False
            enable_huff_read.next = False


    @always_comb
    def assign_huffman_in():
        """"Huffman Module and RLE Module connections"""
        huffmandatastream.runlength.next = rle_outputs.runlength
        huffmandatastream.vli_size.next = rle_outputs.size
        huffmandatastream.vli.next = rle_outputs.amplitude
        huffmandatastream.data_valid.next = rle_outputs.read_enable
        rle_fifo_empty.next = rle_outputs.fifo_empty
        rle_outputs.buffer_sel.next = huffmandatastream.buffer_sel

    # instantiation of Huffman Module
    inst_huffman = huffman(clock, reset, huffmancntrl, bufferdatabus,
                           huffmandatastream, img_size, rle_fifo_empty)

    @always_comb
    def assign_bs_in():
        """connections between ByteStuffer and Huffman Module"""
        bs_in_stream.data_in.next = bufferdatabus.huf_packed_byte
        bs_in_stream.fifo_empty.next = bufferdatabus.fifo_empty
        bufferdatabus.read_req.next = bs_in_stream.read

    @always_comb
    def assig_buff():
        """assign buffers between ByteStuffer and Huffman"""
        bufferdatabus.buffer_sel.next = bs_in_stream.buffer_sel

    # instantiation of Byte stuffer
    inst_bytestuffer = bytestuffer(clock, reset, bs_in_stream,
                                   bs_out_stream, bs_cntrl, num_enc_bytes)

    @always_comb
    def assign_out():
        """output from the Backend Module"""
        data_out.next = bs_out_stream.byte
        addr.next = bs_out_stream.addr

    return (inst_dbuf, control_ready_valid, assign_quant_in,
            inst_quant, assign_rle_in, inst_rle, counter_huff,
            assign_huffman_in, inst_huffman, assign_bs_in,
            assig_buff, inst_bytestuffer, assign_out)
