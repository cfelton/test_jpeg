
from __future__ import division
from __future__ import print_function

from PIL import Image

from myhdl import *
from _SignalQueue import SignalQueue

from _jpeg_intf import JPEGEnc


class JPEGEncV1(object):
    
    def __init__(self, clock, reset):
        """
        """

        self.clock = clock
        self.reset = reset
    