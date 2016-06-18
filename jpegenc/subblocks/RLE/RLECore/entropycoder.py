""" This module takes a input and returns amplitude of the input
    and number of bits required to store the input """

from myhdl import always_seq, block
from myhdl import intbv, ResetSignal, Signal
from myhdl.conversion import analyze

WIDTH_REG = 12
SIZE = 4


def two2bin(num):
    """ converts negative number to positive """
    inum = ~ num
    return inum + 1


def nbits(num):
    """ returns the number of bits required to store num """
    i = WIDTH_REG - 1
    while i >= 0:
        if num[i] == 1:
            return i + 1
        i = i - 1
    return num[WIDTH_REG]


@block
def entropycoder(clock, reset, input_value, size, amplitude):
    """ returns the amplitude of input and number of bits
        required to store the input """

    @always_seq(clock.posedge, reset=reset)
    def logic():
        """ sequential block that finds amplitude and num of bits"""
        if input_value[WIDTH_REG] == 0:
            amplitude.next = input_value
            size.next = nbits(input_value)

        else:
            amplitude.next = input_value - 1
            absval = intbv(0)[(WIDTH_REG):0]
            absval[:] = two2bin(input_value)
            size.next = nbits(absval)

    return logic
