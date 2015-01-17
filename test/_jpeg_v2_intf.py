
from __future__ import division
from __future__ import print_function

import datetime 

from PIL import Image

from myhdl import *
from _SignalQueue import SignalQueue

from _jpeg_intf import JPEGEnc


class JPEGEncV2(JPEGEnc):
    
    def __init__(self, clock, reset, args=None):
        """
        """

        JPEGEnc.__init__(self, clock, reset, args=args)

        # ---[encoder interface]---
        # the default interface (Signals) to the jpeg encoder
        self.end_of_file_signal = Signal(bool(0))               # input
        self.enable = Signal(bool(0))                           # input
        self.data_in = Signal(intbv(0)[24:])                    # input
        self.jpeg_bitstream = Signal(intbv(0)[32:])             # output
        self.data_ready = Signal(bool(0))                       # output
        self.end_of_file_bitstream_count = Signal(intbv(0)[5:]) # output
        self.eof_data_partial_ready = Signal(bool(0))           # output
  
        # set the encoder parameters 
        self.block_size = (8,8,)
        self.nout = args.nout
        self.start_time = args.start_time


    def stream_img_in(self):
        """ 
        A transactor to take an image and stream it to the jpeg encoder.

        This encoder (design2) requires a 8x8 block be streamed in 
        after the block is streamed in it needs to wait 33 clock 
        cycles before the next 8x8 can be streamed in.
        """
        
        @instance
        def t_bus_in():

            while True:
                imglst = [None]
                yield self._inq.get(imglst, block=True)
                self.pxl_done.next = False
                img = imglst[0]
                nx,ny = img.size
                print("V2: encode image %s %d x %d" % (str(img), nx, ny,))
                for yy in xrange(0, ny, 8):
                    for xx in xrange(0, nx, 8):
                        self.enable.next = True
                        
                        #print("   sending block %3d,%3d out of %3d,%3d" % (xx, yy, nx, ny))
                        if yy >= ny-8 and xx >= nx-8:
                            self.end_of_file_signal.next = True

                        # send the 8x8 block
                        for yb in xrange(8):
                            for xb in xrange(8):                                
                                r,g,b = img.getpixel((xx+xb,yy+yb,))
                                self.data_in.next[24:16] = b
                                self.data_in.next[16:8] = g
                                self.data_in.next[8:0] = r
                                yield self.clock.posedge

                        # after each 8x8 block the encoder requires
                        # 33 clocks before the next block
                        for ii in xrange(33):
                            yield self.clock.posedge

                        self.enable.next = False
                        yield self.clock.posedge                                        
                        

                self.pxl_done.next = True
                self.data_in.next = 0
                self.end_of_file_signal.next = False
                end_time = datetime.datetime.now()
                dt = end_time - self.start_time
                print("V2: end pixel stream %s " % (dt,))


        return t_bus_in


    def stream_jpg_out(self):
        """ capture the encoded bitstream
        """
        
        @instance
        def t_bus_out():
            ii = 0
            do_capture = True
            Ncyc = 100
            while do_capture:
                yield self.clock.posedge
                #yield self.data_ready.posedge
                if self.data_ready:
                    self._bitstream.append(int(self.jpeg_bitstream))
                    ii += 1
                    if ii%Ncyc == 0: 
                        print("V2: %4d output, latest %08X" % (ii, int(self.jpeg_bitstream,)))

                if ((self.nout > 0 and ii >= self.nout) or 
                    self.eof_data_partial_ready):
                    yield self._outq.put(self._bitstream)
                    do_capture = False
                    
                    end_time = datetime.datetime.now()
                    dt = end_time - self.start_time
                    print("V2: end of bitstream %s " % (dt,))
                    self.enc_done.next = True

        return t_bus_out


