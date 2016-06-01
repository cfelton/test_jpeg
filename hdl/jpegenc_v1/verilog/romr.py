
import myhdl
from myhdl import Signal, intbv, always, always_comb


@myhdl.block
def romr(addr, clk, datao):

    # build the ROM table
    rom_size = 2**len(addr)
    rom = [0 for _ in range(rom_size)]
    rom = [0] + [int(round(((2**16)-1)/float(ii))) 
                 for ii in range(1, rom_size)]
    rom = tuple(rom)
    raddr = Signal(addr)

    @always(clk.posedge)
    def beh_addr():
        raddr.next = addr

    @always_comb
    def beh_out():
        datao.next = rom[raddr]

    return beh_addr, beh_out


def convert():
    clock = Signal(bool(0))
    addr = Signal(intbv(0)[8:])
    datao = Signal(intbv(0)[16:])
    inst = romr(addr, clock, datao)
    inst.convert(hdl='Verilog', name='ROMR',
                 directory='output_files', testbench=False)


if __name__ == '__main__':
    convert()