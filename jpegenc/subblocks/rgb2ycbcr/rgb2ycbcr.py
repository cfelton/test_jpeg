#!/bin/python
"""Color Space Conversion Module"""

import numpy as np

import myhdl
from myhdl import Signal, ResetSignal, intbv, always_comb, always_seq
from myhdl.conversion import analyze


class ColorSpace(object):

    """
    Color Space Conversion Class
    It is used to derive the integer coefficients
    and as a software reference for the conversion
    """

    def __init__(self, red=0, green=0, blue=0):
        """Instance variables"""
        self.red = red
        self.green = green
        self.blue = blue
        # setup the constant coefficients for YCbCr
        self._set_jfif_coefs()

    def _set_jfif_coefs(self):
        """The YCbCr special constants
        The JFIF YCbCr conversion requires "special" constants defined
        by the standard.  The constants are describe in a Wikipedia page:
        https://en.wikipedia.org/wiki/YCbCr
        """
        self.ycbcr_coef_mat = np.array([
            [0.2999, 0.5870, 0.1140],     # Y coefficients
            [-0.1687, -0.3313, 0.5000],   # Cb coefficients
            [0.5000, -0.4187, -0.0813],   # Cr coefficients
        ])
        self.offset = np.array([0, 128, 128])

    def get_jfif_ycbcr(self):
        """RGB to YCbCr Conversion"""
        rgb = np.array([self.red, self.green, self.blue])
        rgb = rgb[np.newaxis, :].transpose()
        offset = self.offset[np.newaxis, :].transpose()
        cmat = self.ycbcr_coef_mat
        ycbcr = np.dot(cmat, rgb) + offset
        ycbcr = np.rint(ycbcr)
        return ycbcr.astype(int)

    def get_jfif_ycbcr_int_coef(self, precision_factor=0):
        """Generate the integer (fixed-point) coefficients"""
        cmat = self.ycbcr_coef_mat
        cmat_ab = np.absolute(cmat)
        int_coef = cmat_ab * (2**precision_factor)
        int_coef = np.rint(int_coef)
        int_coef = int_coef.astype(int)
        int_offset = np.rint(self.offset * (2**precision_factor))
        int_offset = int_offset.astype(int)
        return int_coef.tolist(), int_offset.tolist()


def build_coeffs(fract_bits):
    """ function which used to build the coefficients """
    def list_of_ints(val, num):
        return [val for _ in range(num)]
    Y, Cb, Cr, Offset = (list_of_ints(0, 3), list_of_ints(0, 3),
                         list_of_ints(0, 3), list_of_ints(0, 3),)
    int_coef, Offset = ColorSpace().get_jfif_ycbcr_int_coef(fract_bits)
    Y = int_coef[0]
    Cb = int_coef[1]
    Cr = int_coef[2]
    return Y, Cb, Cr, Offset


class RGB(object):

    """Red, Green, Blue Signals with nbits bitwidth for RGB input"""

    def __init__(self, nbits=8):
        self.nbits = nbits
        self.red = Signal(intbv(0)[nbits:])
        self.green = Signal(intbv(0)[nbits:])
        self.blue = Signal(intbv(0)[nbits:])
        self.data_valid = Signal(bool(0))


class YCbCr(object):

    """Y, Cb, Cr are the outputs signals of the color space
    conversion module with nbits bitwidth
    """

    def __init__(self, nbits=8):
        self.nbits = nbits
        self.y = Signal(intbv(0)[nbits:])
        self.cb = Signal(intbv(0)[nbits:])
        self.cr = Signal(intbv(0)[nbits:])
        self.data_valid = Signal(bool(0))

    def bitLength(self): return self.nbits


@myhdl.block
def rgb2ycbcr(rgb, ycbcr, clock, reset, num_fractional_bits=14):
    """
    Color Space Conversion module
    This module is used to transform the rgb input
    to an other representation called YCbCr

    Inputs:
        Red, Green, Blue, data_valid
        clock, reset

    Outputs:
        Y, Cb ,Cr, data_valid

    Parameters:
        num_fractional_bits
    """

    fract_bits = num_fractional_bits
    nbits = rgb.nbits
    # the a and b are used for the rounding
    a = fract_bits + nbits
    b = fract_bits

    # build the coefficients
    Y, Cb, Cr, Offset = build_coeffs(fract_bits)

    # Ranges for multiplication and addition signals
    mult_max_range = 2**(nbits + fract_bits + 1)
    rgb_range = 2**nbits
    coeff_range = 2**fract_bits

    # signals for y,cb,cr registers
    Y_reg, Cb_reg, Cr_reg = [[Signal(intbv(0, min=-mult_max_range,
                                           max=mult_max_range)) for _ in range(3)] for _ in range(3)]
    Y_sum, Cb_sum, Cr_sum = [Signal(intbv(0, min=-mult_max_range,
                                          max=mult_max_range)) for _ in range(3)]

    # signals for signed input RGB
    R_s, G_s, B_s = [Signal(intbv(0, min=-rgb_range,
                                  max=rgb_range)) for _ in range(3)]

    # signals for coefficient signed conversion
    Y1_s, Y2_s, Y3_s = [Signal(intbv(Y[i], min=-coeff_range,
                                     max=coeff_range)) for i in range(3)]
    Cb1_s, Cb2_s, Cb3_s = [Signal(intbv(Cb[i], min=-coeff_range,
                                        max=coeff_range)) for i in range(3)]
    Cr1_s, Cr2_s, Cr3_s = [Signal(intbv(Cr[i], min=-coeff_range,
                                        max=coeff_range)) for i in range(3)]
    offset_y, offset_cb, offset_cr = [Signal(intbv(Offset[i], min=-mult_max_range,
                                                   max=mult_max_range)) for i in range(3)]

    data_valid_reg = [Signal(bool(0)) for _ in range(2)]

    @always_comb
    def logic2():
        # input RGB to RGB signed
        R_s.next = rgb.red
        G_s.next = rgb.green
        B_s.next = rgb.blue

    @always_seq(clock.posedge, reset=reset)
    def logic():

        if rgb.data_valid:

            Y_reg[0].next = R_s * Y1_s
            Y_reg[1].next = G_s * Y2_s
            Y_reg[2].next = B_s * Y3_s

            Cb_reg[0].next = R_s * Cb1_s
            Cb_reg[1].next = G_s * Cb2_s
            Cb_reg[2].next = B_s * Cb3_s

            Cr_reg[0].next = R_s * Cr1_s
            Cr_reg[1].next = G_s * Cr2_s
            Cr_reg[2].next = B_s * Cr3_s

            Y_sum.next = Y_reg[0] + Y_reg[1] + Y_reg[2] + offset_y
            Cb_sum.next = - Cb_reg[0] - Cb_reg[1] + Cb_reg[2] + offset_cb
            Cr_sum.next = Cr_reg[0] - Cr_reg[1] - Cr_reg[2] + offset_cr

            # rounding the part from signal[fract_bits + nbits:fract_bits]

            if(Y_sum[b - 1] == 1 and Y_sum[a:b] != (2**nbits)):
                ycbcr.y.next = Y_sum[a:b] + 1
            else:
                ycbcr.y.next = Y_sum[a:b]
            if(Cb_sum[b - 1] == 1 and Cb_sum[a:b] != (2**nbits)):
                ycbcr.cb.next = Cb_sum[a:b] + 1
            else:
                ycbcr.cb.next = Cb_sum[a:b]
            if(Cr_sum[b - 1] == 1 and Cr_sum[a:b] != (2**nbits)):
                ycbcr.cr.next = Cr_sum[a:b] + 1
            else:
                ycbcr.cr.next = Cr_sum[a:b]

            # data_valid delayed for 3 cycles
            data_valid_reg[0].next = rgb.data_valid
            data_valid_reg[1].next = data_valid_reg[0]
            ycbcr.data_valid.next = data_valid_reg[1]

        else:

            ycbcr.data_valid.next = False

    return logic, logic2


def convert():
    """convert rgb2ycbcr module"""
    ycbcr = YCbCr()
    rgb = RGB()

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)

    analyze.simulator = 'ghdl'
    assert rgb2ycbcr(rgb, ycbcr, clock, reset,
                     num_fractional_bits=14).analyze_convert() == 0

if __name__ == '__main__':
    convert()
