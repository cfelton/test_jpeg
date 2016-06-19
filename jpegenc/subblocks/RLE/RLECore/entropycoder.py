""" This module takes a input and returns amplitude of the input
    and number of bits required to store the input """

from myhdl import always_seq, block
from myhdl import intbv, ResetSignal, Signal
from myhdl.conversion import analyze


def two2bin(num):
    """ converts negative number to positive """
    inum = ~ num
    return inum + 1


def nbits(num, WIDTH):
    """ returns the number of bits required to store num """
    i = WIDTH - 1
    while i >= 0:
        if num[i] == 1:
            return i + 1
        i = i - 1
    return num[WIDTH]


@block
def entropycoder(WIDTH, clock, reset, data_in, size, amplitude):

    """ returns the amplitude of input and number of bits
        required to store the input """

    @always_seq(clock.posedge, reset=reset)
    def logic():
        """ sequential block that finds amplitude and num of bits"""
        if data_in[WIDTH] == 0:
            amplitude.next = data_in
            size.next = nbits(data_in, WIDTH)

        else:
            amplitude.next = data_in - 1
            absval = intbv(0)[(WIDTH):0]
            absval[:] = two2bin(data_in)
            size.next = nbits(absval, WIDTH)

    return logic
