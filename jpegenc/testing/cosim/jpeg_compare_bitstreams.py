from __future__ import division, print_function

import os
from PIL import Image


def compare_bitstreams(ipth, bitstreams):
    """
    This function will compare the generated bit-streams with the 
    software generated JPEG bitstream from the original file.
    """
    if os.path.isfile(ipth):
        img = Image(ipth)

        # @todo: complete this function, the following is not valid
        assert img == bitstreams

