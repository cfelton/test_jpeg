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

def divider_ref(dividend, divisor):
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

    round_ = int((mult/(2**15))%2)

    if round_ == 1:
        if dividend >= 0:
            mult_s = mult_s + 1
        else:
            mult_s = int(mult_s - 1)

    return int(mult_s)
