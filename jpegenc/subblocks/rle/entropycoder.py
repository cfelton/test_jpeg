"""
This module takes a input and returns amplitude of the input and
number of bits required to store the input
"""

from myhdl import always_seq, block, intbv


def two2bin(num):
    """converts negative number to positive"""
    inum = ~ num
    return inum + 1


def nbits(num, width):
    """returns the number of bits required to store num"""
    i = width - 1
    while i >= 0:
        if num[i] == 1:
            return i + 1
        i = i - 1
    return num[width]


def entropy_encode(amplitude):
    """ Model of the entropy encoding

    Arguments:
        amplitude (int): given an integer generate the encoding

    Returns:
        amplitude_ref:
        size_ref:
    """
    if amplitude >= 0:
        amplitude_ref = amplitude
        size_ref = amplitude.bit_length()
    else:
        amplitude_ref = amplitude - 1
        size_ref = abs(amplitude).bit_length()

    return amplitude_ref, size_ref


@block
def entropycoder(width, clock, reset, data_in, size, amplitude):
    """returns the amplitude of input and number of bits required to store the input
    """

    @always_seq(clock.posedge, reset=reset)
    def logic():
        """sequential block that finds amplitude and num of bits"""
        if data_in[width] == 0:
            amplitude.next = data_in
            size.next = nbits(data_in, width)

        else:
            amplitude.next = data_in - 1
            absval = intbv(0)[(width):0]
            absval[:] = two2bin(data_in)
            size.next = nbits(absval, width)

    return logic
