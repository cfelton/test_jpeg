"""This module contains the HDL for
    divider used for Quantiser"""

from myhdl import always_seq, block, intbv, always_comb, Signal
from jpegenc.subblocks.quantizer.romr import romr


def divider_ref(dividend, divisor):
    """software implementation of divider"""

    rom_size = 2**8
    rom = [0 for _ in range(rom_size)]
    rom = [0] + [int(round(((2**16)-1)/float(ii)))
                 for ii in range(1, rom_size)]
    rom = tuple(rom)

    divisor_reciprocal = rom[divisor]

    if dividend < 0:
        dividend_d1 = -dividend
    else:
        dividend_d1 = dividend

    mult = (dividend_d1 * divisor_reciprocal)
    mult_s = mult/(2**16)

    if dividend < 0:
        mult_s = -mult_s

    round_ = int((mult/(2**15)) % 2)

    if round_ == 1:
        if dividend >= 0:
            mult_s = mult_s + 1
        else:
            mult_s = int(mult_s - 1)

    return int(mult_s)


@block
def divider(clock, reset, dividend, divisor, quotient):
    """This module contains the HDL implementation"""

    # constants for length of divisor, dividend and reciprocal
    divisor_len = len(divisor)
    dividend_len = len(dividend)
    reciprocal_len = 16

    # rom signals used to get reciprocal
    romr_address = Signal(intbv(0)[divisor_len:])
    romr_data_out = Signal(intbv(0)[reciprocal_len:])

    # temporary signals for dividend and reciprocal
    dividend_temp = Signal(intbv(0)[dividend_len:].signed())
    dividend_temp_d1 = Signal(intbv(0)[dividend_len:])
    reciprocal = Signal(intbv(0)[reciprocal_len:])

    # temporary signals for multiplication
    mult_out = Signal(intbv(0)[(reciprocal_len + dividend_len):])
    mult_out_s = Signal(intbv(0)[dividend_len:].signed())

    # signbit signals
    signbit = Signal(bool(0))
    signbit_d1 = Signal(bool(0))
    signbit_d2 = Signal(bool(0))
    signbit_d3 = Signal(bool(0))

    # signal used for rounding the multiplier output
    round_ = Signal(bool(0))

    # instantiation of rom used for getting reciprocals
    inst_romr = romr(romr_address, clock, romr_data_out)

    @always_comb
    def assign1():
        """assignments for divisor, reciprocal and dividend"""
        romr_address.next = divisor
        reciprocal.next = romr_data_out
        dividend_temp.next = dividend.signed()

    @always_comb
    def assign2():
        """assigning signbit"""
        signbit.next = dividend_temp[11]

    @always_seq(clock.posedge, reset=reset)
    def rdiv():
        """part of the module that does the division"""
        signbit_d1.next = signbit
        signbit_d2.next = signbit_d1
        signbit_d3.next = signbit_d2

        # if signbit is 1 store the sign
        if signbit:
            dividend_temp_d1.next = -dividend_temp
        else:
            dividend_temp_d1.next = dividend_temp

        # multiply dividend with reciprocal of divisor
        mult_out.next = reciprocal*dividend_temp_d1

        # assigning output from the multiplied value
        if not signbit_d2:
            mult_out_s.next = mult_out[(
                reciprocal_len + dividend_len):(reciprocal_len)]

        else:
            mult_out_s.next = -mult_out[(
                reciprocal_len + dividend_len):(reciprocal_len)]

        # getting the round bit
        round_.next = mult_out[reciprocal_len - 1]

        # rounding the output depending upon round bit
        if not signbit_d3:
            if round_:
                quotient.next = mult_out_s + 1

            else:
                quotient.next = mult_out_s

        else:
            if round_:
                quotient.next = mult_out_s - 1
            else:
                quotient.next = mult_out_s

    return inst_romr, assign1, assign2, rdiv
