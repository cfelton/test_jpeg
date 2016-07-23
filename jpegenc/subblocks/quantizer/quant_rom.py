"""MyHDL implementation of Quantiser ROM"""

import csv
from myhdl import Signal, always
from myhdl import block, always_comb


def build_huffman_rom_tables(csvfile):
    """build huffman tables"""
    tables_quant = []
    with open(csvfile, 'r') as csvfp:
        csvreader = csv.reader(csvfp, delimiter=',')
        for row in csvreader:
            tables_quant.append(row[0])
    tables_quant = tuple(tables_quant)
    return tables_quant


@block
def quant_rom(clock, address, data_out):
    """Build Chrominance ROM for Huffman Tables"""

    tables = build_huffman_rom_tables(
        '../jpegenc/subblocks/quantizer/quant_tables.csv')

    tables_len = len(tables)
    rom_tables = [0 for _ in range(tables_len)]
    rom_tables = [int(tables[0])] + [int(
        tables[ii+1]) for ii in range(tables_len-1)]

    rom_tables = tuple(rom_tables)

    raddr = Signal(address.val)

    @always(clock.posedge)
    def beh_addr():
        """assign address to a signal"""
        raddr.next = address

    @always_comb
    def beh_out():
        """assign output code"""
        data_out.next = rom_tables[raddr]

    return beh_addr, beh_out
