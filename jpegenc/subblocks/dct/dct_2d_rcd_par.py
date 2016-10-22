
import myhdl
from rhea import Global
from jpegenc.interfaces import YCbCrStream


@myhdl.block
def dct2_rcd_par(glbl, color_in, dct_out, csb=None, cso=None):
    """DCT 2D parallel row-column decomposition.

    This is a parallel implementation of the row-column decomposition
    DCT.  This is best used when a whole row from the image block
    (matrix) is transferred in parallel (e.g. 8 pixels).

    Args:
        glbl (Global):
        color_in (YCbCrStream):
        dct_out ():
        csb (MemoryMapped):
        cso (ControlStatusBase):

    Returns:

    """
    assert isinstance(glbl, Global)
    assert isinstance(color_in, YCbCrStream)
    assert isinstance(dct_out, object)
    assert isinstance(csb, (type(None), ))    # MemoryMapped
    assert isinstance(cso, (type(None), ))    # ControlStatusObject

    # @todo: add a warning if the number of pixels in the input
    #     interfaces is less than the


