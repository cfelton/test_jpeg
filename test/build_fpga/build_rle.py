import argparse
from argparse import Namespace

import myhdl
from myhdl import Signal, ResetSignal, intbv, always, always_comb

from rhea import Signals
from rhea.cores.misc import io_stub
from rhea.build import get_board

from jpegenc.subblocks.rle import rlencoder
from jpegenc.subblocks.rle import DataStream, BufferDataBus, RLEConfig

from board_map import board_map


@myhdl.block
def rlencoder_stub(clock, sdi, sdo, reset=None):
    """This is a top-level wrapper for the jpegenc run-length-encoder

    """

    if reset is None:
        reset = ResetSignal(1, active=0, async=True)

    # ?? the input is not streaming but wants access to
    # a RAM.
        

        



