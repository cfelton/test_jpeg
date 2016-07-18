
from argparse import Namespace

import myhdl
from myhdl import Signal, ResetSignal, intbv, always, always_comb

from rhea import Signals
from rhea.cores.misc import io_stub
from rhea.build import get_board

from jpegenc.subblocks.common import input_interface, outputs_2d
from jpegenc.subblocks import dct_2d


@myhdl.block
def mdct_stub(clock, sdi, sdo, reset=None):
    """This is a top-level wrapper around the jpegenc DCT2.

    This module is used to simply test the synthesis results 
    of the DCT2 subblock.  This module (block) is not functional,
    the ouptut will not be captured (probably) but this block 
    maintains all the of the inputs and outputs.
    """

    if reset is None:
        reset = ResetSignal(1, active=0, async=True)

    # the following should be something like, reused common
    # interface types.
    #     ycbcr = YCbCrStream()
    #     imgfreq = ImageBlock(size=(8,8), data_width=precision)
    #
    # And there should be a helper function to determine the 
    # precision based on some domain property (how would a system
    # designer define it) ...

    # the inputs to the DCT2
    y = input_interface()    
    cb = input_interface()
    cr = input_interface()

    # the outputs from the DCT2
    yf = outputs_2d()
    cbf = outputs_2d()
    crf = outputs_2d()

    # stub out the inputs and outputs 
    ni, no = len(y.data_in), yf.out_range
    iports = Signals(intbv(0)[ni:0], 3)
    oports = Signals(intbv(0)[no:0], 3*(yf.N**2))
    valid = Signal(bool(0))

    io_inst = io_stub(clock, reset, sdi, sdo, iports, oports, valid)

    # assign the inputs and outputs to the subblock (DCT2)
    @always_comb
    def beh_assign_inputs():
        y.data_in.next = iports[0]
        y.data_valid.next = valid
        cb.data_in.next = iports[1]
        cb.data_valid.next = valid
        cr.data_in.next = iports[2]
        cr.data_valid.next = valid

    block_size = yf.N**2
    for oi in (yf, cbf, crf):
        assert block_size == oi.N**2

    # offset into the output port list of signals
    b1offset = block_size
    b2offset = 2*block_size

    # this adds another set of output registers
    @always(clock.posedge)
    def beh_assign_outputs():
        if yf.data_valid:
            for ii in range(block_size):
                oports[ii].next = yf.out_sigs[ii]            

        if cbf.data_valid:
            for ii in range(block_size):
                oports[ii+b1offset].next = cbf.out_sigs[ii]

        if crf.data_valid:
            for ii in range(block_size):
                oports[ii+b2offset].next = crf.out_sigs[ii]

    dct2_y_inst = dct_2d(y, yf, clock, reset)
    dct2_cb_inst = dct_2d(cb, cbf, clock, reset)
    dct2_cr_inst = dct_2d(cr, crf, clock, reset)

    return myhdl.instances()
        
        
def run_flow(args=None):
    if args is None:
        # args = Namespace(brd='nexys_video')
        args = Namespace(brd='zybo')

    # define a port to map the serial IO to.
    fpga_map = {
        'zybo': 'pmod_jb',
        'nexys_video': 'pmod_jb',
        'atlys': 'pmod',
        'de0nano': 'gpio',
    }

    brd = get_board(args.brd)
    port = fpga_map[args.brd]
    brd.add_port_name('sdi', port, 0)
    brd.add_port_name('sdo', port, 1)

    flow = brd.get_flow(top=mdct_stub)
    flow.run()
    info = flow.get_utilization()

    return info


if __name__ == '__main__':
    run_flow()
        
    