

def color_conversion(glbl, pixel_in, pixel_out):
    """

    (arguments == ports)
    Argumentss:
        glbl (Global):
        pixel_in (PixelStream):
        pixel_out ():

    myhdl convertible
    """


def transformer_twod(glbl, sample_input, matrix_outputs, block_size=(8, 8)):
    """A two-dimension (2D) transform block

    (arguments == ports)
    Arguments:
        sample_input (PixelStream):
        matrix_outputs (ImageBlock):

    Parameters:
        block_size (tuple):

    myhdl convertible
    """
    pass


def transformer_oned(glbl, sample_input, block_output, block_size=8):
    """A one-dimension (1D) transform block

    This ~~module~~ block will stream in a sample at a time, collecting
    `block_size` input samples before producing the transform.

    (arguments == ports)
    Arguments:
        sample_input (DataStream): input sample stream
        block_output (DataBlock): output transformed block.

    Parameters:
        block_size: the size of the transform, the transform will be
            computed on ``block_size`` data points, typically the
            *N* in the math equations.

    myhdl convertible
    """
    pass
