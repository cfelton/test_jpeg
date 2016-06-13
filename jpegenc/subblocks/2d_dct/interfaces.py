#!/usr/bin/env python
# coding=utf-8

from myhdl import Signal, intbv

class outputs_2d(object):

    def __init__(self, precision_factor=10):
        self.out_precision = precision_factor
        out_range = 2**precision_factor
        self.y00 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y01 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y02 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y03 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y04 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y05 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y06 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y07 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y10 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y11 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y12 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y13 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y14 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y15 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y16 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y17 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y20 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y21 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y22 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y23 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y24 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y25 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y26 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y27 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y30 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y31 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y32 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y33 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y34 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y35 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y36 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y37 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y40 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y41 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y42 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y43 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y44 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y45 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y46 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y47 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y50 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y51 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y52 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y53 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y54 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y55 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y56 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y57 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y60 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y61 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y62 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y63 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y64 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y65 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y66 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y67 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y70 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y71 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y72 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y73 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y74 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y75 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y76 = Signal(intbv(0, min=-out_range, max=out_range))
        self.y77 = Signal(intbv(0, min=-out_range, max=out_range))
        self.data_valid = Signal(bool(0))

class input_interface(object):

    def __init__(self, nbits=8):
        self.nbits = nbits
        in_range = 2**nbits
        self.data_in = Signal(intbv(0, min=0, max=in_range))
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

