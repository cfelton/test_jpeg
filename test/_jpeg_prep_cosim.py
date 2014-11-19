
import os
from argparse import Namespace
from myhdl import *
from _jpeg_filelist import filelist_v1
from _jpeg_filelist import filelist_v2

def prep_cosim(clock, reset, jpgv1, jpgv2, args=None):
    """
    """
    global filelist_v1, filelist_v2

    # build the first JPEG encoder
    # @note: this encoder is still being converted to 
    #    Verilog, for now just build
    if not args.build_skip_v1:
        # @todo: save std* and create log
        cmd = "iverilog -g2005 -o jpegenc_v1 %s" % (" ".join(filelist_v1))
        print("compiling v1 ...")
        os.system(cmd)

    # build the second JPEG encoder
    # @todo: use subprocess, check the return and the "log"
    #   to verify it build correctly.
    cmd = "iverilog -g2005 -o jpegenc_v2 %s " % (" ".join(filelist_v2))
    print("compiling v2 ...")
    os.system(cmd)

    files = ['tb_jpegenc.v']
    cmd = "iverilog -g2005 -o jpegenc %s %s tb_jpegenc.v" % \
    ( 
        " ".join(filelist_v1), 
        " ".join(filelist_v2),
    )
    print("compiling testbench ...")
    os.system(cmd)


    if not os.path.exists('vcd'):
        os.makedirs('vcd')

    if args.build_only:
        return None

    print("cosimulation setup ...")
    cmd = "vvp -m ./myhdl.vpi jpegenc"

    gcosim = Cosimulation(cmd,
        clock = clock,
        reset = reset,

        # encoder 1 (V1, design1)
        j1_iram_wdata      = jpgv1.iram_wdata,
        j1_iram_wren       = jpgv1.iram_wren,
        j1_iram_fifo_afull = jpgv1.iram_fifo_afull,
        j1_ram_byte        = jpgv1.ram_byte,
        j1_ram_wren        = jpgv1.ram_wren,
        j1_ram_wraddr      = jpgv1.ram_wraddr,
        j1_almost_full     = jpgv1.almost_full,
        j1_frame_size      = jpgv1.frame_size,

        # encoder 2 (V2, design2)
        j2_eof        = jpgv2.end_of_file_signal,
        j2_en         = jpgv2.enable,
        j2_dati       = jpgv2.data_in,
        j2_bits       = jpgv2.jpeg_bitstream,
        j2_rdy        = jpgv2.data_ready,
        j2_eof_cnt    = jpgv2.end_of_file_bitstream_count,
        j2_eof_p      = jpgv2.eof_data_partial_ready
                          
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
               None, None,
               args)