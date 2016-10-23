
import myhdl
from rhea import Global
from jpegenc.interfaces import YCbCrStream


@myhdl.block
def dct2_rcd(glbl, color_in, dct_out, csb=None, cso=None):
    """ DCT 2D row-column decomposition implementation.

    This block implements the DCT 2D row-column decomposition DCT-2D
    [1], this block conforms to the interfaces defined for the
    JPEG encoder.

    Arguments (Ports):
        glbl (Global): common signals, clock, reset, enable
        color_in (YCbCrStream): input color stream
        dct_out (???):
        csb (MemoryMapped):
        cso (ControlStatus):

    Parameters:
        block_size (tuple): image block size

    myhdl convertible

    [1]: A. Madisetti and A. N. Willson, "A 100 MHz 2-D 8×8 DCT/IDCT
         processor for HDTV applications," in IEEE Transactions on
         Circuits and Systems for Video Technology,
         vol. 5, no. 2, pp. 158-165, Apr 1995. doi: 10.1109/76.388064
         URL: http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=388064&isnumber=8802

    """
    assert isinstance(glbl, Global)
    assert isinstance(color_in, YCbCrStream)
    assert isinstance(dct_out, object)
    assert isinstance(csb, (type(None), ))    # MemoryMapped
    assert isinstance(cso, (type(None), ))    # ControlStatusObject

