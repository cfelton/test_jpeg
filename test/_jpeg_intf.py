from __future__ import division
from __future__ import print_function

from PIL import Image

from myhdl import *
from _SignalQueue import SignalQueue
    
                 
class JPEGEnc(object):

    def __init__(self, clock, reset, args=None):
        """
        """

        # @todo: the following parameters should be part of the args
        self.pixel_nbits = 24
        self.block_size  = (8,8,)

        self.clock = clock
        self.reset = reset

        # ---[generic interface]---
        # pixel stream input
        self.sof = Signal(bool(0))        # start of figure/frame
        self.eof = Signal(bool(0))        # end of figure/frame
        self.pxl = Signal(intbv(0)[24:])  # pixel bus
        self.pbv = Signal(bool(0))        # pixel bus valid
        
        # bitstream output
        self.sob = Signal(bool(0))        # start of bitstream
        self.eob = Signal(bool(0))        # end of bitstream
        self.bst = Signal(intbv(0)[32:])  # jpeg bitstream
        self.pwrd = Signal(bool(0))       # partial word (always last)
        self.pcnt = Signal(intbv(0)[4:])  # valid bits in last (partial) word

        # ---[the trasactor interfaces]---
        self.done = Signal(bool(0))
        self._inq = SignalQueue()
        self._outq = SignalQueue()
        self._bitstream = []

    def _ext8(self, img):
        """ extend an image to be a multiple of 8 pixels
        """
        w,h = img.size
        w8,h8 = w+(8-w%8), h+(8-h%8)
        nimg = Image.new("RGB", (w8,h8,))
        nimg.paste(img, (0,0,))
        return nimg


    def put_image(self, img):
        """
        """
        assert img.mode == 'RGB'
        nimg = self._ext8(img)
        self._bitstream = []
        yield self._inq.put(nimg)
        yield self.clock.posedge


    def get_jpeg(self, bic):
        """
        """
        assert isinstance(bic, list)
        yield self._outq.get(bic, block=True)


    # the specific interfaces need to define: 
    #  - stream_img_in 
    #  - stream_jpg_out

    def stream_img_in(self):
        """ stream image in adapter """
        raise NotImplemented

    def stream_jpg_out(self):
        """ stream jpeg bitstream out """
        raise NotImplemented

    def get_gens(self):
        d = self.stream_img_in()
        m = self.stream_jpg_out()
        return d,m