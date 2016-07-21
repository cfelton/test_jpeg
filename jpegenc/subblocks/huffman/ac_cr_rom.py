"""MyHDL implementation of AC Chrominance ROM"""

from myhdl import Signal, always, always_comb
from myhdl import block, intbv, concat
from .tablebuilder import build_huffman_rom_tables


@block
def ac_cr_rom(clock, address1, address2, data_out_size, data_out_code):
    """build ac ROM for chrominance"""

    code, size = build_huffman_rom_tables(
        '../jpegenc/subblocks/huffman/ac_cr_rom.csv')

    rom_code_size = len(code)
    rom_code = [0 for _ in range(rom_code_size)]
    rom_code = [int(code[0], 2)] + [int(
        code[ii+1], 2) for ii in range(rom_code_size-1)]

    rom_code = tuple(rom_code)

    rom_depth = len(size)
    rom_size = [0 for _ in range(rom_depth)]
    rom_size = [int(size[0])] + [int(size[ii+1]) for ii in range(rom_depth-1)]
    rom_size = tuple(rom_size)
    address = Signal(intbv(0)[len(address1)+len(address2):])
    raddr = Signal(intbv(0)[len(address1)+len(address2):])

    @always_comb
    def assign1():
        """concat address1 and address2"""
        address.next = concat(address1, address2)

    @always(clock.posedge)
    def beh_addr():
        """assign address to a signal"""
        raddr.next = address

    @always_comb
    def beh_out_code():
        """asssign output code"""
        data_out_code.next = rom_code[raddr]

    @always_comb
    def beh_out_size():
        """assign output size"""
        data_out_size.next = rom_size[raddr]

    return assign1, beh_addr, beh_out_code, beh_out_size
