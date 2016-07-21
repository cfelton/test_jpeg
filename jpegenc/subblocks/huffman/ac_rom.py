import csv
import myhdl
from myhdl import Signal, always, always_comb, block, intbv, concat


def build_huffman_rom_tables(csvfile):
    code = []
    size = []
    with open(csvfile, 'r') as csvfp:
        csvreader = csv.reader(csvfp, delimiter=',', quotechar="'" )
        for row in csvreader:
            code.append(row[0])
            size.append(row[1])
    code = tuple(code)
    size = tuple(size)
    return code, size

@block
def ac_rom(clock, address1, address2, data_out_size, data_out_code):
    code, size = build_huffman_rom_tables('../jpegenc/subblocks/huffman/ac_rom.csv')
    
    rom_code_size = len(code)
    rom_code = [0 for _ in range(rom_code_size)]
    rom_code = [int(code[0], 2)] + [int(code[ii+1], 2) for ii in range(rom_code_size-1)]
    rom_code = tuple(rom_code)

    rom_depth = len(size)
    rom_size = [0 for _ in range(rom_depth)]
    rom_size = [int(size[0])] + [int(size[ii+1]) for ii in range(rom_depth-1)]
    rom_size = tuple(rom_size)
    address = Signal(intbv(0)[len(address1)+len(address2):])
    raddr = Signal(intbv(0)[len(address1)+len(address2):])
    @always_comb
    def assign1():
        """assign rom address"""
        address.next = concat(address1, address2)

    @always(clock.posedge)
    def beh_addr():
        raddr.next = address

    @always_comb
    def beh_out_code():
        data_out_code.next = rom_code[raddr]

    @always_comb
    def beh_out_size():
        data_out_size.next = rom_size[raddr]

    return assign1, beh_addr, beh_out_code, beh_out_size

def convert():

    clock = Signal(bool(0))

    address1 = Signal(intbv(0)[4:])
    address2 = Signal(intbv(0)[4:])
    data_out_size = Signal(intbv(0)[8:])
    data_out_code = Signal(intbv(0)[8:])

    inst = ac_rom(address1, address2, clock, data_out_size, data_out_code)
    inst.convert(hdl='Verilog')


if __name__ == '__main__':
    convert()
