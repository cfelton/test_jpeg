"""The above module is a Luminance Rom
   for DC component for huffman module"""

from myhdl import always_seq, block


@block
def dc_cr_rom(clock, reset, vli_size, vlc_dc_size, vlc_dc):
    """HDL implementation of Chrominance DC ROM"""

    @always_seq(clock.posedge, reset=reset)
    def assign():
        """storing variable length coded data in rom"""

        # variable length integer number is the address for rom
        if vli_size == 0x0:
            vlc_dc_size.next = 0x2
            vlc_dc.next = 0b00

        elif vli_size == 0x1:
            vlc_dc_size.next = 0x2
            vlc_dc.next = 0b01

        elif vli_size == 0x2:
            vlc_dc_size.next = 0x2
            vlc_dc.next = 0b10

        elif vli_size == 0x3:
            vlc_dc_size.next = 0x3
            vlc_dc.next = 0b110

        elif vli_size == 0x4:
            vlc_dc_size.next = 0x4
            vlc_dc.next = 0b1110

        elif vli_size == 0x5:
            vlc_dc_size.next = 0x5
            vlc_dc.next = 0b11110

        elif vli_size == 0x6:
            vlc_dc_size.next = 0x6
            vlc_dc.next = 0b111110

        elif vli_size == 0x7:
            vlc_dc_size.next = 0x7
            vlc_dc.next = 0b1111110

        elif vli_size == 0x8:
            vlc_dc_size.next = 0x8
            vlc_dc.next = 0b11111110

        elif vli_size == 0x9:
            vlc_dc_size.next = 0x9
            vlc_dc.next = 0b111111110

        elif vli_size == 0xA:
            vlc_dc_size.next = 0xA
            vlc_dc.next = 0b1111111110

        elif vli_size == 0xB:
            vlc_dc_size.next = 0xB
            vlc_dc.next = 0b11111111110

        else:
            vlc_dc_size.next = 0x0
            vlc_dc.next = 0b0

    return assign
