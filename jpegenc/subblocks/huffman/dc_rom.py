"""MyHDL implementation of DC ROM
   used for Huffman Encoder"""

from myhdl import Signal, always
from myhdl import block, always_comb
from .tablebuilder import build_huffman_rom_tables


@block
def dc_rom(clock, address, data_out_size, data_out_code):
    """build dc rom here"""

    code, size = build_huffman_rom_tables(
        '../jpegenc/subblocks/huffman/dc_rom.csv')

    rom_code_size = len(code)
    rom_code = [0 for _ in range(rom_code_size)]
    rom_code = [int(code[0])] + [int(
        code[ii+1]) for ii in range(rom_code_size-1)]

    rom_code = tuple(rom_code)

    rom_depth = len(size)
    rom_size = [0 for _ in range(rom_depth)]
    rom_size = [int(size[0])] + [int(size[ii+1]) for ii in range(rom_depth-1)]
    rom_size = tuple(rom_size)

    raddr = Signal(address.val)

    @always(clock.posedge)
    def beh_addr():
        """assign adrress value to a signal"""
        raddr.next = address

    @always_comb
    def beh_out_code():
        """read code output"""
        data_out_code.next = rom_code[raddr]

    @always_comb
    def beh_out_size():
        """read size output"""
        data_out_size.next = rom_size[raddr]

    return beh_addr, beh_out_code, beh_out_size
