"""MyHDL implementation of Chrominance DC ROM"""

from myhdl import Signal, always
from myhdl import block, always_comb
from .tablebuilder import build_huffman_rom_tables


@block
def dc_cr_rom(clock, address, data_out_size, data_out_code):
    """Build Chrominance ROM for Huffman Tables"""

    code, size = build_huffman_rom_tables(
        '../jpegenc/subblocks/huffman/dc_cr_rom.csv')

    rom_code_size = len(code)
    rom_code = [0 for _ in range(rom_code_size)]
    rom_code = [int(code[0], 2)] + [int(
        code[ii+1], 2) for ii in range(rom_code_size-1)]

    rom_code = tuple(rom_code)

    rom_depth = len(size)
    rom_size = [0 for _ in range(rom_depth)]
    rom_size = [int(size[0])] + [int(size[ii+1]) for ii in range(rom_depth-1)]
    rom_size = tuple(rom_size)

    raddr = Signal(address.val)

    @always(clock.posedge)
    def beh_addr():
        """assign address to a signal"""
        raddr.next = address

    @always_comb
    def beh_out_code():
        """assign output code"""
        data_out_code.next = rom_code[raddr]

    @always_comb
    def beh_out_size():
        """assign output size"""
        data_out_size.next = rom_size[raddr]

    return beh_addr, beh_out_code, beh_out_size
