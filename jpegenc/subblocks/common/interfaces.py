#!/usr/bin/env python
# coding=utf-8

from myhdl import Signal, intbv, block, always_comb

class inputs_frontend(object):

    """Inputs of the frontend part of the decoder"""

    def __init__(self):
        self.data_in = Signal(intbv(0)[24:])
        self.data_valid = Signal(bool(0))

class outputs_frontend(object):

    def __init__(self, precision_factor=10, N=8):
        self.out_precision = precision_factor
        self.out_range = 2**precision_factor
        self.N = N
        self.data_valid = Signal(bool(0))
        self.y_dct_out = [Signal(intbv(0, min=-self.out_range,
                                       max=self.out_range)) for _ in range(self.N**2)]
        self.cb_dct_out = [Signal(intbv(0, min=-self.out_range,
                                        max=self.out_range)) for _ in range(self.N**2)]
        self.cr_dct_out = [Signal(intbv(0, min=-self.out_range,
                                        max=self.out_range)) for _ in range(self.N**2)]

class outputs_frontend_new(object):

    def __init__(self, precision_factor=10):
        self.out_precision = precision_factor
        self.out_range = 2**precision_factor
        self.data_valid = Signal(bool(0))
        self.end_of_block_conversion = Signal(bool(0))
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


class YCbCr(object):

    """Y, Cb, Cr output signals"""

    def __init__(self, nbits=8):
        self.nbits = nbits
        self.y = Signal(intbv(0)[nbits:])
        self.cb = Signal(intbv(0)[nbits:])
        self.cr = Signal(intbv(0)[nbits:])
        self.data_valid = Signal(bool(0))

@block
def assign(a, b):

    @always_comb
    def assign():
            a.next = b

    return assign


@block
def assign_array(a, b):

    assert isinstance(a, list)
    assert isinstance(b, list)
    assert len(a) == len(b)


    g = []
    for i in range(len(a)):
        g += [assign(a[i], b[i])]
    return g


class outputs_2d(object):

    """Output interface for the 2D-DCT module"""

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


class input_1d_2nd_stage(object):

    """Input interface for the 2nd 1D-DCT module"""

    def __init__(self, precision_factor=10):
        """Input signals for the 2nd 1D-DCT module"""
        self.nbits = precision_factor
        in_range = 2**(self.nbits)
        self.data_in = Signal(intbv(0, min=-in_range, max=in_range))
        self.data_valid = Signal(bool(0))


