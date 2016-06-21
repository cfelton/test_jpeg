#!/usr/bin/env python
# coding=utf-8

from myhdl import Signal, intbv

class outputs_2d(object):

    def __init__(self, precision_factor=10):
        self.out_precision = precision_factor
        self.out_range = 2**precision_factor
        self.data_valid = Signal(bool(0))
        self._build_output_attributes()

    def _build_output_attributes(self):
        for i in range(8):
            for j in range(8):
                y = 'y{:d}{:d}'.format(i, j)
                self.__dict__[y] = Signal(intbv(0, min=-self.out_range,
                                                max=self.out_range))


class input_interface(object):

    def __init__(self, nbits=8):
        self.nbits = nbits
        self.in_range = 2**nbits
        self.data_in = Signal(intbv(0, min=0, max=self.in_range))
        self.data_valid = Signal(bool(0))

class input_1d_1st_stage(object):

    def __init__(self, nbits=8):
        self.nbits = nbits
        self.in_range = 2**nbits
        self.data_in = Signal(intbv(0, min=-self.in_range, max=self.in_range))
        self.data_valid = Signal(bool(0))

class output_interface(object):

    def __init__(self, out_precision=10):
        self.out_precision = out_precision
        out_range = 2**out_precision
        self.out0 = Signal(intbv(0, min=-out_range, max=out_range))
        self.out1 = Signal(intbv(0, min=-out_range, max=out_range))
        self.out2 = Signal(intbv(0, min=-out_range, max=out_range))
        self.out3 = Signal(intbv(0, min=-out_range, max=out_range))
        self.out4 = Signal(intbv(0, min=-out_range, max=out_range))
        self.out5 = Signal(intbv(0, min=-out_range, max=out_range))
        self.out6 = Signal(intbv(0, min=-out_range, max=out_range))
        self.out7 = Signal(intbv(0, min=-out_range, max=out_range))
        self.data_valid = Signal(bool(0))

class input_1d_2nd_stage(object):

    def __init__(self, precision_factor=10):
        self.nbits = precision_factor
        in_range = 2**(self.nbits)
        self.data_in = Signal(intbv(0, min=-in_range, max=in_range))
        self.data_valid = Signal(bool(0))

