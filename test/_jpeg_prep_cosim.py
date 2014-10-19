
import os
from myhdl import *
from _jpeg_filelist import filelist_v2

def prep_cosim(clock, reset, jpeg_intf, args=None):
    """
    """
    global filelist_v2
    files = filelist_v2 + ['tb_jpegenc.v']
    cmd = "iverilog -o jpegenc_v2 %s " % ("".join(files))
    print("compiling ...")
    os.system(cmd)

    if not os.path.exists('vcd'):
        os.makedirs('vcd')

    print("cosimulation setup ...")
    cmd = "vvp -m ./myhdl.vpi jpegenc_v2"

    gcosim = Cosimulation(cmd,
        clock = clock,
        reset = reset,
        jpeg_eof = jpeg_intf.end_of_file_signal,
        jpeg_en = jpeg_intf.enable,
        jpeg_dati = jpeg_intf.data_in,
        jpeg_bits = jpeg_intf.jpeg_bitstream,
        jpeg_rdy = jpeg_intf.data_ready,
        jpeg_eof_cnt = jpeg_intf.end_of_file_bitstream_count,
        jpeg_eof_p = jpeg_intf.eof_data_partial_ready)

    return gcosim
                          
    