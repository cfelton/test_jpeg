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

    @block
    def assignment_1(self, array):

        # avoid verilog indexing
        @block
        def assign(y, x):
            @always_comb
            def assign():
                y.next = x
            return assign

        g = [None for _ in range(self.N**2)]
        for i in range(self.N**2):
            g[i] = assign(self.out_sigs[i], array[i])
        return g


    @block
    def assignment_2(self, array):

        # avoid verilog indexing
        @block
        def assign(y, x):
            @always_comb
            def assign():
                y.next = x
            return assign

        g = [None for _ in range(self.N**2)]
        for i in range(self.N**2):
            g[i] = assign(array[i], self.out_sigs[i])
        return g


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

    @block
    def assignment(self, array):

        # avoid verilog indexing
        @block
        def assign(y, x):
            @always_comb
            def assign():
                y.next = x
            return assign

        g = [None for _ in range(self.N)]
        for i in range(self.N):
            g[i] = assign(self.out_sigs[i], array[i])
        return g

    @block
    def assignment_2(self, array):

        # avoid verilog indexing
        @block
        def assign(y, x):
            @always_comb
            def assign():
                y.next = x
            return assign

        g = [None for _ in range(self.N)]
        for i in range(self.N):
            g[i] = assign(array[i], self.out_sigs[i])
        return g

class input_1d_2nd_stage(object):

    """Input interface for the 2nd 1D-DCT module"""

    def __init__(self, precision_factor=10):
        """Input signals for the 2nd 1D-DCT module"""
        self.nbits = precision_factor
        in_range = 2**(self.nbits)
        self.data_in = Signal(intbv(0, min=-in_range, max=in_range))
        self.data_valid = Signal(bool(0))

    @block
    def assignment(self, data_in, data_valid):

        # avoid verilog indexing
        @block
        def assign(y1, x1, y2, x2):
            @always_comb
            def assign():
                y1.next = x1
                y2.next = x2
            return assign

        g = [assign(self.data_in, data_in, self.data_valid, data_valid)]
        return g
