#!/bin/python
"""Color Space Conversion Module"""

import numpy as np

import myhdl
from myhdl import Signal, ResetSignal, intbv, always_comb, always_seq
from myhdl.conversion import analyze
from jpegenc.subblocks.common import RGB_v2, YCbCr_v2

class ColorSpace(object):

    """Color Space Conversion Class

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
    """function which used to build the coefficients"""
    def list_of_ints(val, num):
        """create lists"""
        return [val for _ in range(num)]
    Y, Cb, Cr, Offset = (list_of_ints(0, 3), list_of_ints(0, 3),
                         list_of_ints(0, 3), list_of_ints(0, 3),)
    int_coef, Offset = ColorSpace().get_jfif_ycbcr_int_coef(fract_bits)
    Y = int_coef[0]
    Cb = int_coef[1]
    Cr = int_coef[2]
    return tuple(Y), tuple(Cb), tuple(Cr), Offset

@myhdl.block
def rgb2ycbcr_v2(rgb, ycbcr, clock, reset, num_fractional_bits=14):
    """Color Space Conversion module

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

    # make rom from the coeffs
    y_rom, Cb_rom, Cr_rom, Offset = build_coeffs(fract_bits)

    # Ranges for multiplication and addition signals
    mult_max_range = 2**(nbits + fract_bits + 1)
    rgb_range = 2**nbits
    coeff_range = 2**fract_bits

    R_s, G_s, B_s = [Signal(intbv(0, min=-rgb_range,
                                  max=rgb_range)) for _ in range(3)]

    data_valid_reg = [Signal(bool(0)) for _ in range(4)]

    coeffs = [Signal(intbv(0, min=-coeff_range,
                           max=coeff_range)) for i in range(3)]

    mul_reg = [Signal(intbv(0, min=-mult_max_range,
                            max=mult_max_range)) for _ in range(3)]

    mul_reg_1 = [Signal(intbv(0, min=-mult_max_range,
                            max=mult_max_range)) for _ in range(3)]


    first_adder_sum = Signal(intbv(0, min=-mult_max_range, max=mult_max_range))

    second_adder_sum = Signal(intbv(0, min=-mult_max_range, max=mult_max_range))

    third_adder_sum = Signal(intbv(0, min=-mult_max_range, max=mult_max_range))

    offset = [Signal(intbv(Offset[i], min=-mult_max_range,
                           max=mult_max_range)) for i in range(3)]

    color_mode_reg = Signal(intbv(0, min=0, max=3))
    color_mode_reg_1 = Signal(intbv(0, min=0, max=3))

    @always_comb
    def logic2():
        """input RGB to RGB signed"""
        R_s.next = rgb.red
        G_s.next = rgb.green
        B_s.next = rgb.blue

    @always_comb
    def coeff_mux():
        """multiplexer for the coefficients"""
        if rgb.color_mode == 0:
            for i in range(3):
                coeffs[i].next = y_rom[i]
        elif rgb.color_mode == 1:
            for i in range(3):
                coeffs[i].next = Cb_rom[i]
        else:
            for i in range(3):
                coeffs[i].next = Cr_rom[i]

    @always_seq(clock.posedge, reset=reset)
    def mul_reg_sign():
        """multiplexer for the sign of the multiplication"""
        if color_mode_reg == 0:
            mul_reg_1[0].next = mul_reg[0]
            mul_reg_1[1].next = mul_reg[1]
            mul_reg_1[2].next = mul_reg[2]
        elif color_mode_reg == 1:
            mul_reg_1[0].next = - mul_reg[0]
            mul_reg_1[1].next = - mul_reg[1]
            mul_reg_1[2].next = mul_reg[2]
        else:
            mul_reg_1[0].next = mul_reg[0]
            mul_reg_1[1].next = - mul_reg[1]
            mul_reg_1[2].next = - mul_reg[2]



    @always_seq(clock.posedge, reset=reset)
    def logic():
        """Color Space Equation Conversion Implementation"""

        mul_reg[0].next = R_s * coeffs[0]
        mul_reg[1].next = G_s * coeffs[1]
        mul_reg[2].next = B_s * coeffs[2]

        color_mode_reg.next = rgb.color_mode
        color_mode_reg_1.next = color_mode_reg

        first_adder_sum.next = mul_reg_1[0] + mul_reg_1[1]
        second_adder_sum.next = mul_reg_1[2] + offset[color_mode_reg_1]
        third_adder_sum.next = first_adder_sum + second_adder_sum

        # rounding the part from signal[fract_bits + nbits:fract_bits]
        if third_adder_sum[b - 1] == 1 and third_adder_sum[a:b] != (2**nbits):
            ycbcr.data_out.next = third_adder_sum[a:b] + 1
        else:
            ycbcr.data_out.next = third_adder_sum[a:b]

        # data_valid delayed for 4 cycles
        data_valid_reg[0].next = rgb.data_valid
        data_valid_reg[1].next = data_valid_reg[0]
        data_valid_reg[2].next = data_valid_reg[1]
        data_valid_reg[3].next = data_valid_reg[2]

        if rgb.data_valid:
            ycbcr.data_valid.next = data_valid_reg[3]
        else:
            ycbcr.data_valid.next = False

    return logic, logic2, coeff_mux, mul_reg_sign


def convert():
    ycbcr = YCbCr_v2()
    rgb = RGB_v2()

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)
    analyze.simulator = 'ghdl'
    assert rgb2ycbcr_v2(rgb, ycbcr, clock, reset,
                     num_fractional_bits=14).analyze_convert() == 0

