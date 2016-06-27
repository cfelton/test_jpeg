def numofbits(amplitude):
    count = 0
    while amplitude != 0:
        amplitude = int(amplitude/2)
        count = count + 1
    return int(count)


def entropy_encode(amplitude):

    """ Expected outputs are generated from here """
    if amplitude >= 0:
        amplitude_ref = amplitude
        size_ref = numofbits(amplitude)
    else:
        amplitude_ref = amplitude - 1
        size_ref = numofbits(abs(amplitude))

    return amplitude_ref, size_ref
