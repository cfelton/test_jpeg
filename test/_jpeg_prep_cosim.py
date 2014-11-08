
import os
from argparse import Namespace
from myhdl import *
from _jpeg_filelist import filelist_v1
from _jpeg_filelist import filelist_v2

def prep_cosim(clock, reset, jpeg_intf, args=None):
    """
    """
    global filelist_v1, filelist_v2

    # build the first JPEG encoder
    # @note: this encoder is still being converted to 
    #    Verilog, for now just build
    if not args.build_skip_v1:
        for ff in filelist_v1:        
            cmd = "iverilog -g2005 %s" % (ff,)
            os.system(cmd)

    # build the second JPEG encoder
    # @todo: use subprocess, check the return and the "log"
    #   to verify it build correctly.
    files = filelist_v2 + ['tb_jpegenc.v']
    cmd = "iverilog -o jpegenc_v2 %s " % ("".join(files))
    print("compiling ...")
    os.system(cmd)

    if not os.path.exists('vcd'):
        os.makedirs('vcd')

    if args.build_only:
        return None

    print("cosimulation setup ...")
    cmd = "vvp -m ./myhdl.vpi jpegenc_v2"

    gcosim = Cosimulation(cmd,
        clock = clock,
        reset = reset,

        # encoder 1

        # encoder 2
        jpeg_eof = jpeg_intf.end_of_file_signal,
        jpeg_en = jpeg_intf.enable,
        jpeg_dati = jpeg_intf.data_in,
        jpeg_bits = jpeg_intf.jpeg_bitstream,
        jpeg_rdy = jpeg_intf.data_ready,
        jpeg_eof_cnt = jpeg_intf.end_of_file_bitstream_count,
        jpeg_eof_p = jpeg_intf.eof_data_partial_ready
                          
        # encoder (future versions)
    )

    return gcosim
                          

if __name__ == '__main__':
    args = Namespace(
        build_only=True,
        build_skip_v1=False,
        build_skip_v2=False
    )
    
    prep_cosim(Signal(bool(0)), 
               ResetSignal(0, 0, False),
               None,
               args)