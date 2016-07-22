
import argparse
from argparse import Namespace

import myhdl
from myhdl import Signal, ResetSignal, intbv, always, always_comb, concat

from rhea import Signals
from rhea.cores.misc import io_stub
from rhea.build import get_board

# need to resolve the spelling inconsitency 
from jpegenc.subblocks import quantizer_top
from jpegenc.subblocks.quantizer import QuantIDataStream
from jpegenc.subblocks.quantizer import QuantCtrl
from jpegenc.subblocks.quantizer import QuantConfig
from jpegenc.subblocks.quantizer import QuantODataStream

from board_map import board_map



@myhdl.block
def stub_quantizer(clock, sdi, sdo, reset=None):
    """
    """

    if reset is None:
        reset = ResetSignal(1, active=0, async=True)

    # the quantizer input wants a RAM??, the QuantIDataStream
    # needs defaults for width and addr
    # why separate interfaces (type) for the input and output ???
    qi = QuantIDataStream(width=12, addr=8)   # 
    ctl = QuantCtrl()           # for an object, just call it QuantControl
    cfg = QuantConfig(12, 8)
    qo = QuantODataStream(width=12, addr=8)   # 

    
    iports = Signals(intbv(0)[8:0], 6)
    oports = Signals(intbv(0)[8:0], 6)
    valid = Signal(bool(0))

    io_inst = io_stub(clock, reset, sdi, sdo, iports, oports, valid)

    @always_comb
    def beh_assign_inputs():
        d0 = iports[0]
        d1 = iports[1]
        qi.data_in.next = concat(d1[4:0], d0)
        qo.read_addr.next = iports[3]

    @always_comb
    def beh_assign_outputs():
        oports[0].next = qi.read_addr
        oports[1].next = qo.data_out

    
    quant_inst = quantizer_top(clock, reset, qi, ctl, cfg, qo)

    return myhdl.instances()
    