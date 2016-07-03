
from __future__ import division, print_function, absolute_import

import datetime
import struct

from PIL import Image

from myhdl import *

from .signal_queue import SignalQueue
from .opb import OPBBus
from .jpeg_intf import JPEGEnc
from .jpeg_roms import rom_lum, rom_chr


class JPEGEncV1(JPEGEnc):
    
    def __init__(self, clock, reset, args=None):
        """
        """

        JPEGEnc.__init__(self, clock, reset, args=args)
        self.args = args

        # ---[encoder interface]---
        # these are the encoder v1 interface signals
        pixel_nbits = self.pixel_nbits
        self.iram_wdata = Signal(intbv(0)[pixel_nbits:])  # input
        self.iram_wren = Signal(bool(0))                  # input
        self.iram_fifo_afull = Signal(bool(0))            # output
        self.ram_byte = Signal(intbv(0)[8:])              # output
        self.ram_wren = Signal(bool(0))                   # output
        self.ram_wraddr = Signal(intbv(0)[24:])           # output
        self.almost_full = Signal(bool(0))                # input
        self.frame_size = Signal(intbv(0)[24:])           # output
        
        self.opb = OPBBus(clock, reset)
        self._enc_done = Signal(bool(0))

        # set the encoder parameters 
        self.block_size = (16,8,)

        self.nout = args.nout
        self.start_time = args.start_time

    def initialize(self, luminance=1, chrominance=1):
        """ initialize the encoder 

        Arguments
        ---------
          luninance : 1, .85, .75 or .5
          chrominance : 1, .85, .75 or .5
        """
        # lum address
        offset = {1: 0x00, .85: 0x40, .75: 0x80, .50: 0xC0}
        lbase, cbase = 64*offset[luminance], 64*offset[chrominance]

        # program the luminance table
        for ii, off in enumerate(range(lbase,lbase+64)):
            addr = 0x00000100 + ii*4
            # print("[%8d] V1 init %8X --> %8X" % (now(), addr, rom_lum[off]))
            yield self.opb.write(addr, rom_lum[off])

        # program the chrominace table
        for ii, off in enumerate(range(cbase, cbase+64)):
            addr = 0x00000200 + ii*4
            yield self.opb.write(addr, rom_chr[off])

    def check_done(self, done):        
        assert isinstance(done, SignalType)
        dn = False
        # read the status register
        rval = Signal(intbv(0)[32:])        
        yield self.opb.read(0x0C, rval)
        
        if (rval & 0x01) == 0x01:
            dn = False
        elif (rval & 0x02) == 0x02:
            dn = True
        else:
            # hmmm, not done and not busy?
            dn = True

        done.next = dn
        self._enc_done.next = dn
        # print("%8d checked done %X %d->%d" % (now(), rval,
        #                                   self._enc_done.val, self._enc_done.next))

    def stream_img_in(self):
        """
        A transactor to take an image and stream it to the jpeg encoder.
        
        This encoder (design1) requires a 12x8 block to be streamed in,
        the pixels are streamed into the FIFO until the FIFO is full.
        """

        @instance
        def t_bus_in():
            while True:
                # get the an image to be streamed to the encoder
                imglst = [None]
                yield self._inq.get(imglst, block=True)
                self.pxl_done.next = False
                img = imglst[0]
                nx, ny = img.size

                # this encoder needs some commands via the control bus (memmap)
                # to start encoding, need to program in the requested (?) x and y 
                wval = concat(intbv(nx)[16:], intbv(ny)[16:])
                yield self.opb.write(0x04, wval)
                # write a start request, RGB=11, sof=1
                yield self.opb.write(0x00, 0x07)

                # stream the image to the encoder
                print("V1: encode image %s %d x %d" % (str(img), nx, ny,))
                self.img_size = img.size

                self.encode_start_time = now()
                for yy in range(0, ny):
                    for xx in range(0, nx):
                        self.iram_wren.next = False
                        while self.iram_fifo_afull:
                            yield self.clock.posedge

                        # clear to write a pixel in
                        r, g, b = img.getpixel((xx,yy,))
                        self.iram_wren.next = True
                        self.iram_wdata.next[24:16] = b
                        self.iram_wdata.next[16:8] = g
                        self.iram_wdata.next[8:0] = r
                        yield self.clock.posedge

                self.iram_wren.next = False
                self.iram_wdata.next = 0     

                # writing is complete (not ready for next frame yet)
                self.pxl_done.next = True       
                end_time = datetime.datetime.now()
                dt = end_time - self.start_time
                print("V1: end pixel stream %s " % (dt,))

                # wait for the encoder to be completed
                self.iram_wdata.next = 0
                cd = Signal(bool(0))
                while not cd:
                    yield self.check_done(cd)
                    yield self.clock.posedge

                # at this point the next frame can be sent
                self.encode_end_time = now()
                # display the max frame rate
                dt = self.encode_end_time - self.encode_start_time
                self.max_frame_rate = 1/(dt * 1e-9)
                print("V1: max frame rate %8.3f frames/sec" % (self.max_frame_rate,))

        return t_bus_in

    def stream_jpg_out(self):
        """ capture the encoded bitstream
        """
        # save the raw bitstream to a file
        jfp = open('jpegv1.jpg', 'wb')

        @instance
        def t_bus_out():
            ii = 0
            do_capture = True
            Ncyc = self.args.ncyc
            word = 0
            nwords = 0

            # capture the output from the encoder
            while do_capture:
                yield self.clock.posedge
                if self.ram_wren:
                    # put in 32bit values, first in time MSB
                    nb = int(self.ram_byte)
                    word = (word << 8) | nb
                    ii += 1
                    # when 4 bytes received save it
                    if (ii%4) ==  0:
                        self._bitstream.append(word)
                        nwords += 1
                        if nwords%Ncyc == 0:
                            print("V1: %6d output, latest %08X" % (nwords, self._bitstream[-1],))

                        # write this word to the file
                        fword = struct.pack('>L', word)
                        #print("V1: {:08X}, {}".format(word, fword))
                        jfp.write(fword)
                        word = 0

                #if ii > 10:
                if ((self.nout > 0 and ii >= self.nout) or self._enc_done):
                    yield self._outq.put(self._bitstream)
                    do_capture = False

                    end_time = datetime.datetime.now()
                    dt = end_time - self.start_time
                    print("V1: end of bitstream %s " % (dt,))
                    self.enc_done.next = True
                    jfp.close()

        return t_bus_out
