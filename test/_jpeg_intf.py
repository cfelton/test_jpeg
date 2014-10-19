
from myhdl import *

class JPEGEnc(object):
    end_of_file_signal = Signal(bool(0))
    enable = Signal(bool(0))
    data_in = Signal(intbv(0)[24:])
    jpeg_bitstream = Signal(intbv(0)[32:])
    data_ready = Signal(bool(0))
    end_of_file_bitstream_count = Signal(intbv(0)[4:])
    eof_data_partial_ready = Signal(bool(0))
        