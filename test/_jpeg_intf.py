from __future__ import division
from __future__ import print_function

from PIL import Image

from myhdl import *
from _SignalQueue import SignalQueue

def _ext8(img):
    """ extend an image to be a multiple of 8 pixels
    """
    w,h = img.size
    w8,h8 = w+(8-w%8), h+(8-h%8)
    nimg = Image.new("RGB", (w8,h8,))
    nimg.paste(img, (0,0,))
    return nimg


# @todo: create a generic base class with generic signals to 
#    support the different versions.  Create specific classes
#    for each encoder.  Each encoder will have a small adapter
#    to drive the specific encoders interface
class _JPEGEnc(object):
    # pixel stream input
    sof = Signal(bool(0))        # start of figure/frame
    eof = Signal(bool(0))        # end of figure/frame
    pxl = Signal(intbv(0)[24:])  # pixel bus
    pbv = Signal(bool(0))        # pixel bus valid
    # bitstream output
    sob = Signal(bool(0))        # start of bitstream
    eob = Signal(bool(0))        # end of bitstream
    bst = Signal(intbv(0)[32:])  # jpeg bitstream
    pwrd = Signal(bool(0))       # partial word (always last)
    pcnt = Signal(intbv(0)[4:])  # valid bits in last (partial) word

    
                 
class JPEGEnc(object):

    def __init__(self, clock, reset):
        """
        """

        self.clock = clock
        self.reset = reset

        # encoder interface
        # the default interface (Signals) to the jpeg encoder
        self.end_of_file_signal = Signal(bool(0))
        self.enable = Signal(bool(0))
        self.data_in = Signal(intbv(0)[24:])
        self.jpeg_bitstream = Signal(intbv(0)[32:])
        self.data_ready = Signal(bool(0))
        self.end_of_file_bitstream_count = Signal(intbv(0)[5:])
        self.eof_data_partial_ready = Signal(bool(0))
        self.done = Signal(bool(0))

        self._inq = SignalQueue()
        self._outq = SignalQueue()
        self._bitstream = []


    def put_image(self, img):
        """
        """
        assert img.mode == 'RGB'
        nimg = _ext8(img)
        self._bitstream = []
        yield self._inq.put(nimg)
        yield self.clock.posedge


    def get_jpeg(self, bic):
        """
        """
        assert isinstance(bic, list)
        yield self._outq.get(bic, block=True)


    def stream_img_in(self):
        """ 
        A transactor to take an image and stream it to the jpeg encoder.

        The design2 jpeg encoder requires 8x8 inputs
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
                        

                self.done.next = True
                self.data_in.next = 0
                self.end_of_file_signal.next = False

        return t_bus_in


    def stream_img_out(self):
        """
        """
        
        @instance
        def t_bus_out():
            ii = 0
            while True:
                yield self.clock.posedge
                #yield self.data_ready.posedge
                if self.data_ready:
                    self._bitstream.append(self.jpeg_bitstream)                
                    ii += 1

                #if ii > 10:
                if self.eof_data_partial_ready:
                    yield self._outq.put(self._bitstream)

        return t_bus_out

    def get_gens(self):
        d = self.stream_img_in()
        m = self.stream_img_out()
        return d,m