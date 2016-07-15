"""
This module takes a input and returns amplitude of the
input and number of bits required to store the input.

"""

from myhdl import always_seq, block, intbv


def two2bin(num):
    """converts negative number to positive"""

    inum = ~ num
    return inum + 1


def bit_length(num, maxlen=32):
    """
    Determine the number of bits required to represent a value
    This functions provides the same functionality as the Python
    int.bit_length() function but is convertible.

    This function generates the combinatorial logic to determine the maximum
    number of bits required to represent an unsigned value.

    Currently the function computes a maximum of maxlen bits.

    for values larger than 2**maxlen this function will fail.
    myhdl convertible

    """

    assert num >= 0 and num < 2**maxlen
    val = int(num)

    nbits = 0

    for bit in range(maxlen):
        if val == 0:
            nbits = bit
            break
        val = val >> 1

    return nbits


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
def entropycoder(clock, reset, data_in, size, amplitude):
    """
    This module return the amplitude and
    number of bits required to store input

    io ports:

    data_in : input data into the entropy coder

    size : number of bits required to store amplitude
    amplitude : amplitude of the input

    constants:

    width_data : width of the input data

    """

    # width of the input data
    width_data = len(data_in)

    @always_seq(clock.posedge, reset=reset)
    def logic():
        """sequential block that finds amplitude and num of bits"""

        # encoding of positive numbers

        # if MSB is logical low number is positive
        if data_in[(width_data-1)] == 0:

            # amplitude of the positive number(input)
            amplitude.next = data_in

            # number of bits required to store input
            size.next = bit_length(data_in, maxlen=width_data)

        # encoding of negative number
        else:

            # amplitude of the negative number(input)
            amplitude.next = data_in - 1
            absval = intbv(0)[(width_data-1):0]

            # convert negative number to positive
            absval[:] = two2bin(data_in)

            # number of bits required to store input
            size.next = bit_length(absval, maxlen=width_data)

    return logic
