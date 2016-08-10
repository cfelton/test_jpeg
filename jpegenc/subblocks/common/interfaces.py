#!/usr/bin/env python
# coding=utf-8

from myhdl import Signal, intbv

class ram_in(object):

    def __init__(self, data_width=24, address_width=10, neg=False):
        self.neg = neg
        self.address_width = address_width
        if(neg):
            self.data_range = 2**data_width
            self.data_in = Signal(intbv(0, min=-self.data_range, max=self.data_range))
        else:
            self.data_width = data_width
            self.data_in = Signal(intbv(0)[data_width:])
        self.write_en = Signal(bool(0))
        self.read_addr = Signal(intbv(0)[address_width:])
        self.write_addr = Signal(intbv(0)[address_width:])

class ram_out(object):

    def __init__(self, data_width=24, neg=False):
        if(neg):
            self.data_range = 2**data_width
            self.data_out = Signal(intbv(0, min=-self.data_range, max=self.data_range))
        else:
            self.data_width = data_width
            self.data_out = Signal(intbv(0)[data_width:])


class block_buffer_in(object):

    def __init__(self, data_width=24):
        self.data_width = data_width
        self.data_in = Signal(intbv(0)[data_width:])
        self.data_valid = Signal(bool(0))
        self.ready_to_output_data = Signal(bool(0))

class block_buffer_out(object):

    def __init__(self, data_width=24):
        self.data_out = Signal(intbv(0)[data_width:])
        self.data_valid = Signal(bool(0))
        self.write_all = Signal(bool(0))
        self.read_all = Signal(bool(0))

class triple_buffer_in(object):

    def __init__(self, data_width=24):
        self.data_width = data_width
        self.data_in = Signal(intbv(0)[data_width:])
        self.data_valid = Signal(bool(0))

class triple_buffer_out(object):

    def __init__(self, data_width=24):
        self.data_width = data_width
        self.data_out = Signal(intbv(0)[data_width:])
        self.data_valid = Signal(bool(0))
        self.stop_source = Signal(bool(0))

class outputs_frontend_new(object):

    """Output signals of the frontend part"""

    def __init__(self, precision_factor=10):
        self.out_precision = precision_factor
        self.out_range = 2**precision_factor
        self.data_valid = Signal(bool(0))
        self.data_out = Signal(intbv(0, min=-self.out_range, max=self.out_range))

class RGB(object):

    """Red, Green, Blue Signals with nbits bitwidth for RGB input"""

    def __init__(self, nbits=8):
        """member variables initialize"""
        self.nbits = nbits
        self.red = Signal(intbv(0)[nbits:])
        self.green = Signal(intbv(0)[nbits:])
        self.blue = Signal(intbv(0)[nbits:])
        self.data_valid = Signal(bool(0))
        self.color_mode = Signal(intbv(0, min=0, max=3))

class inputs_frontend_new(object):

    """Red, Green, Blue Signals with nbits bitwidth for RGB input"""

    def __init__(self, nbits=8):
        """member variables initialize"""
        self.nbits = nbits
        self.red = Signal(intbv(0)[nbits:])
        self.green = Signal(intbv(0)[nbits:])
        self.blue = Signal(intbv(0)[nbits:])
        self.data_valid = Signal(bool(0))

class YCbCr_v2(object):

    """Data_out Signal. According to color mode the data_out
    could be Y, Cb or Cr for color mode = 0, 1, 2
    """

    def __init__(self, nbits=8):
        self.nbits = nbits
        self.data_out = Signal(intbv(0)[nbits:])
        self.data_valid = Signal(bool(0))

class YCbCr(object):

    """Y, Cb, Cr output signals"""

    def __init__(self, nbits=8):
        self.nbits = nbits
        self.y = Signal(intbv(0)[nbits:])
        self.cb = Signal(intbv(0)[nbits:])
        self.cr = Signal(intbv(0)[nbits:])
        self.data_valid = Signal(bool(0))

class outputs_2d(object):

    """Output interface for the 2D-DCT module. It is used also
    as input/output interface for the zig-zag scan module"""

    def __init__(self, precision_factor=10, N=8):
        """Output signals for the 2D-DCT module"""
        self.out_precision = precision_factor
        self.out_range = 2**precision_factor
        self.N = N
        self.data_valid = Signal(bool(0))
        self.out_sigs =[Signal(intbv(0, min=-self.out_range,
                                     max=self.out_range)) for _ in range(self.N**2)]

class input_interface(object):

    """Input Interface for the 2D-DCT module"""

    def __init__(self, nbits=8):
        """Input signals for the 2D-DCT module"""
        self.nbits = nbits
        self.in_range = 2**nbits
        self.data_in = Signal(intbv(0, min=0, max=self.in_range))
        self.data_valid = Signal(bool(0))


class input_1d_1st_stage(object):

    """ Input interface for the 1st stage 1D-DCT"""

    def __init__(self, nbits=8):
        """Input signals for the 1D-DCT module"""
        self.nbits = nbits
        self.in_range = 2**nbits
        self.data_in = Signal(intbv(0, min=-self.in_range, max=self.in_range))
        self.data_valid = Signal(bool(0))

class output_interface(object):

    """Output interface for the 1D-DCT module"""

    def __init__(self, out_precision=10, N=8):
        """Outputs signals for the 1D-DCT module"""
        self.out_precision = out_precision
        self.N = N
        nrange = 2**out_precision
        self.out_sigs = [Signal(intbv(0, min=-nrange, max=nrange))
                         for _ in range(N)]
        self.data_valid = Signal(bool(0))
