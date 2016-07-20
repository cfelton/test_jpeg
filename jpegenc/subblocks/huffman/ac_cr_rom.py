"""The above module is a Luminance Rom
    for AC component for huffman module"""

from myhdl import always_seq, block, Signal, ResetSignal
from myhdl import intbv, always_comb, concat
from myhdl.conversion import analyze


@block
def ac_cr_rom(clock, reset, runlength, vli_size, vlc_ac_size, vlc_ac):
    """HDL implementation of Chrominance AC ROM"""

    width_runlength = len(runlength)
    width_size = len(vli_size)

    rom_addr = Signal(intbv(0)[(width_runlength+width_size):])

    @always_comb
    def assign1():
        """assign rom address"""

        rom_addr.next = concat(runlength, vli_size)

    @always_seq(clock.posedge, reset=reset)
    def assign():
        """storing variable length coded data in rom"""
        if runlength == 0:

            if vli_size == 0x0:
                vlc_ac_size.next = 4
                vlc_ac.next = 0b1010

            elif vli_size == 0x1:
                vlc_ac_size.next = 2
                vlc_ac.next = 0b00

            elif vli_size == 0x2:
                vlc_ac_size.next = 2
                vlc_ac.next = 0b01

            elif vli_size == 0x3:
                vlc_ac_size.next = 3
                vlc_ac.next = 0b100

            elif vli_size == 0x4:
                vlc_ac_size.next = 4
                vlc_ac.next = 0b1011

            elif vli_size == 0x5:
                vlc_ac_size.next = 5
                vlc_ac.next = 0b11010

            elif vli_size == 0x6:
                vlc_ac_size.next = 7
                vlc_ac.next = 0b1111000

            elif vli_size == 0x7:
                vlc_ac_size.next = 8
                vlc_ac.next = 0b11111000

            elif vli_size == 0x8:
                vlc_ac_size.next = 10
                vlc_ac.next = 0b1111110110

            elif vli_size == 0x9:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110000010

            elif vli_size == 0xA:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110000011

            else:
                vlc_ac_size.next = 0
                vlc_ac.next = 0b0

        elif runlength == 0x1:

            if vli_size == 0x1:
                vlc_ac_size.next = 4
                vlc_ac.next = 0b1100

            elif vli_size == 0x2:
                vlc_ac_size.next = 5
                vlc_ac.next = 0b11011

            elif vli_size == 0x3:
                vlc_ac_size.next = 7
                vlc_ac.next = 0b1111001

            elif vli_size == 0x4:
                vlc_ac_size.next = 9
                vlc_ac.next = 0b111110110

            elif vli_size == 0x5:
                vlc_ac_size.next = 11
                vlc_ac.next = 0b11111110110

            elif vli_size == 0x6:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110000100

            elif vli_size == 0x7:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110000101

            elif vli_size == 0x8:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110000110

            elif vli_size == 0x9:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110000111

            elif vli_size == 0xA:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110001000

            else:
                vlc_ac_size.next = 0
                vlc_ac.next = 0b0

        elif runlength == 0x2:

            if vli_size == 0x1:
                vlc_ac_size.next = 5
                vlc_ac.next = 0b11100

            elif vli_size == 0x2:
                vlc_ac_size.next = 8
                vlc_ac.next = 0b11111001

            elif vli_size == 0x3:
                vlc_ac_size.next = 10
                vlc_ac.next = 0b1111110111

            elif vli_size == 0x4:
                vlc_ac_size.next = 12
                vlc_ac.next = 0b111111110100

            elif vli_size == 0x5:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110001001

            elif vli_size == 0x6:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110001010

            elif vli_size == 0x7:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110001011

            elif vli_size == 0x8:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110001100

            elif vli_size == 0x9:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110001101

            elif vli_size == 0xA:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110001110

            else:
                vlc_ac_size.next = 0
                vlc_ac.next = 0b0

        elif runlength == 0x3:

            if vli_size == 0x1:
                vlc_ac_size.next = 6
                vlc_ac.next = 0b111010

            elif vli_size == 0x2:
                vlc_ac_size.next = 9
                vlc_ac.next = 0b111110111

            elif vli_size == 0x3:
                vlc_ac_size.next = 12
                vlc_ac.next = 0b111111110101

            elif vli_size == 0x4:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110001111

            elif vli_size == 0x5:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110010000

            elif vli_size == 0x6:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110010001

            elif vli_size == 0x7:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110010010

            elif vli_size == 0x8:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110010011

            elif vli_size == 0x9:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110010100

            elif vli_size == 0xA:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110010101

            else:
                vlc_ac_size.next = 0
                vlc_ac.next = 0b0

        elif runlength == 0x4:

            if vli_size == 0x1:
                vlc_ac_size.next = 6
                vlc_ac.next = 0b111011

            elif vli_size == 0x2:
                vlc_ac_size.next = 10
                vlc_ac.next = 0b1111111000

            elif vli_size == 0x3:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110010110

            elif vli_size == 0x4:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110010111

            elif vli_size == 0x5:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110011000

            elif vli_size == 0x6:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110011001

            elif vli_size == 0x7:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110011010

            elif vli_size == 0x8:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110011011

            elif vli_size == 0x9:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110011100

            elif vli_size == 0xA:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110011101

            else:
                vlc_ac_size.next = 0
                vlc_ac.next = 0b0

        elif runlength == 0x5:

            if vli_size == 0x1:
                vlc_ac_size.next = 7
                vlc_ac.next = 0b1111010

            elif vli_size == 0x2:
                vlc_ac_size.next = 11
                vlc_ac.next = 0b11111110111

            elif vli_size == 0x3:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110011110

            elif vli_size == 0x4:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110011111

            elif vli_size == 0x5:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110100000

            elif vli_size == 0x6:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110100001

            elif vli_size == 0x7:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110100010

            elif vli_size == 0x8:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110100011

            elif vli_size == 0x9:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110100100

            elif vli_size == 0xA:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110100101

            else:
                vlc_ac_size.next = 0
                vlc_ac.next = 0b0

        elif runlength == 0x6:

            if vli_size == 0x1:
                vlc_ac_size.next = 7
                vlc_ac.next = 0b1111011

            elif vli_size == 0x2:
                vlc_ac_size.next = 12
                vlc_ac.next = 0b111111110110

            elif vli_size == 0x3:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110100110

            elif vli_size == 0x4:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110100111

            elif vli_size == 0x5:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110101000

            elif vli_size == 0x6:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110101001

            elif vli_size == 0x7:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110101010

            elif vli_size == 0x8:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110101011

            elif vli_size == 0x9:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110101100

            elif vli_size == 0xA:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110101101

            else:
                vlc_ac_size.next = 0
                vlc_ac.next = 0b0

        elif runlength == 0x7:

            if vli_size == 0x1:
                vlc_ac_size.next = 8
                vlc_ac.next = 0b11111010

            elif vli_size == 0x2:
                vlc_ac_size.next = 12
                vlc_ac.next = 0b111111110111

            elif vli_size == 0x3:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110101110

            elif vli_size == 0x4:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110101111

            elif vli_size == 0x5:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110110000

            elif vli_size == 0x6:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110110001

            elif vli_size == 0x7:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110110010

            elif vli_size == 0x8:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110110011

            elif vli_size == 0x9:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110110100

            elif vli_size == 0xA:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110110101

            else:
                vlc_ac_size.next = 0
                vlc_ac.next = 0b0

        elif runlength == 0x8:

            if vli_size == 0x1:
                vlc_ac_size.next = 9
                vlc_ac.next = 0b111111000

            elif vli_size == 0x2:
                vlc_ac_size.next = 15
                vlc_ac.next = 0b111111111000000

            elif vli_size == 0x3:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110110110

            elif vli_size == 0x4:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110110111

            elif vli_size == 0x5:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110111000

            elif vli_size == 0x6:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110111001

            elif vli_size == 0x7:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110111010

            elif vli_size == 0x8:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110111011

            elif vli_size == 0x9:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110111100

            elif vli_size == 0xA:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110111101

            else:
                vlc_ac_size.next = 0
                vlc_ac.next = 0b0

        elif runlength == 0x9:

            if vli_size == 0x1:
                vlc_ac_size.next = 9
                vlc_ac.next = 0b111111001

            elif vli_size == 0x2:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110111110

            elif vli_size == 0x3:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111110111111

            elif vli_size == 0x4:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111000000

            elif vli_size == 0x5:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111000001

            elif vli_size == 0x6:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111000010

            elif vli_size == 0x7:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111000011

            elif vli_size == 0x8:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111000100

            elif vli_size == 0x9:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111000101

            elif vli_size == 0xA:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111000110

            else:
                vlc_ac_size.next = 0
                vlc_ac.next = 0b0

        elif runlength == 0xA:

            if vli_size == 0x1:
                vlc_ac_size.next = 9
                vlc_ac.next = 0b111111010

            elif vli_size == 0x2:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111000111

            elif vli_size == 0x3:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111001000

            elif vli_size == 0x4:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111001001

            elif vli_size == 0x5:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111001010

            elif vli_size == 0x6:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111001011

            elif vli_size == 0x7:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111001100

            elif vli_size == 0x8:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111001101

            elif vli_size == 0x9:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111001110

            elif vli_size == 0xA:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111001111

            else:
                vlc_ac_size.next = 0
                vlc_ac.next = 0b0

        elif runlength == 0xB:

            if vli_size == 0x1:
                vlc_ac_size.next = 10
                vlc_ac.next = 0b1111111001

            elif vli_size == 0x2:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111010000

            elif vli_size == 0x3:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111010001

            elif vli_size == 0x4:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111010010

            elif vli_size == 0x5:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111010011

            elif vli_size == 0x6:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111010100

            elif vli_size == 0x7:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111010101

            elif vli_size == 0x8:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111010110

            elif vli_size == 0x9:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111010111

            elif vli_size == 0xA:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111011000

            else:
                vlc_ac_size.next = 0
                vlc_ac.next = 0b0

        elif runlength == 0xC:

            if vli_size == 0x1:
                vlc_ac_size.next = 10
                vlc_ac.next = 0b1111111010

            elif vli_size == 0x2:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111011001

            elif vli_size == 0x3:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111011010

            elif vli_size == 0x4:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111011011

            elif vli_size == 0x5:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111011100

            elif vli_size == 0x6:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111011101

            elif vli_size == 0x7:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111011110

            elif vli_size == 0x8:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111011111

            elif vli_size == 0x9:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111100000

            elif vli_size == 0xA:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111100001

            else:
                vlc_ac_size.next = 0
                vlc_ac.next = 0b0

        elif runlength == 0xD:

            if vli_size == 0x1:
                vlc_ac_size.next = 11
                vlc_ac.next = 0b11111111000

            elif vli_size == 0x2:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111100010

            elif vli_size == 0x3:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111100011

            elif vli_size == 0x4:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111100100

            elif vli_size == 0x5:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111100101

            elif vli_size == 0x6:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111100110

            elif vli_size == 0x7:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111100111

            elif vli_size == 0x8:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111101000

            elif vli_size == 0x9:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111101001

            elif vli_size == 0xA:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111101010

            else:
                vlc_ac_size.next = 0
                vlc_ac.next = 0b0

        elif runlength == 0xE:

            if vli_size == 0x1:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111101011

            elif vli_size == 0x2:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111101100

            elif vli_size == 0x3:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111101101

            elif vli_size == 0x4:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111101110

            elif vli_size == 0x5:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111101111

            elif vli_size == 0x6:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111110000

            elif vli_size == 0x7:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111110001

            elif vli_size == 0x8:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111110010

            elif vli_size == 0x9:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111110011

            elif vli_size == 0xA:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111110100

            else:
                vlc_ac_size.next = 0
                vlc_ac.next = 0b0

        elif runlength == 0xF:

            if vli_size == 0x0:
                vlc_ac_size.next = 11
                vlc_ac.next = 0b11111111001

            elif vli_size == 0x1:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111110101

            elif vli_size == 0x2:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111110110

            elif vli_size == 0x3:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111110111

            elif vli_size == 0x4:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111111000

            elif vli_size == 0x5:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111111001

            elif vli_size == 0x6:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111111010

            elif vli_size == 0x7:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111111011

            elif vli_size == 0x8:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111111100

            elif vli_size == 0x9:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111111101

            elif vli_size == 0xA:
                vlc_ac_size.next = 16
                vlc_ac.next = 0b1111111111111110

            else:
                vlc_ac_size.next = 0
                vlc_ac.next = 0b0

        else:
            vlc_ac_size.next = 0
            vlc_ac.next = 0

    return assign1, assign
