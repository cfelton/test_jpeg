
from __future__ import division
from __future__ import print_function

from PIL import Image

from myhdl import *
from _SignalQueue import SignalQueue

from _jpeg_intf import JPEGEnc


class JPEGEncV1(JPEGEnc):
    
    def __init__(self, clock, reset, args=None):
        """
        """

        JPEGEnc.__init__(self, clock, reset, args=args)

        # ---[encoder interface]---
        # these are the encoder v1 interface signals
        #self.mmbus = OPBBus()
        pixel_nbits = self.pixel_nbits
        self.iram_wdata = Signal(intbv(0)[pixel_nbits:])  # input
        self.iram_wren = Signal(bool(0))                  # input
        self.iram_fifo_afull = Signal(bool(0))            # output
        self.ram_byte = Signal(intbv(0)[8:])              # output
        self.ram_wren = Signal(bool(0))                   # output
        self.ram_wraddr = Signal(intbv(0)[24:])           # output
        self.almost_full = Signal(bool(0))                # input
        self.frame_size = Signal(intbv(0)[24:])           # output


        # set the encoder parameters 
        self.block_size = (16,8,)
        
        
    def stream_img_in(self):
        """
        A transactor to take an image and stream it to the jpeg encoder.
        
        This encoder (design1) requires a 12x8 block to be streamed in,
        the pixels are streamed into the FIFO until the FIFO is full 
        (the encoder actually handles extracting the 12x8?).
        """


        @instance
        def t_bus_in():
            while True:
                imglst = [None]
                yield self._inq.get(imglst, block=True)
                self.done.next = False
                img = imglst[0]
                nx,ny = img.size
                print("encode image %s %d x %d" % (str(img), nx, ny,))
                for yy in xrange(0, ny):
                    for xx in xrange(0, nx):
                        self.iram_wren.next = False
                        while self.iram_fifo_afull:
                            yield self.clock.posedge

                        # clear to write a pixel in
                        r,g,b = img.getpixel((xx,yy,))
                        self.iram_wren.next = True
                        self.iram_wdata.next[24:16] = b
                        self.iram_wdata.next[16:8] = g
                        self.iram_wdata.next[8:0] = r
                        yield self.clock.posedge

                self.iram_wren.next = False
                self.iram_wdata.next = 0
                self.done.next = True

        return t_bus_in


    def stream_jpg_out(self):
        """
        """

        @instance
        def t_bus_out():
            ii = 0
            while True:
                yield self.clock.posedge
                if self.ram_wren:
                    self._bitstream.append(self.ram_byte)
                    ii += 1

        return t_bus_out

                            
                