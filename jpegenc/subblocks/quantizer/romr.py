"""This module generates reciprocals for numbers 0-255"""

import myhdl
from myhdl import Signal, always, always_comb


@myhdl.block
def romr(addr, clk, datao):
    """Reciprocals of numbers are generated for quantizer core"""

    # build the ROM table
    rom_size = 2**len(addr)
    rom = [0 for _ in range(rom_size)]
    rom = [0] + [int(round(((2**16)-1)/float(ii)))
                 for ii in range(1, rom_size)]
    rom = tuple(rom)
    raddr = Signal(addr.val)
    # raddr = Signal(intbv(0)[len(addr):])

    @always(clk.posedge)
    def beh_addr():
        """read rom address"""
        raddr.next = addr

    @always_comb
    def beh_out():
        """write from rom address"""
        datao.next = rom[raddr]

    return beh_addr, beh_out
